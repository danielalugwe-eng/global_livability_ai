
"""
src/features.py
===============
Engineer model inputs from panel_imputed.csv:
  • Lag features     : every indicator at t-1 and t-2
  • Rate-of-change   : (x_t - x_{t-1}) / x_{t-1} for key indicators
  • Interaction terms: domain-knowledge cross-products
  • Country one-hot encoding
  • year_since_2000 trend signal

Output → data/features/features.csv
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"

# Indicators for rate-of-change features
ROC_INDICATORS = [
    "air_quality_score",
    "gdp_per_capita_ppp",
    "life_expectancy",
    "internet_users_pct",
    "epi_score",
    "hdi_score",
]


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def engineer_features(cfg: dict) -> pd.DataFrame:
    in_path = ROOT / cfg["paths"]["processed"] / "panel_imputed.csv"
    df = pd.read_csv(in_path).sort_values(["iso3", "year"]).reset_index(drop=True)

    id_cols = ["iso3", "year"]
    raw_feature_cols = [c for c in df.columns if c not in id_cols]

    # ── Lag features ──────────────────────────────────────────────────────────
    log.info("Computing lag features …")
    lag_frames: list[pd.DataFrame] = []
    for lag in (1, 2):
        lagged = (
            df.groupby("iso3")[raw_feature_cols]
            .shift(lag)
            .rename(columns={c: f"{c}_lag{lag}" for c in raw_feature_cols})
        )
        lag_frames.append(lagged)

    df = pd.concat([df] + lag_frames, axis=1)

    # ── Rate-of-change features ───────────────────────────────────────────────
    log.info("Computing rate-of-change features …")
    for col in ROC_INDICATORS:
        if col in df.columns:
            prev = df.groupby("iso3")[col].shift(1)
            df[f"{col}_roc"] = ((df[col] - prev) / prev.replace(0, np.nan)).fillna(0)

    # ── Interaction features ──────────────────────────────────────────────────
    log.info("Computing interaction features …")
    _safe_mul = lambda a, b: df[a] * df[b] if a in df.columns and b in df.columns else None

    interactions = {
        "interact_health_spend_x_life_exp": ("healthcare_spend_per_capita", "life_expectancy"),
        "interact_edu_spend_x_hdi": ("education_spend_pct_gdp", "hdi_score"),
        "interact_co2_x_epi_air": ("co2_emissions_per_capita", "air_quality_score"),
    }
    for feat_name, (col_a, col_b) in interactions.items():
        result = _safe_mul(col_a, col_b)
        if result is not None:
            df[feat_name] = result

    # ── Country one-hot encoding ──────────────────────────────────────────────
    log.info("One-hot encoding country …")
    country_dummies = pd.get_dummies(df["iso3"], prefix="country", dtype=int)
    df = pd.concat([df, country_dummies], axis=1)

    # ── Temporal trend ────────────────────────────────────────────────────────
    df["year_since_2000"] = df["year"] - 2000

    # Drop rows where lag-2 is NaN (first 2 years per country) — not useful for training
    lag2_cols = [c for c in df.columns if c.endswith("_lag2")]
    df = df.dropna(subset=lag2_cols[:1]).reset_index(drop=True)

    out_path = ROOT / cfg["paths"]["features"] / "features.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    log.info("features.csv: %s rows × %s cols", len(df), len(df.columns))
    return df


def main() -> None:
    cfg = load_config()
    engineer_features(cfg)


if __name__ == "__main__":
    main()
