
"""
src/impute.py
=============
Two-stage imputation:
  Stage 1 — Forward-fill within each country group (handles biennial EPI gaps)
  Stage 2 — IterativeImputer(BayesianRidge) cross-sectionally for residual NaNs

Output → data/processed/panel_imputed.csv (0 NaN values guaranteed)
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def impute(cfg: dict) -> pd.DataFrame:
    in_path = ROOT / cfg["paths"]["processed"] / "panel_raw.csv"
    df = pd.read_csv(in_path)

    id_cols = ["iso3", "year"]
    feature_cols = [c for c in df.columns if c not in id_cols]

    log.info("Before imputation: %.1f%% NaN", df[feature_cols].isnull().mean().mean() * 100)

    # Stage 1: forward-fill (then backward-fill to catch leading NaNs) within country
    df = df.sort_values(["iso3", "year"])
    df[feature_cols] = (
        df.groupby("iso3")[feature_cols]
        .transform(lambda g: g.ffill().bfill())
    )
    pct_after_ffill = df[feature_cols].isnull().mean().mean() * 100
    log.info("After ffill/bfill: %.1f%% NaN", pct_after_ffill)

    # Stage 2: IterativeImputer on numeric columns with remaining NaNs
    still_null_cols = [c for c in feature_cols if df[c].isnull().any()]
    if still_null_cols:
        log.info("Running IterativeImputer on %d columns", len(still_null_cols))
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            max_iter=10,
            random_state=42,
            verbose=0,
        )
        df[feature_cols] = imputer.fit_transform(df[feature_cols])
    else:
        log.info("No residual NaNs — IterativeImputer skipped.")

    # Clip imputed negatives for strictly positive indicators
    strictly_positive = [
        c for c in feature_cols
        if any(tok in c for tok in ["rate", "pct", "score", "index", "access",
                                    "spend", "gdp", "gni", "mortality", "expectancy",
                                    "beds", "incidence"])
    ]
    for col in strictly_positive:
        df[col] = df[col].clip(lower=0)

    assert df[feature_cols].isnull().sum().sum() == 0, "Imputation left NaN values!"
    log.info("Panel: %d countries, %d rows", df["iso3"].nunique(), len(df))

    out_path = ROOT / cfg["paths"]["processed"] / "panel_imputed.csv"
    df.to_csv(out_path, index=False)
    log.info("panel_imputed.csv: %s rows × %s cols | 0 NaN", len(df), len(df.columns))
    return df


def main() -> None:
    cfg = load_config()
    impute(cfg)


if __name__ == "__main__":
    main()
