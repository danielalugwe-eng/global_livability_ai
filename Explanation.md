# Asia Livability AI — Deep Code Explanation

> A complete, line-by-line walkthrough of every folder, file, and script in the project — explained simply.

---

## The Folder Structure — What Each Folder Is For

```
sea_livability_ai/          ← The whole project lives here (root folder)
│
├── src/                    ← The "brain" — Python scripts that do all the work
├── app/                    ← The "face" — the website you open in a browser
├── data/                   ← Where all files (raw, cleaned, processed) are saved
├── models/                 ← Where the trained AI brain is saved
├── tests/                  ← Scripts that check nothing is broken
├── kestra/                 ← Automation (schedules the pipeline to run by itself)
├── terraform/              ← Cloud setup (rents servers on Amazon AWS automatically)
└── config.yaml             ← The settings file — like the recipe card for the whole project
```

Think of it like a restaurant:
- `src/` = the kitchen (where food is cooked)
- `app/` = the dining room (what customers see)
- `data/` = the pantry + fridge
- `models/` = the chef's secret recipe book
- `config.yaml` = the menu

---

## The Files at the Root Level

---

### `config.yaml` — The Settings File

This is the most important file. Every script reads it. Think of it as the **master control panel**.

```yaml
scope: asia                    # "Which countries are we studying?" Asia.
countries:
  CHN: China                   # Each country gets a 3-letter code (CHN = China)
  JPN: Japan                   # These codes are international standards (ISO3)
  SGP: Singapore               # ...all 49 countries listed here
```

```yaml
years:
  start: 2000                  # We want data going back to year 2000
  end: 2024                    # ...up to 2024
```

```yaml
sources:
  world_bank:
    indicators:
      SP.DYN.LE00.IN: life_expectancy   # "SP.DYN.LE00.IN" is the World Bank's code
                                         # for life expectancy. We rename it to
                                         # "life_expectancy" so it's readable.
      SP.DYN.IMRT.IN: infant_mortality  # How many babies die before age 1
      NY.GDP.PCAP.PP.CD: gdp_per_capita_ppp  # How rich the country is per person
```

```yaml
pillar_weights:
  health: 0.30        # Health counts for 30% of the total score
  economy: 0.25       # Economy counts for 25%
  education: 0.15     # Education counts for 15%
  environment: 0.20   # Environment counts for 20%
  safety_infra: 0.10  # Safety counts for 10%
                      # All must add up to 1.0 (= 100%)
```

```yaml
pillar_indicators:
  health:
    positive: [life_expectancy, uhc_service_coverage_index]  # Higher = better score
    negative: [infant_mortality]   # Lower = better score (so we FLIP this one)
```

```yaml
optuna:
  xgboost:
    n_trials: 100      # Try 100 different combinations of AI settings
    params:
      max_depth: [2, 8]  # Try tree depths between 2 and 8
      learning_rate: [0.01, 0.3]  # Try learning speeds between 0.01 and 0.3
```

---

### `requirements.txt` — The Shopping List

Before you can cook, you need ingredients. This file lists every Python library the project needs.

```
pandas>=2.2         # The spreadsheet tool — loads and manipulates tables of data
numpy>=1.26         # Math library — handles numbers, arrays, statistics
requests>=2.32      # Downloads data from the internet (like a web browser for Python)
openpyxl>=3.1       # Opens Excel files (.xlsx)
scikit-learn==1.4.2 # ML toolkit — has tools for imputation, cross-validation, etc.
xgboost==2.0.3      # The main AI model (XGBoost = Extreme Gradient Boosting)
optuna==3.6.1       # Finds the best settings for the AI automatically
shap==0.45.1        # Explains WHY the AI gave each country its score
matplotlib==3.8.4   # Draws charts and saves them as images
streamlit==1.34.0   # Turns Python code into a website
plotly==5.22.0      # Interactive charts in the website (you can hover and zoom)
mlflow==2.12.2      # Keeps a diary of every model training run
joblib==1.4.0       # Saves and loads the trained model to/from disk
pyyaml==6.0.1       # Reads .yaml files (like config.yaml)
```

