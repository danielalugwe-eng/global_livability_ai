
"""
src/explain.py
==============
SHAP explainability for the best trained model.

Outputs:
  app/assets/shap_global.png        — mean |SHAP| bar chart
  app/assets/shap_{country}.png     — per-country waterfall (latest year)
  app/assets/shap_dependence_{feat}.png — top-5 feature dependence plots
  data/features/shap_values.csv     — full SHAP matrix for dashboard
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def main() -> None:
    cfg = load_config()
    assets_dir = ROOT / cfg["paths"]["app_assets"]
    assets_dir.mkdir(parents=True, exist_ok=True)

    # ── Load model and features ───────────────────────────────────────────────
    model_path = ROOT / cfg["paths"]["models"] / "best_model.pkl"
    model = joblib.load(model_path)

    feat_path = ROOT / cfg["paths"]["features"] / "features.csv"
    df = pd.read_csv(feat_path).sort_values(["iso3", "year"])

    feat_cols_path = ROOT / cfg["paths"]["models"] / "feature_columns.txt"
    feature_cols = feat_cols_path.read_text().splitlines()

    X = df[feature_cols]

    # ── SHAP values ───────────────────────────────────────────────────────────
    # Unwrap stacking ensemble to its XGBoost sub-model if needed
    underlying = model
    if hasattr(model, "final_estimator_"):
        # StackingRegressor — use the first base estimator for SHAP
        underlying = model.estimators_[0][1]
    elif hasattr(model, "estimators"):
        # RF
        pass

    log.info("Computing SHAP values …")
    explainer = shap.TreeExplainer(underlying)
    shap_values = explainer(X)   # returns Explanation object

    sv_matrix = shap_values.values  # (n_samples, n_features)

    # ── Integrity check ───────────────────────────────────────────────────────
    preds = underlying.predict(X)
    base_val = shap_values.base_values
    reconstruction = base_val + sv_matrix.sum(axis=1)
    max_diff = np.abs(reconstruction - preds).max()
    log.info("SHAP integrity: max |base + Σshap - pred| = %.6f", max_diff)
    assert max_diff < 0.1, f"SHAP integrity check failed: max diff = {max_diff}"

    # ── Global feature importance ─────────────────────────────────────────────
    mean_abs = np.abs(sv_matrix).mean(axis=0)
    importance_df = pd.DataFrame({"feature": feature_cols, "mean_abs_shap": mean_abs})
    importance_df = importance_df.sort_values("mean_abs_shap", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    top20 = importance_df.head(20)
    ax.barh(top20["feature"][::-1], top20["mean_abs_shap"][::-1], color="steelblue")
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Global Feature Importance (Top 20)")
    plt.tight_layout()
    fig.savefig(assets_dir / "shap_global.png", dpi=150)
    plt.close(fig)
    log.info("Saved shap_global.png")

    # ── Per-country waterfall plots (latest year) — top 30 by score ─────────────
    name_lookup: dict[str, str] = {}
    names_path = ROOT / cfg["paths"]["raw"] / "country_names.csv"
    if names_path.exists():
        _ndf = pd.read_csv(names_path)
        name_lookup = dict(zip(_ndf["iso3"], _ndf["country_name"]))

    latest_year_shap = df["year"].max()
    if "target_score" in df.columns:
        top_iso = (
            df[df["year"] == latest_year_shap]
            .groupby("iso3")["target_score"].mean()
            .nlargest(30).index.tolist()
        )
    else:
        top_iso = df["iso3"].unique().tolist()[:30]

    for iso3 in top_iso:
        mask = (df["iso3"] == iso3)
        if not mask.any():
            continue
        latest_idx = df[mask]["year"].idxmax()
        row_pos = df.index.get_loc(latest_idx)

        exp = shap.Explanation(
            values=sv_matrix[row_pos],
            base_values=float(base_val[row_pos]) if hasattr(base_val, "__len__") else float(base_val),
            data=X.iloc[row_pos].values,
            feature_names=feature_cols,
        )
        fig, ax = plt.subplots(figsize=(10, 7))
        shap.waterfall_plot(exp, max_display=15, show=False)
        cname = name_lookup.get(iso3, iso3)
        plt.title(f"{cname} — Latest Year SHAP Waterfall")
        plt.tight_layout()
        fig.savefig(assets_dir / f"shap_{iso3}.png", dpi=150)
        plt.close(fig)
        log.info("Saved shap_%s.png", iso3)

    # ── Dependence plots for top 5 features ───────────────────────────────────
    top5_feats = importance_df["feature"].head(5).tolist()
    for feat in top5_feats:
        fig, ax = plt.subplots(figsize=(7, 5))
        feat_idx = feature_cols.index(feat)
        ax.scatter(X[feat], sv_matrix[:, feat_idx], alpha=0.6, s=20, c="darkcyan")
        ax.set_xlabel(feat)
        ax.set_ylabel(f"SHAP value for {feat}")
        ax.set_title(f"SHAP Dependence: {feat}")
        plt.tight_layout()
        safe_name = feat.replace("/", "_")[:50]
        fig.savefig(assets_dir / f"shap_dependence_{safe_name}.png", dpi=150)
        plt.close(fig)
        log.info("Saved shap_dependence_%s.png", safe_name)

    # ── Save SHAP matrix CSV ──────────────────────────────────────────────────
    shap_df = pd.DataFrame(sv_matrix, columns=[f"shap_{c}" for c in feature_cols])
    shap_df.insert(0, "year", df["year"].values)
    shap_df.insert(0, "iso3", df["iso3"].values)
    shap_df["predicted_score"] = preds
    shap_out = ROOT / cfg["paths"]["features"] / "shap_values.csv"
    shap_df.to_csv(shap_out, index=False)
    log.info("Saved shap_values.csv (%s rows × %s cols)", len(shap_df), len(shap_df.columns))


if __name__ == "__main__":
    main()
