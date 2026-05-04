
"""
src/tune.py
===========
Optuna hyperparameter search for XGBoost and RandomForest.
Uses TimeSeriesSplit CV; optimizes mean RMSE across folds.

Saves best params to:
  models/best_params_xgb.yaml
  models/best_params_rf.yaml
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def load_data(cfg: dict):
    feat_path = ROOT / cfg["paths"]["features"] / "features.csv"
    df = pd.read_csv(feat_path).sort_values(["iso3", "year"])

    train_end = cfg["temporal_split"]["train_end"]
    df_train = df[df["year"] <= train_end].copy()

    target_col = "target_score"
    drop_cols = ["iso3", "year", "target_score"] + [c for c in df.columns if c.startswith("pillar_")]
    # Drop any non-numeric columns
    drop_cols += [c for c in df_train.columns if df_train[c].dtype == object]

    X = df_train.drop(columns=[c for c in drop_cols if c in df_train.columns])
    y = df_train[target_col]
    return X, y


def cv_rmse(model, X: pd.DataFrame, y: pd.Series, n_splits: int) -> float:
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmses = []
    for train_idx, val_idx in tscv.split(X):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
        rmses.append(rmse)
    return float(np.mean(rmses))


# ── XGBoost tuning ────────────────────────────────────────────────────────────

def tune_xgboost(cfg: dict, X: pd.DataFrame, y: pd.Series) -> dict:
    xgb_cfg = cfg["optuna"]["xgboost"]
    n_trials = xgb_cfg["n_trials"]
    n_splits = cfg["cv"]["n_splits"]
    early_stop = xgb_cfg["early_stopping_rounds"]

    def objective(trial: optuna.Trial) -> float:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", *xgb_cfg["params"]["n_estimators"]),
            max_depth=trial.suggest_int("max_depth", *xgb_cfg["params"]["max_depth"]),
            learning_rate=trial.suggest_float("learning_rate", *xgb_cfg["params"]["learning_rate"], log=True),
            subsample=trial.suggest_float("subsample", *xgb_cfg["params"]["subsample"]),
            colsample_bytree=trial.suggest_float("colsample_bytree", *xgb_cfg["params"]["colsample_bytree"]),
            min_child_weight=trial.suggest_int("min_child_weight", *xgb_cfg["params"]["min_child_weight"]),
            reg_alpha=trial.suggest_float("reg_alpha", *xgb_cfg["params"]["reg_alpha"], log=True),
            reg_lambda=trial.suggest_float("reg_lambda", *xgb_cfg["params"]["reg_lambda"], log=True),
            tree_method="hist",
            random_state=42,
            n_jobs=-1,
            early_stopping_rounds=early_stop,
            eval_metric="rmse",
        )
        # Use last CV fold for early stopping eval set
        tscv = TimeSeriesSplit(n_splits=n_splits)
        *_, (tr_idx, val_idx) = tscv.split(X)
        X_tr, X_val = X.iloc[tr_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[tr_idx], y.iloc[val_idx]

        model = XGBRegressor(**params)
        model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
        preds = model.predict(X_val)
        return float(np.sqrt(mean_squared_error(y_val, preds)))

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(),
    )
    log.info("XGBoost Optuna: %d trials …", n_trials)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best = study.best_params
    log.info("XGBoost best RMSE: %.4f | params: %s", study.best_value, best)

    out_path = ROOT / cfg["paths"]["models"] / "best_params_xgb.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        yaml.dump(best, f)
    return best


# ── RandomForest tuning ───────────────────────────────────────────────────────

def tune_random_forest(cfg: dict, X: pd.DataFrame, y: pd.Series) -> dict:
    rf_cfg = cfg["optuna"]["random_forest"]
    n_trials = rf_cfg["n_trials"]
    n_splits = cfg["cv"]["n_splits"]

    def objective(trial: optuna.Trial) -> float:
        max_features_choices = rf_cfg["params"]["max_features"]
        max_features = trial.suggest_categorical("max_features", max_features_choices)
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", *rf_cfg["params"]["n_estimators"]),
            max_depth=trial.suggest_int("max_depth", *rf_cfg["params"]["max_depth"]),
            min_samples_split=trial.suggest_int("min_samples_split", *rf_cfg["params"]["min_samples_split"]),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", *rf_cfg["params"]["min_samples_leaf"]),
            max_features=max_features,
            random_state=42,
            n_jobs=-1,
        )
        model = RandomForestRegressor(**params)
        return cv_rmse(model, X, y, n_splits)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(),
    )
    log.info("RandomForest Optuna: %d trials …", n_trials)
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best = study.best_params
    log.info("RF best RMSE: %.4f | params: %s", study.best_value, best)

    out_path = ROOT / cfg["paths"]["models"] / "best_params_rf.yaml"
    with open(out_path, "w") as f:
        yaml.dump(best, f)
    return best


def main() -> None:
    cfg = load_config()
    X, y = load_data(cfg)
    log.info("Training set: %s rows × %s features", X.shape[0], X.shape[1])
    tune_xgboost(cfg, X, y)
    tune_random_forest(cfg, X, y)
    log.info("Hyperparameter tuning complete.")


if __name__ == "__main__":
    main()
