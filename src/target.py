
"""
src/target.py
=============
Build the composite livability target score (0–100):
  1. Min-max normalize each indicator to 0–100 (global range)
  2. Invert "lower is better" indicators
  3. Average within each pillar
  4. Weighted sum across pillars per config.yaml weights

Output → data/features/features.csv  (adds 'target_score' column)
         data/features/target_debug.csv (pillar sub-scores)
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


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def minmax_normalize(series: pd.Series) -> pd.Series:
    """Normalize to [0, 100] using global (all rows) min/max."""
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(50.0, index=series.index)
    return (series - lo) / (hi - lo) * 100


def build_target(cfg: dict) -> pd.DataFrame:
    feat_path = ROOT / cfg["paths"]["features"] / "features.csv"
    df = pd.read_csv(feat_path)

    pillars: dict[str, dict] = cfg["pillar_indicators"]
    weights: dict[str, float] = cfg["pillar_weights"]

    # Use the base (non-lagged) indicators from panel_imputed for target construction
    imputed_path = ROOT / cfg["paths"]["processed"] / "panel_imputed.csv"
    base = pd.read_csv(imputed_path).sort_values(["iso3", "year"]).reset_index(drop=True)

    # Normalize each indicator globally
    all_indicators = [
        ind
        for pillar_def in pillars.values()
        for ind in (pillar_def.get("positive", []) + pillar_def.get("negative", []))
    ]
    norm: dict[str, pd.Series] = {}
    for ind in all_indicators:
        if ind in base.columns:
            raw = base[ind].copy()
            norm[ind] = minmax_normalize(raw)
        else:
            log.warning("Indicator %s not found in panel — skipped.", ind)

    # Compute pillar scores
    pillar_scores: dict[str, pd.Series] = {}
    for pillar_name, pillar_def in pillars.items():
        components: list[pd.Series] = []
        for ind in pillar_def.get("positive", []):
            if ind in norm:
                components.append(norm[ind])
        for ind in pillar_def.get("negative", []):
            if ind in norm:
                components.append(100 - norm[ind])   # invert
        if components:
            pillar_scores[pillar_name] = pd.concat(components, axis=1).mean(axis=1)
        else:
            pillar_scores[pillar_name] = pd.Series(50.0, index=base.index)

    # Weighted composite score
    composite = sum(
        pillar_scores[p] * weights.get(p, 0.0)
        for p in pillar_scores
    )
    base["target_score"] = composite
    for p, s in pillar_scores.items():
        base[f"pillar_{p}"] = s

    # Sanity check: Singapore should rank highest on average
    avg_by_country = base.groupby("iso3")["target_score"].mean().sort_values(ascending=False)
    log.info("Average target_score by country:\n%s", avg_by_country.to_string())
    top = avg_by_country.idxmax()
    _HIGH_DEV = {"SGP", "NOR", "CHE", "AUS", "IRL", "DNK", "SWE", "NLD",
                 "DEU", "FIN", "NZL", "USA", "GBR", "AUT", "BEL", "CAN",
                 "JPN", "ISL", "KOR", "LUX", "ISR"}
    if top in _HIGH_DEV:
        log.info("Sanity check PASSED: %s has highest average score.", top)
    else:
        log.warning("Top country is %s — verify scoring is reasonable.", top)

    # Merge target back into features dataframe
    target_cols = ["iso3", "year", "target_score"] + [f"pillar_{p}" for p in pillar_scores]
    df = df.merge(base[target_cols], on=["iso3", "year"], how="left")

    # Save
    feat_out = ROOT / cfg["paths"]["features"] / "features.csv"
    df.to_csv(feat_out, index=False)

    debug_out = ROOT / cfg["paths"]["features"] / "target_debug.csv"
    base[target_cols].to_csv(debug_out, index=False)

    log.info(
        "target_score stats: min=%.2f  max=%.2f  mean=%.2f",
        df["target_score"].min(), df["target_score"].max(), df["target_score"].mean(),
    )
    return df


def main() -> None:
    cfg = load_config()
    build_target(cfg)


if __name__ == "__main__":
    main()