---

### `pyproject.toml` — Code Quality Rules

This is the **grammar rulebook** for the code. It tells tools like `ruff` (a linter) what style rules to enforce.

```toml
[tool.ruff]
line-length = 100      # Lines of code can't be longer than 100 characters

[tool.ruff.lint]
select = ["E", "W", "F", "I"]   # Check for errors (E), warnings (W),
                                  # undefined names (F), and import order (I)
ignore = ["E501"]      # But ignore "line too long" since formatter handles it
```

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]     # "Look for test files inside the tests/ folder"
python_functions = "test_*"  # "Any function starting with test_ is a test"
```

---

### `Makefile` — The Shortcut Button Panel

Instead of typing long commands, you type `make data` and it runs several scripts in one go.

```makefile
data:
    python src/collect.py    # Step 1: download data
    python src/harmonize.py  # Step 2: merge it
    python src/impute.py     # Step 3: fill gaps

features:
    python src/features.py   # Step 4: build smart columns
    python src/target.py     # Step 5: calculate scores

train:
    python src/tune.py       # Step 6: find best AI settings
    python src/train.py      # Step 7: train the AI

app:
    streamlit run app/app.py  # Launch the website

clean:
    rm -rf data/processed/* models/* app/assets/*.png  # Delete all generated files (start fresh)
```

---

### `Dockerfile` — The Shipping Box

A Dockerfile is like instructions for packing the entire app into a sealed box (called a container) that can run anywhere.

```dockerfile
FROM python:3.11-slim AS base   # Start with a clean, tiny computer that has Python 3.11 installed

RUN apt-get update && apt-get install -y \
    build-essential git curl libgomp1   # Install extra tools the OS needs
    && rm -rf /var/lib/apt/lists/*      # Delete the installer cache to save space

WORKDIR /app          # "Go to the /app folder inside the container" (like cd /app)

COPY requirements.txt .    # Copy the shopping list into the container
RUN pip install -r requirements.txt    # Install everything on the list

COPY config.yaml .    # Copy settings file
COPY src/ src/        # Copy all pipeline scripts
COPY app/ app/        # Copy the dashboard code

RUN mkdir -p data/raw data/processed models app/assets  # Create empty folders

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app   # Create a non-admin user for safety
USER appuser                            # Switch to that user (never run as root!)

ENV STREAMLIT_SERVER_PORT=8501    # Tell Streamlit to use port 8501
EXPOSE 8501                       # Open port 8501 so the outside world can connect

CMD ["streamlit", "run", "app/app.py"]  # Default: when the container starts, launch the website
```

---

### `docker-compose.yml` — Running Multiple Boxes Together

Docker Compose runs multiple containers at once and connects them.

```yaml
volumes:
  livability_data:     # A shared hard drive that ALL containers can read/write
  mlflow_data:         # A separate drive just for MLflow's experiment logs

services:
  mlflow:              # Container 1: the experiment diary server
    image: ghcr.io/mlflow/mlflow:v2.12.2   # Use the official MLflow image
    ports:
      - "5000:5000"    # Port 5000 on your laptop connects to port 5000 inside

  pipeline:            # Container 2: runs collect → harmonize → impute → features → target
    build: .           # Build from our Dockerfile
    command: sh -c "python src/collect.py && python src/harmonize.py ..."

  app:                 # Container 3: the Streamlit dashboard
    ports:
      - "8501:8501"    # Open port 8501 so you can visit http://localhost:8501
```

---

## The `src/` Folder — The Pipeline Scripts

These 9 scripts run **in order**, each one building on the previous.

---

### `src/collect.py` — Download the Raw Data

**Job:** Go to the internet, download data from 4 websites, save as CSV files.

```python
from pathlib import Path   # Like os.path but nicer — helps build file paths
import pandas as pd        # Table manipulation
import requests            # Makes HTTP requests (downloads web pages/data)
import yaml                # Reads the config.yaml file

ROOT = Path(__file__).resolve().parents[1]
# __file__ = this script's location
# .resolve() = get the full absolute path
# .parents[1] = go up 2 folders → lands at the project root

CFG_PATH = ROOT / "config.yaml"  # Build path: project_root/config.yaml
```

```python
_NAME_TO_ISO3: dict[str, str] = {
    "Afghanistan": "AFG",   # A giant lookup table: country name → 3-letter code
    "China": "CHN",         # Because different data sources spell names differently
    "Viet Nam": "VNM",      # (WHO says "Viet Nam", World Bank says "Vietnam")
    ...                      # So we standardize everything to the 3-letter ISO3 code
}
```

```python
def _get_wb_countries(timeout=30) -> dict:
    result = {}
    page = 1
    while True:                        # Keep looping through pages of results
        resp = requests.get(           # Download one page from World Bank API
            _WB_COUNTRIES_URL,
            params={"format": "json", "per_page": 300, "page": page},
            timeout=timeout,           # Give up after 30 seconds if no response
        )
        resp.raise_for_status()        # If the website returned an error, crash loudly
        body = resp.json()             # Parse the JSON response into a Python dict
        for rec in body[1]:            # Loop over each country record
            iso3 = rec.get("id")       # Get the 3-letter code
            region = rec.get("region") or {}
            if len(iso3) == 3 and region.get("id") != "NA":  # Skip non-countries (aggregates)
                result[iso3] = rec.get("name", iso3)
        if page >= body[0]["pages"]:   # If we've read all pages, stop looping
            break
        page += 1                      # Otherwise go to next page
    return result
```

```python
def collect_world_bank(cfg):
    scope = cfg.get("scope", "global")
    if scope != "global" and "countries" in cfg:
        valid_iso3 = set(cfg["countries"].keys())  # Only keep the 49 Asian countries

    for ind_code, col_name in indicators.items():  # Loop over each indicator
        url = _WB_INDICATOR_URL.format(indicator=ind_code)  # Build the URL
        rows = []
        while True:                    # Page through results
            resp = requests.get(url, params=params, timeout=60)
            for rec in body[1]:
                iso3 = rec.get("countryiso3code")
                if iso3 not in valid_iso3:
                    continue           # Skip countries we don't care about
                rows.append({"iso3": iso3, "year": int(yr), col_name: float(val)})
```

---

### `src/harmonize.py` — Merge All Sources Into One Big Table

**Job:** Take 4 separate CSV files and combine them into one master table where each row = one country + one year.

```python
def build_panel(cfg):
    years = list(range(cfg["years"]["start"], cfg["years"]["end"] + 1))
    # → [2000, 2001, 2002, ..., 2024]

    grid = pd.DataFrame(
        [(iso3, year) for iso3 in countries for year in years],
        columns=["iso3", "year"],
    )
    # Creates a "skeleton" table with ALL combinations of countries and years
    # e.g.: (CHN, 2000), (CHN, 2001), ..., (SGP, 2024)
    # This ensures NO (country, year) row is missing even if a source didn't report it

    panel = grid.merge(wb, on=["iso3", "year"], how="left")
    # "left" merge = keep ALL rows from grid, add WB columns where available
    # Missing data gets NaN (blank) — that's OK, impute.py fixes it next

    panel = panel.merge(undp, on=["iso3", "year"], how="left")  # Add UNDP columns
    panel = panel.merge(who,  on=["iso3", "year"], how="left")  # Add WHO columns
    panel = panel.merge(epi,  on=["iso3", "year"], how="left")  # Add Yale EPI columns

    panel.to_csv(out_path, index=False)  # Save to disk as panel_raw.csv
```

---

### `src/impute.py` — Fill in the Blank Cells

**Job:** Some cells in the table are empty (NaN). Fill them in with smart estimates.

```python
from sklearn.experimental import enable_iterative_imputer  # Unlock an advanced feature in scikit-learn
from sklearn.impute import IterativeImputer                 # The smart gap-filler
from sklearn.linear_model import BayesianRidge              # The math model used to estimate missing values
```

**Stage 1 — Forward fill (simple):**

```python
df[feature_cols] = (
    df.groupby("iso3")[feature_cols]     # For each country separately...
    .transform(lambda g: g.ffill().bfill())  # Copy the value forward in time
)
# If Japan's life expectancy was 83.2 in 2010 but missing in 2011,
# ffill() copies 83.2 into 2011.
# bfill() works backwards for gaps at the start.
```

**Stage 2 — Smart imputation (complex):**

```python
imputer = IterativeImputer(
    estimator=BayesianRidge(),  # Uses a math formula (Bayesian Ridge Regression)
    max_iter=10,                # Do 10 passes over the data, improving estimates each time
    random_state=42,            # "42" = fixed seed so results are the same every run
)
df[feature_cols] = imputer.fit_transform(df[feature_cols])
# This looks at ALL other columns to estimate the missing one.
# e.g. "country X is missing GDP. But it has high HDI and high life expectancy,
#       so GDP is probably high too." — like a detective.
```

```python
for col in strictly_positive:
    df[col] = df[col].clip(lower=0)
# The imputer might estimate a negative life expectancy — that's impossible!
# clip(lower=0) forces all negative values to 0.

assert df[feature_cols].isnull().sum().sum() == 0  # CRASH the program if any NaN left
```

---

### `src/features.py` — Create Smart Columns

**Job:** From the raw cleaned data, engineer new columns that help the AI learn patterns.

```python
ROC_INDICATORS = ["air_quality_score", "gdp_per_capita_ppp", "life_expectancy", ...]
# Rate-of-change will be computed for these specific indicators
```

**Lag features:**

```python
for lag in (1, 2):           # Create lag-1 and lag-2 versions of every column
    lagged = (
        df.groupby("iso3")[raw_feature_cols]
        .shift(lag)          # "shift by 1" = move data 1 year into the future
                             # So row for year 2010 gets GDP from year 2009
        .rename(columns={c: f"{c}_lag{lag}" for c in raw_feature_cols})
        # Rename: "gdp_per_capita_ppp" → "gdp_per_capita_ppp_lag1"
    )
```

> This lets the AI learn: *"If a country had high GDP last year, it probably has high livability this year."*

**Rate of change features:**

```python
for col in ROC_INDICATORS:
    prev = df.groupby("iso3")[col].shift(1)        # Last year's value
    df[f"{col}_roc"] = ((df[col] - prev) / prev)  # % change = (new - old) / old
```

> This lets the AI learn: *"Countries whose GDP is growing fast tend to improve livability."*

**Interaction features:**

```python
interactions = {
    "interact_health_spend_x_life_exp": ("healthcare_spend_per_capita", "life_expectancy"),
    # Multiply healthcare spending × life expectancy
    # Countries that spend MORE on health AND have longer lives score differently
    # than countries that spend a lot but still have short lives
}
```

**One-hot encoding:**

```python
country_dummies = pd.get_dummies(df["iso3"], prefix="country", dtype=int)
# Converts the "iso3" text column into 49 binary (0/1) columns:
# "country_SGP", "country_JPN", etc.
# Singapore row → country_SGP=1, all others=0
# The AI can't read text, so we turn it into numbers
```

```python
df["year_since_2000"] = df["year"] - 2000
# Adds a column like: 2005 → 5, 2010 → 10, 2024 → 24
# Helps the AI understand "time is passing" rather than treating 2024 as a random number
```

---

### `src/target.py` — Calculate the Final Score (0–100)

**Job:** Combine all the indicators into one number per country per year.

```python
def minmax_normalize(series):
    lo, hi = series.min(), series.max()   # Find smallest and largest value
    if hi == lo:                           # Edge case: all values are identical
        return pd.Series(50.0, ...)        # Return 50 (middle) for everyone
    return (series - lo) / (hi - lo) * 100
    # Formula: (value - minimum) / (maximum - minimum) × 100
    # Squishes any range into 0–100
    # Lowest country gets 0, highest gets 100, rest in between
```

```python
for ind in pillar_def.get("positive", []):    # For "good" indicators (higher = better)
    components.append(norm[ind])               # Add the normalized score directly

for ind in pillar_def.get("negative", []):    # For "bad" indicators (lower = better)
    components.append(100 - norm[ind])         # FLIP it: 0 becomes 100, 100 becomes 0
    # Example: infant_mortality — the country with MOST deaths gets score 0,
    #          the country with LEAST deaths gets score 100
```

```python
pillar_scores[pillar_name] = pd.concat(components, axis=1).mean(axis=1)
# Average all indicator scores within a pillar
# Health pillar = average of (life_expectancy_score, uhc_score, hospital_beds_score, ...)
```

```python
composite = sum(
    pillar_scores[p] * weights.get(p, 0.0)   # Multiply each pillar by its weight
    for p in pillar_scores
)
# Final score = 0.30×Health + 0.25×Economy + 0.20×Environment + 0.15×Education + 0.10×Safety
```

---

### `src/tune.py` — Find the Best AI Settings

**Job:** Try 100+ different combinations of model settings. Keep the best one.

```python
import optuna   # Optuna = the "smart guesser" that finds the best settings
```

```python
def cv_rmse(model, X, y, n_splits):
    tscv = TimeSeriesSplit(n_splits=n_splits)   # Split time series into 5 folds
    rmses = []
    for train_idx, val_idx in tscv.split(X):    # For each fold...
        model.fit(X_tr, y_tr)                   # Train on older data
        preds = model.predict(X_val)             # Predict on newer data
        rmse = sqrt(mean_squared_error(y_val, preds))  # Measure error
        rmses.append(rmse)
    return mean(rmses)                           # Average error across all folds
# RMSE = Root Mean Squared Error = how far off predictions are on average
```

```python
def objective(trial):              # Optuna calls this function 100 times
    params = dict(
        n_estimators=trial.suggest_int("n_estimators", 100, 1000),
        # "Suggest a number of trees between 100 and 1000"
        max_depth=trial.suggest_int("max_depth", 2, 8),
        # "Suggest a tree depth between 2 and 8"
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        # "Suggest a learning rate (log scale = try more values near 0.01)"
    )
    model = XGBRegressor(**params)  # Build the model with these settings
    return cv_rmse(model, X, y, n_splits)  # Return the error — lower is better

study = optuna.create_study(direction="minimize")  # "We want to MINIMIZE error"
study.optimize(objective, n_trials=100)            # Run 100 experiments
```

```python
with open(out_path, "w") as f:
    yaml.dump(best, f)   # Save the best settings to best_params_xgb.yaml
```

---

### `src/train.py` — Train the Final AI Model

**Job:** Use the best settings found by `tune.py` to train the model on real data.

```python
train_mask = years <= train_end    # Data from 2000–2019 = TRAINING
test_mask = years >= test_start    # Data from 2020–2024 = TESTING (never seen during training)
```

```python
def verify_no_leakage(tscv, years_train):
    for i, (tr_idx, val_idx) in enumerate(tscv.split(years_train)):
        overlap = set(tr_years) & set(val_years)
        assert len(overlap) == 0    # CRASH if any year appears in both train AND validation
        assert max(tr_years) < min(val_years)  # CRASH if training data is from the FUTURE
        # "Data leakage" = cheating — using future data to predict the future
```

```python
def metrics(y_true, y_pred, label):
    rmse = sqrt(mean_squared_error(y_true, y_pred))  # Average prediction error
    r2 = r2_score(y_true, y_pred)    # R² = 1.0 means perfect, 0 means useless
    dir_acc = mean(sign(diff(y_true)) == sign(diff(y_pred)))
    # "Did we correctly predict whether the score went UP or DOWN?"
```

```python
if best_r2 < 0.85:          # If no single model is good enough (R² below 0.85)...
    stack = StackingRegressor(
        estimators=[("xgb", xgb_model), ("rf", rf_model)],  # Use BOTH models
        final_estimator=Ridge(),   # A 3rd simple model learns to combine their predictions
        cv=tscv,
    )
    # Like asking two experts for opinions, then a 3rd expert decides how to blend them
```

```python
joblib.dump(best_model, model_path)   # Save the trained model to disk as best_model.pkl
# joblib is like pickle but faster for large numpy arrays
```

```python
with mlflow.start_run(run_name=best_name):
    mlflow.log_params({"model": best_name, ...})  # Record what settings were used
    mlflow.log_metrics({"test_r2": ..., "test_rmse": ...})  # Record how well it performed
    # MLflow keeps a logbook of every training run — you can compare them later
```

---

### `src/explain.py` — Ask "WHY?"

**Job:** For each country, explain which indicators pushed the score up or down.

```python
explainer = shap.TreeExplainer(underlying)   # SHAP works with tree-based models
shap_values = explainer(X)                   # Compute a SHAP score for every feature, every row
sv_matrix = shap_values.values               # Shape: (n_countries × n_years, n_features)
# Each cell = "how much did this feature change the prediction?"
# Positive = pushed score UP, Negative = pushed score DOWN
```

```python
reconstruction = base_val + sv_matrix.sum(axis=1)
max_diff = abs(reconstruction - preds).max()
assert max_diff < 0.1   # Math check: base_value + sum(all SHAP values) must = prediction
```

```python
mean_abs = abs(sv_matrix).mean(axis=0)   # For each feature: average |SHAP| across all countries
# This tells us: "Which features matter MOST globally?"
ax.barh(top20["feature"], top20["mean_abs_shap"])   # Draw horizontal bar chart
fig.savefig(assets_dir / "shap_global.png")          # Save as image file
```

---

### `src/forecast.py` — Predict the Future

**Job:** For each country, fit a trend line to historical scores, then extend it 5 years into the future.

```python
FORECAST_HORIZON = 5    # Predict 5 years ahead
N_BOOTSTRAP = 200       # Run the random simulation 200 times (for confidence bands)
RNG_SEED = 42           # Fixed random seed = same results every run
```

```python
degree = 2 if len(train_df) >= 8 else 1
# If we have 8+ years of data: use a CURVE (degree 2 = parabola)
# If we have less data: use a STRAIGHT LINE (degree 1)
# More data = we can trust a more complex shape
```

```python
coeffs = np.polyfit(train_years, train_scores, degree)
# Fit a polynomial: find the line/curve that best fits the historical scores
yhat = np.polyval(coeffs, forecast_years)
# Apply those coefficients to future years to get predictions
```

```python
for _ in range(N_BOOTSTRAP):         # Do this 200 times:
    idx = rng.integers(0, n, size=n)  # Randomly resample years WITH replacement
    c = np.polyfit(all_years[idx], all_scores[idx], degree)  # Fit a trend on sample
    boot_preds.append(np.polyval(c, forecast_years))          # Record prediction

yhat_lower = np.percentile(boot_preds_arr, 2.5, axis=0)   # Bottom 2.5% of 200 runs
yhat_upper = np.percentile(boot_preds_arr, 97.5, axis=0)  # Top 97.5% of 200 runs
# The range between lower and upper = 95% confidence band
# "We're 95% sure the real score will land in this shaded zone"
```

```python
yhat = np.clip(yhat, 0, 100)   # A score can't be below 0 or above 100
```

---

## The `app/` Folder — The Website

### `app/app.py` — The Dashboard

```python
import streamlit as st     # Streamlit = turns Python into a web app with no HTML needed
import plotly.express as px  # Creates interactive charts

@st.cache_data             # Magic decorator: "run this function once, then remember the result"
def load_features():       # Next time it's called, return cached data instead of re-reading file
    return pd.read_csv(FEATURES_DIR / "features.csv")
```

The 5 tabs are built using:

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs(["World Map", "Country Analysis", ...])
with tab1:
    # draw the map
with tab2:
    # draw country charts
```

---

## The `data/` Folder

```
data/
├── raw/           ← Original downloads from World Bank, WHO, UNDP, Yale (untouched)
├── processed/
│   ├── panel_raw.csv      ← After harmonize.py: all sources merged, NaNs present
│   └── panel_imputed.csv  ← After impute.py: zero NaNs, ready for ML
├── features/
│   ├── features.csv       ← After features.py + target.py: lag/ROC columns + score added
│   ├── target_debug.csv   ← Just the pillar scores for debugging
│   ├── shap_values.csv    ← SHAP scores from explain.py
│   └── forecast_XXX.csv   ← One file per country from forecast.py
└── forecasts/
    └── forecasts.csv      ← All countries' forecasts in one file
```

---

## The `models/` Folder

```
models/
├── best_params_xgb.yaml   ← Best XGBoost settings found by tune.py
├── best_params_rf.yaml    ← Best Random Forest settings
└── best_model.pkl         ← The actual trained AI brain (binary file, created by train.py)
```

`.pkl` = "pickle" format — like a freeze-dried version of the Python model object.

---

## The `tests/` Folder

```python
# test_pipeline_units.py checks that functions work correctly:
def test_minmax_normalize():
    series = pd.Series([0, 50, 100])
    result = minmax_normalize(series)
    assert result.min() == 0    # Smallest value must become 0
    assert result.max() == 100  # Largest value must become 100

# test_data_quality.py checks that output files are correct:
def test_no_nulls_after_imputation():
    df = pd.read_csv("data/processed/panel_imputed.csv")
    assert df.isnull().sum().sum() == 0   # CRASH if any blank cells remain
```

---

## The `kestra/` Folder — The Alarm Clock

Kestra is like a **cron job manager** — it automatically re-runs the pipeline on a schedule (e.g., every year when new data is available).

```yaml
# kestra/flows/pipeline.yml
id: livability-pipeline
schedule:
  cron: "0 2 1 1 *"   # "Run at 2am on January 1st every year"
tasks:
  - id: collect
    type: io.kestra.plugin.scripts.python.Commands
    commands: ["python src/collect.py"]
  - id: harmonize
    dependsOn: [collect]     # Only run AFTER collect finishes
```

---

## The `terraform/` Folder — Renting Cloud Servers

Terraform writes instructions for Amazon AWS to set up cloud servers automatically.

```hcl
# ecr.tf — Creates a private Docker image registry on AWS
resource "aws_ecr_repository" "app" {
  name = "global-livability-ai"   # Name of the image store
}

# ecs.tf — Creates a cloud computer that runs the Docker container 24/7
resource "aws_ecs_service" "app" {
  desired_count = 1    # Run 1 copy of the container
}

# s3.tf — Creates an S3 bucket (like Google Drive for developers)
resource "aws_s3_bucket" "data_lake" {
  bucket = "gla-data-lake-dev"    # Store all data files here
}
```

---

## The Big Picture: How Everything Connects

```
config.yaml  (settings)
    ↓
collect.py   → data/raw/*.csv
    ↓
harmonize.py → panel_raw.csv
    ↓
impute.py    → panel_imputed.csv
    ↓
features.py  → features.csv  (+ lag/ROC columns)
    ↓
target.py    → features.csv  (+ target_score column)
    ↓
tune.py      → best_params_xgb.yaml, best_params_rf.yaml
    ↓
train.py     → best_model.pkl  (the trained brain)
    ↓
explain.py   → shap_*.png, shap_values.csv
    ↓
forecast.py  → forecast_*.csv, forecast_*.png
    ↓
app.py       → http://localhost:8501  (the website)
```

Every script reads `config.yaml` for settings and saves its output to disk, so each step can be re-run independently without starting over from scratch.
