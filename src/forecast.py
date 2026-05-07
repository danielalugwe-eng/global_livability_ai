
"""
src/forecast.py
===============
Per-country polynomial-trend forecasting of the composite livability score.

• Fits a polynomial trend (degree 1 or 2) to each country's target_score
• Uses bootstrap resampling for 95% confidence intervals
• Withholds 2022–2024 for holdout evaluation
• Forecasts 5 years beyond the last observed year

Output:
  data/features/forecast_{iso3}.csv   — per-country forecast DataFrame
  app/assets/forecast_{iso3}.png      — forecast chart with confidence interval
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"

FORECAST_HORIZON = 5   # years beyond last observed
HOLDOUT_START = 2022   # years withheld for validation
N_BOOTSTRAP = 200
RNG_SEED = 42


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


def _fit_poly(years: np.ndarray, scores: np.ndarray, degree: int) -> np.ndarray:
    """Return polynomial coefficients (highest power first)."""
    return np.polyfit(years, scores, degree)


def forecast_country(
    iso3: str,
    country_name: str,
    df_full: pd.DataFrame,
    cfg: dict,
) -> pd.DataFrame:
    assets_dir = ROOT / cfg["paths"]["app_assets"]
    feat_dir = ROOT / cfg["paths"]["features"]
    assets_dir.mkdir(parents=True, exist_ok=True)
    feat_dir.mkdir(parents=True, exist_ok=True)

    country_df = df_full[df_full["iso3"] == iso3].copy().sort_values("year")
    country_df = country_df.dropna(subset=["target_score"])

    if len(country_df) < 4:
        log.warning("%s: not enough data, skipping", iso3)
        return pd.DataFrame()

    train_df = country_df[country_df["year"] < HOLDOUT_START]
    holdout_df = country_df[country_df["year"] >= HOLDOUT_START]

    log.info("%s: train=%d rows, holdout=%d rows", iso3, len(train_df), len(holdout_df))

    degree = 2 if len(train_df) >= 8 else 1

    train_years = train_df["year"].values.astype(float)
    train_scores = train_df["target_score"].values.astype(float)

    # Holdout evaluation
    if len(holdout_df) > 0:
        coeffs = _fit_poly(train_years, train_scores, degree)
        ho_pred = np.polyval(coeffs, holdout_df["year"].values.astype(float))
        ho_rmse = np.sqrt(np.mean((holdout_df["target_score"].values - ho_pred) ** 2))
        log.info("%s holdout RMSE (%d–): %.4f", iso3, HOLDOUT_START, ho_rmse)

    # Fit on all observed data
    all_years = country_df["year"].values.astype(float)
    all_scores = country_df["target_score"].values.astype(float)
    coeffs_full = _fit_poly(all_years, all_scores, degree)

    last_year = int(country_df["year"].max())
    future_years = np.arange(last_year + 1, last_year + FORECAST_HORIZON + 1, dtype=float)
    forecast_years = np.concatenate([all_years, future_years])

    yhat = np.polyval(coeffs_full, forecast_years)

    # Bootstrap CI
    rng = np.random.default_rng(RNG_SEED)
    n = len(all_years)
    boot_preds = []
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, n, size=n)
        c = np.polyfit(all_years[idx], all_scores[idx], degree)
        boot_preds.append(np.polyval(c, forecast_years))
    boot_preds_arr = np.array(boot_preds)
    yhat_lower = np.percentile(boot_preds_arr, 2.5, axis=0)
    yhat_upper = np.percentile(boot_preds_arr, 97.5, axis=0)

    yhat = np.clip(yhat, 0, 100)
    yhat_lower = np.clip(yhat_lower, 0, 100)
    yhat_upper = np.clip(yhat_upper, 0, 100)

    ds = pd.to_datetime([f"{int(y)}-01-01" for y in forecast_years])
    out_df = pd.DataFrame({
        "ds": ds,
        "year": forecast_years.astype(int),
        "yhat": yhat,
        "yhat_lower": yhat_lower,
        "yhat_upper": yhat_upper,
        "iso3": iso3,
    })

    out_path = feat_dir / f"forecast_{iso3}.csv"
    out_df.to_csv(out_path, index=False)

    # Plot
    obs_ds = pd.to_datetime([f"{int(y)}-01-01" for y in all_years])
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(ds, yhat_lower, yhat_upper, alpha=0.2, color="steelblue", label="95% CI")
    ax.plot(ds, yhat, color="steelblue", lw=2, label="Forecast")
    ax.scatter(obs_ds, all_scores, color="black", s=20, zorder=5, label="Observed")
    if len(holdout_df) > 0:
        ho_ds = pd.to_datetime([f"{int(y)}-01-01" for y in holdout_df["year"].values])
        ax.scatter(ho_ds, holdout_df["target_score"].values, color="red", s=20, zorder=5, label="Holdout")
    ax.axvline(pd.Timestamp(f"{last_year}-01-01"), color="gray", linestyle="--", alpha=0.5)
    ax.set_title(f"{country_name} — Livability Score Forecast")
    ax.set_xlabel("Year")
    ax.set_ylabel("Composite Score (0–100)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(assets_dir / f"forecast_{iso3}.png", dpi=150)
    plt.close(fig)
    log.info("Saved forecast_%s.png", iso3)

    return out_df


def main() -> None:
    cfg = load_config()

    feat_path = ROOT / cfg["paths"]["features"] / "features.csv"
    df = pd.read_csv(feat_path)

    # Load country names if available
    name_lookup: dict[str, str] = {}
    names_path = ROOT / cfg["paths"]["raw"] / "country_names.csv"
    if names_path.exists():
        _ndf = pd.read_csv(names_path)
        name_lookup = dict(zip(_ndf["iso3"], _ndf["country_name"]))

    all_forecasts: list[pd.DataFrame] = []
    for iso3 in sorted(df["iso3"].unique()):
        country_name = name_lookup.get(iso3, iso3)
        log.info("Forecasting: %s (%s)", country_name, iso3)
        fc = forecast_country(iso3, country_name, df, cfg)
        if len(fc):
            all_forecasts.append(fc)

    # Consolidate into a single file for the dashboard
    if all_forecasts:
        consolidated = pd.concat(all_forecasts, ignore_index=True)
        out_dir = ROOT / "data" / "forecasts"
        out_dir.mkdir(parents=True, exist_ok=True)
        consolidated.to_csv(out_dir / "forecasts.csv", index=False)
        log.info("Saved consolidated forecasts.csv: %d rows, %d countries",
                 len(consolidated), consolidated["iso3"].nunique())

    log.info("Forecasting complete.")


if __name__ == "__main__":
    main()
