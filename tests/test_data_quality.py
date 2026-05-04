# ─────────────────────────────────────────────────────────────────────────────
# tests/test_data_quality.py
#
# Data engineering quality gates for every pipeline stage.
# Run with:  pytest tests/test_data_quality.py -v
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import pathlib

import pandas as pd
import pytest
import yaml

ROOT = pathlib.Path(__file__).parent.parent
DATA = ROOT / "data"
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())


# ─────────────────────────────────────────────────────────────────────────────
# Raw data checks
# ─────────────────────────────────────────────────────────────────────────────

class TestRawData:
    """Validate files produced by collect.py."""

    def test_world_bank_exists(self):
        assert (DATA / "raw" / "world_bank.csv").exists(), "world_bank.csv missing — run collect.py"

    def test_world_bank_schema(self):
        df = pd.read_csv(DATA / "raw" / "world_bank.csv")
        required = {"iso3", "year"}
        missing = required - set(df.columns)
        assert not missing, f"world_bank.csv missing columns: {missing}"

    def test_world_bank_no_empty_iso3(self):
        df = pd.read_csv(DATA / "raw" / "world_bank.csv")
        assert df["iso3"].notna().all(), "world_bank.csv contains null iso3 values"

    def test_world_bank_iso3_length(self):
        df = pd.read_csv(DATA / "raw" / "world_bank.csv")
        bad = df[df["iso3"].str.len() != 3]
        assert bad.empty, f"Non-3-char ISO3 codes found:\n{bad['iso3'].unique()}"

    def test_world_bank_year_range(self):
        df = pd.read_csv(DATA / "raw" / "world_bank.csv")
        start = CFG["years"]["start"]
        end = CFG["years"]["end"]
        assert df["year"].min() >= start, f"year < {start}"
        assert df["year"].max() <= end, f"year > {end}"

    def test_country_names_exists(self):
        assert (DATA / "raw" / "country_names.csv").exists()

    def test_country_names_schema(self):
        df = pd.read_csv(DATA / "raw" / "country_names.csv")
        assert {"iso3", "name"}.issubset(df.columns)


# ─────────────────────────────────────────────────────────────────────────────
# Processed / feature store checks
# ─────────────────────────────────────────────────────────────────────────────

class TestFeatureStore:
    """Validate files produced by harmonize → impute → features → target."""

    PANEL = DATA / "processed" / "panel.parquet"
    IMPUTED = DATA / "processed" / "imputed.parquet"
    FEATURES = DATA / "features" / "features.parquet"
    TARGET = DATA / "features" / "target.parquet"

    def test_panel_exists(self):
        assert self.PANEL.exists(), "panel.parquet missing — run harmonize.py"

    def test_imputed_exists(self):
        assert self.IMPUTED.exists(), "imputed.parquet missing — run impute.py"

    def test_features_exists(self):
        assert self.FEATURES.exists(), "features.parquet missing — run features.py"

    def test_target_exists(self):
        assert self.TARGET.exists(), "target.parquet missing — run target.py"

    def test_features_no_all_nan_columns(self):
        df = pd.read_parquet(self.FEATURES)
        all_nan = [c for c in df.columns if df[c].isna().all()]
        assert not all_nan, f"Features with 100% NaN: {all_nan}"

    def test_target_score_in_range(self):
        df = pd.read_parquet(self.TARGET)
        assert "livability_score" in df.columns
        assert df["livability_score"].between(0, 1).all(), "Scores outside [0, 1]"

    def test_target_no_duplicate_keys(self):
        df = pd.read_parquet(self.TARGET)
        dupes = df[df.duplicated(subset=["iso3", "year"])]
        assert dupes.empty, f"Duplicate (iso3, year) rows:\n{dupes.head()}"

    def test_minimum_countries(self):
        df = pd.read_parquet(self.TARGET)
        n = df["iso3"].nunique()
        assert n >= 50, f"Only {n} countries in target — expected at least 50"

    def test_features_no_inf(self):
        import numpy as np
        df = pd.read_parquet(self.FEATURES)
        num = df.select_dtypes("number")
        assert not np.isinf(num.values).any(), "Infinite values found in features"


# ─────────────────────────────────────────────────────────────────────────────
# Model artefact checks
# ─────────────────────────────────────────────────────────────────────────────

class TestModelArtifacts:
    """Validate model files produced by train.py."""

    MODELS = ROOT / "models"

    def test_model_file_exists(self):
        pkls = list(self.MODELS.glob("*.pkl"))
        assert pkls, "No .pkl model files found — run train.py"

    def test_metrics_exist(self):
        metrics = self.MODELS / "metrics.json"
        assert metrics.exists(), "metrics.json missing — run train.py"

    def test_r2_acceptable(self):
        import json
        metrics = json.loads((self.MODELS / "metrics.json").read_text())
        r2 = metrics.get("test_r2", -1)
        assert r2 >= 0.70, f"Test R²={r2:.3f} below threshold 0.70"
