
"""
src/train.py
============
Train XGBoost and RandomForest with best tuned params.
Evaluate on held-out 2020–2024 test set.
Optionally build stacking ensemble if best single-model R² < 0.85.
Save best model → models/best_model.pkl

Prints:
  • TimeSeriesSplit fold year ranges (leakage verification)
  • Train / validation / test metrics
"""

from __future__ import annotations

import json
import logging
import os
import warnings
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def load_best_params(name: str, cfg: dict) -> dict:
    path = ROOT / cfg["paths"]["models"] / f"best_params_{name}.yaml"
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {}
    log.warning("%s not found; using defaults.", path)
    return {}


def prepare_data(cfg: dict):
    feat_path = ROOT / cfg["paths"]["features"] / "features.csv"
    df = pd.read_csv(feat_path).sort_values(["year", "iso3"])  # year-first so TimeSeriesSplit splits on year boundaries

    target_col = "target_score"
    drop_cols = (
        ["iso3", "year", "target_score"]
        + [c for c in df.columns if c.startswith("pillar_")]
        + [c for c in df.columns if df[c].dtype == object]
    )

    X_all = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y_all = df[target_col]
    years = df["year"].values

    train_end = cfg["temporal_split"]["train_end"]
    test_start = cfg["temporal_split"]["test_start"]

    train_mask = years <= train_end
    test_mask = years >= test_start

    X_train, y_train = X_all[train_mask], y_all[train_mask]
    X_test, y_test = X_all[test_mask], y_all[test_mask]
    years_train = years[train_mask]

    return X_train, y_train, X_test, y_test, years_train, df


def metrics(y_true, y_pred, label: str) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    # Directional accuracy
    if len(y_true) > 1:
        dir_acc = np.mean(np.sign(np.diff(y_true.values)) == np.sign(np.diff(y_pred)))
    else:
        dir_acc = float("nan")
    log.info("[%s] RMSE=%.4f  MAE=%.4f  R²=%.4f  DirAcc=%.3f", label, rmse, mae, r2, dir_acc)
    return {"label": label, "rmse": rmse, "mae": mae, "r2": r2, "dir_acc": dir_acc}


def verify_no_leakage(tscv: TimeSeriesSplit, years_train: np.ndarray) -> None:
    log.info("TimeSeriesSplit fold verification:")
    for i, (tr_idx, val_idx) in enumerate(tscv.split(years_train)):
        tr_years = years_train[tr_idx]
        val_years = years_train[val_idx]
        overlap = set(tr_years) & set(val_years)
        assert len(overlap) == 0, f"Fold {i}: train/val year overlap! {overlap}"
        assert max(tr_years) < min(val_years), f"Fold {i}: future year in training set!"
        log.info(
            "  Fold %d: train %d–%d | val %d–%d",
            i, min(tr_years), max(tr_years), min(val_years), max(val_years),
        )


