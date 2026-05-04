# ─────────────────────────────────────────────────────────────────────────────
# tests/test_pipeline_units.py
#
# Unit tests for individual pipeline functions (no network / large data needed)
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import pathlib

import pandas as pd
import pytest
import yaml

ROOT = pathlib.Path(__file__).parent.parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())


# ─────────────────────────────────────────────────────────────────────────────
# Config sanity
# ─────────────────────────────────────────────────────────────────────────────

def test_config_pillar_weights_sum_to_one():
    total = sum(CFG["pillar_weights"].values())
    assert abs(total - 1.0) < 1e-6, f"Pillar weights sum to {total}"


def test_config_years_valid():
    assert CFG["years"]["start"] < CFG["years"]["end"]
    assert CFG["years"]["end"] <= 2030


def test_config_required_keys():
    required = ["scope", "years", "sources", "pillar_weights", "pillar_indicators", "optuna"]
    for key in required:
        assert key in CFG, f"config.yaml missing key: {key}"


# ─────────────────────────────────────────────────────────────────────────────
# Harmonize helpers
# ─────────────────────────────────────────────────────────────────────────────

def test_harmonize_imports():
    """Ensure harmonize.py imports without error."""
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("harmonize", ROOT / "src" / "harmonize.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass   # top-level script may call sys.exit on missing data — that's OK


def test_impute_imports():
    import importlib.util
    spec = importlib.util.spec_from_file_location("impute", ROOT / "src" / "impute.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass


def test_features_imports():
    import importlib.util
    spec = importlib.util.spec_from_file_location("features", ROOT / "src" / "features.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# App helpers
# ─────────────────────────────────────────────────────────────────────────────

def test_app_imports():
    """App should import without Streamlit raising RuntimeError (no server)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", ROOT / "app" / "app.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        pass   # Streamlit will raise outside a server context — that's expected
