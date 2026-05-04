
"""
src/harmonize.py
================
Merge all raw data sources on (iso3, year) → data/processed/panel_raw.csv
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def build_panel(cfg: dict) -> pd.DataFrame:
    raw_dir = ROOT / cfg["paths"]["raw"]
    years = list(range(cfg["years"]["start"], cfg["years"]["end"] + 1))

    # Derive country list from collected World Bank data
    wb_raw = pd.read_csv(raw_dir / "world_bank.csv")
    countries = sorted(wb_raw["iso3"].unique().tolist())

    # Full cartesian grid — no (country, year) pair left behind
    grid = pd.DataFrame(
        [(iso3, year) for iso3 in countries for year in years],
        columns=["iso3", "year"],
    )

    # ── World Bank ─────────────────────────────────────────────────────────────
    wb_path = raw_dir / "world_bank.csv"
    wb = pd.read_csv(wb_path)
    wb_cols = ["iso3", "year"] + [c for c in wb.columns if c not in ("iso3", "year", "country_name")]
    wb = wb[wb_cols].copy()
    wb["year"] = wb["year"].astype(int)
    wb = wb.groupby(["iso3", "year"], as_index=False).mean(numeric_only=True)
    panel = grid.merge(wb, on=["iso3", "year"], how="left")
    log.info("After World Bank merge: %s rows", len(panel))

    # ── UNDP HDI ───────────────────────────────────────────────────────────────
    undp_path = raw_dir / "undp_hdi.csv"
    undp = pd.read_csv(undp_path)
    undp["year"] = undp["year"].astype(int)
    undp = undp.groupby(["iso3", "year"], as_index=False).mean(numeric_only=True)
    panel = panel.merge(undp, on=["iso3", "year"], how="left")
    log.info("After UNDP merge: %s rows", len(panel))

    # ── WHO GHO ────────────────────────────────────────────────────────────────
    who_path = raw_dir / "who_gho.csv"
    who = pd.read_csv(who_path)
    who["year"] = who["year"].astype(int)
    # Deduplicate: WHO API returns sex-disaggregated rows; collapse to mean per country-year
    who = who.groupby(["iso3", "year"], as_index=False).mean(numeric_only=True)
    panel = panel.merge(who, on=["iso3", "year"], how="left")
    log.info("After WHO merge: %s rows", len(panel))

    # ── Yale EPI ───────────────────────────────────────────────────────────────
    epi_path = raw_dir / "yale_epi.csv"
    epi = pd.read_csv(epi_path)
    epi["year"] = epi["year"].astype(int)
    epi = epi.groupby(["iso3", "year"], as_index=False).mean(numeric_only=True)
    panel = panel.merge(epi, on=["iso3", "year"], how="left")
    log.info("After EPI merge: %s rows", len(panel))

    # Ensure correct types
    panel["year"] = panel["year"].astype(int)
    panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)

    out_path = ROOT / cfg["paths"]["processed"] / "panel_raw.csv"
    panel.to_csv(out_path, index=False)
    log.info(
        "panel_raw.csv: %s rows × %s cols | NaN rate: %.1f%%",
        len(panel), len(panel.columns),
        panel.isnull().mean().mean() * 100,
    )
    return panel


def main() -> None:
    cfg = load_config()
    (ROOT / cfg["paths"]["processed"]).mkdir(parents=True, exist_ok=True)
    build_panel(cfg)


if __name__ == "__main__":
    main()