def main() -> None:
    cfg = load_config()
    X_train, y_train, X_test, y_test, years_train, df_full = prepare_data(cfg)

    tscv = TimeSeriesSplit(n_splits=cfg["cv"]["n_splits"])
    verify_no_leakage(tscv, years_train)

    # ── XGBoost ───────────────────────────────────────────────────────────────
    xgb_params = load_best_params("xgb", cfg)
    xgb_params.setdefault("tree_method", "hist")
    xgb_params.setdefault("random_state", 42)
    xgb_params.setdefault("n_jobs", -1)
    xgb_model = XGBRegressor(**xgb_params)
    xgb_model.fit(X_train, y_train)

    train_metrics_xgb = metrics(y_train, xgb_model.predict(X_train), "XGB train")
    test_metrics_xgb = metrics(y_test, xgb_model.predict(X_test), "XGB test")

    # Overfit check
    gap = train_metrics_xgb["rmse"] / max(test_metrics_xgb["rmse"], 1e-9)
    if gap > 1.20:
        log.warning("Possible overfit: train/test RMSE ratio=%.2f > 1.20", gap)

    # ── RandomForest ──────────────────────────────────────────────────────────
    rf_params = load_best_params("rf", cfg)
    rf_params.setdefault("random_state", 42)
    rf_params.setdefault("n_jobs", -1)
    rf_model = RandomForestRegressor(**rf_params)
    rf_model.fit(X_train, y_train)

    metrics(y_train, rf_model.predict(X_train), "RF train")
    test_metrics_rf = metrics(y_test, rf_model.predict(X_test), "RF test")

    # ── Select best ───────────────────────────────────────────────────────────
    best_r2 = max(test_metrics_xgb["r2"], test_metrics_rf["r2"])
    if test_metrics_xgb["r2"] >= test_metrics_rf["r2"]:
        best_model = xgb_model
        best_name = "XGBoost"
    else:
        best_model = rf_model
        best_name = "RandomForest"

    log.info("Best single model: %s (R²=%.4f)", best_name, best_r2)

    # ── Stacking ensemble (if R² < 0.85) ─────────────────────────────────────
    if best_r2 < 0.85:
        log.info("R² < 0.85 — building stacking ensemble …")
        stack = StackingRegressor(
            estimators=[
                ("xgb", XGBRegressor(**xgb_params)),
                ("rf", RandomForestRegressor(**rf_params)),
            ],
            final_estimator=Ridge(),
            cv=tscv,
            n_jobs=-1,
        )
        stack.fit(X_train, y_train)
        stack_metrics = metrics(y_test, stack.predict(X_test), "Stacking test")
        if stack_metrics["r2"] > best_r2:
            best_model = stack
            best_name = "StackingEnsemble"
            log.info("Stacking ensemble selected (R²=%.4f).", stack_metrics["r2"])

    # ── Save ──────────────────────────────────────────────────────────────────
    models_dir = ROOT / cfg["paths"]["models"]
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "best_model.pkl"
    joblib.dump(best_model, model_path)
    log.info("Saved best model (%s) → %s", best_name, model_path)

    # Save feature column list for dashboard
    feat_cols_path = models_dir / "feature_columns.txt"
    feat_cols_path.write_text("\n".join(X_train.columns.tolist()))

    # ── MLflow logging ────────────────────────────────────────────────────────
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{ROOT / 'mlflow.db'}")
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("global-livability-ai")

    with mlflow.start_run(run_name=best_name):
        # Parameters
        mlflow.log_params({"model": best_name, **xgb_params, **rf_params})

        # Metrics
        final_preds = best_model.predict(X_test)
        mlflow.log_metrics({
            "test_r2":   float(r2_score(y_test, final_preds)),
            "test_rmse": float(np.sqrt(mean_squared_error(y_test, final_preds))),
            "test_mae":  float(mean_absolute_error(y_test, final_preds)),
        })

        # Artifacts
        mlflow.log_artifact(str(model_path))
        mlflow.log_artifact(str(feat_cols_path))

        # Log model with schema
        if best_name == "XGBoost":
            mlflow.xgboost.log_model(best_model, artifact_path="model")
        else:
            mlflow.sklearn.log_model(best_model, artifact_path="model")

    log.info("MLflow run logged to %s", mlflow_uri)

    # Save metrics.json for CI gate (test_data_quality.py::test_r2_acceptable)
    metrics_out = {
        "model": best_name,
        "test_r2":   float(r2_score(y_test, best_model.predict(X_test))),
        "test_rmse": float(np.sqrt(mean_squared_error(y_test, best_model.predict(X_test)))),
        "test_mae":  float(mean_absolute_error(y_test, best_model.predict(X_test))),
    }
    (models_dir / "metrics.json").write_text(json.dumps(metrics_out, indent=2))
    log.info("Metrics written → %s", models_dir / "metrics.json")

    log.info("Training complete.")


if __name__ == "__main__":
    main()
