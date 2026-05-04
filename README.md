
# 🌍 Global Livability AI

> **Predict how "good" life is in any country — and compare any two countries head-to-head.**
>
> This project downloads real data from 4 global databases, trains a machine-learning model on 180+ countries, gives each country a **Livability Score from 0–100**, and shows everything in a web dashboard.

---

## What Does This Project Do? (The Big Picture)

Imagine you have a giant spreadsheet with facts about every country in the world — things like:
- How long do people live?
- How clean is the air?
- How much does the government spend on schools?
- How fast is the internet?

We take all those numbers, feed them into a smart algorithm (XGBoost), and the algorithm figures out how to combine them into a single **score** — like a report card for how livable a country is.

Then you open a website and can ask:
- *"How does Norway compare to Thailand?"*
- *"Which 10 countries are the best to live in right now?"*
- *"Will Malaysia's score go up or down in 5 years?"*

---

## Folder Structure — What Lives Where

```
sea_livability_ai/
│
├── config.yaml          ← The master settings file (what data to collect, how to weight pillars)
├── requirements.txt     ← List of Python packages to install
├── Makefile             ← Shortcuts to run the full pipeline with one command
│
├── src/                 ← All the Python "worker" scripts (run in order)
│   ├── collect.py       ← Step 1: Download raw data from the internet
│   ├── harmonize.py     ← Step 2: Merge all data sources into one big table
│   ├── impute.py        ← Step 3: Fill in missing values (every country, every year)
│   ├── features.py      ← Step 4: Create extra smart columns the model can learn from
│   ├── target.py        ← Step 5: Calculate the final Livability Score for each country+year
│   ├── tune.py          ← Step 6: Find the best settings for the ML model (takes ~10 min)
│   ├── train.py         ← Step 7: Train the final ML model and save it
│   ├── explain.py       ← Step 8: Figure out WHY the model gave each country its score
│   └── forecast.py      ← Step 9: Predict future scores for the next 5 years
│
├── app/
│   └── app.py           ← The Streamlit web dashboard (what users actually see)
│
├── data/
│   ├── raw/             ← Fresh-downloaded CSVs (world_bank.csv, who_gho.csv, etc.)
│   ├── processed/       ← Cleaned merged table (panel_raw.csv, panel_imputed.csv)
│   └── features/        ← Final ML-ready table (features.csv) + SHAP values
│
└── models/              ← Saved trained model (best_model.pkl) + tuned parameters
```

---

## The Pipeline — Step by Step

Think of this as an assembly line in a factory. Each script does one job and passes its output to the next script.

```
collect → harmonize → impute → features → target → tune → train → explain → forecast → app
```

---

## Every File Explained

---

### `config.yaml` — The Brain / Settings Panel

**What it is:** A plain text settings file that every script reads before doing anything.

**Why it exists:** Instead of hardcoding numbers like `"start year = 2000"` in 9 different scripts, we write it once here and all scripts read it. Change one line → all scripts change behaviour.

**Key sections:**

| Section | What it controls |
|---|---|
| `scope: global` | Collect data for ALL World Bank member countries (~180), not just a region |
| `min_data_years: 5` | Only keep countries that have at least 5 years of data |
| `years: start/end` | Collect data from 2000 to 2024 |
| `sources:` | Which APIs to call, which indicators to download, URLs for Excel files |
| `pillar_weights:` | How much each life-category counts toward the final score (e.g. health = 30%) |
| `pillar_indicators:` | Which raw numbers belong to each life-category (pillar) |
| `temporal_split:` | Which years are for training (2000–2019) vs testing (2020–2024) |
| `optuna:` | How many experiments to try when searching for best model settings |

**Example — pillar weights:**
```yaml
pillar_weights:
  health:      0.30   # 30% of the final score
  economy:     0.25   # 25% of the final score
  environment: 0.20   # 20% of the final score
  education:   0.15   # 15%
  safety:      0.10   # 10%
```

---

### `requirements.txt` — The Shopping List

**What it is:** A list of Python packages (libraries) that need to be installed before running anything.

**How to use it:**
```bash
pip install -r requirements.txt
```

**Key packages and why we need them:**

| Package | What it does |
|---|---|
| `pandas` | The Swiss Army knife for tables. Every CSV is loaded as a pandas DataFrame |
| `numpy` | Fast math on big lists of numbers |
| `requests` | Downloads files from the internet (APIs, Excel files) |
| `scikit-learn` | Provides the IterativeImputer (for filling missing values) and model evaluation tools |
| `xgboost` | The main ML model — a very powerful "decision tree boosting" algorithm |
| `optuna` | Automatically finds the best model settings by trying hundreds of combinations |
| `shap` | Explains model decisions: "this country got 72/100 *because* of X, Y, Z" |
| `prophet` | Facebook's forecasting library — predicts future scores with confidence intervals |
| `streamlit` | Turns a Python script into a web app instantly |
| `plotly` | Interactive charts (zoom, hover, etc.) |
| `pyyaml` | Reads `config.yaml` files |
| `joblib` | Saves/loads trained ML models to disk |
| `openpyxl` | Reads `.xlsx` Excel files (UNDP and Yale EPI use Excel) |

---

### `Makefile` — The Remote Control

**What it is:** A shortcuts file. Instead of typing 9 long commands, you type one short word.

**How to use it** (Linux/Mac terminal or Git Bash):
```bash
make all        # Run the entire pipeline from scratch
make data       # Only download + clean data
make features   # Only rebuild features + target score
make train      # Only re-tune + re-train the model
make explain    # Only regenerate SHAP charts
make forecast   # Only regenerate forecasts
make app        # Launch the Streamlit dashboard
make clean      # Delete all generated files (start fresh)
```

> **Windows users:** Run each `python src/xxx.py` command manually, or use PowerShell with the `.venv` activated.

---

## `src/` — The Worker Scripts

---

### `src/collect.py` — Step 1: The Internet Shopper

**Job:** Go to 4 different websites, download data about every country in the world, and save it as CSV files.

**Where data comes from:**

#### 1. World Bank API
- **URL pattern:** `https://api.worldbank.org/v2/country/all/indicator/{code}`
- Downloads 13 indicators for **all** countries at once (one API call per indicator).
- **Why batch?** The old approach looped over 6 countries one by one. Now we ask for the whole world in one request — much faster.
- **Key helper — `_get_wb_countries()`:** Calls the World Bank's country registry to get a list of all real countries (filters out "aggregate" regions like "Sub-Saharan Africa" which are not real countries).
- Saves `data/raw/world_bank.csv` and `data/raw/country_names.csv`.

#### 2. UNDP Human Development Index (HDI)
- **Source:** An Excel file from the United Nations website.
- Downloads the `.xlsx`, finds the right sheet and header row automatically (it changes every year!).
- Tries to find an ISO3 column first (e.g. `"ISO3"`). If not found, uses the `_NAME_TO_ISO3` dictionary to convert country names like `"Viet Nam"` → `"VNM"`.
- Saves `data/raw/undp_hdi.csv`.

#### 3. WHO Global Health Observatory (GHO)
- **Source:** A REST API at `https://ghoapi.azureedge.net/api`.
- Downloads 3 health indicators (Universal Health Coverage index, financial hardship, TB incidence).
- No country filter — gets the whole world, then the ISO3 code filters out non-countries automatically.
- Saves `data/raw/who_gho.csv`.

#### 4. Yale Environmental Performance Index (EPI)
- **Source:** An Excel file from Yale University.
- Same approach as UNDP: find ISO3 column or fall back to the `_NAME_TO_ISO3` dictionary.
- Extracts: overall EPI score, air quality score, ecosystem vitality score, water/sanitation score.
- Saves `data/raw/yale_epi.csv`.

#### The `_NAME_TO_ISO3` Dictionary
This is a 120-entry lookup table that converts messy country names into the standard 3-letter country code:
```python
"Viet Nam"                          → "VNM"
"Korea (Republic of)"               → "KOR"
"Congo (Democratic Republic of the)" → "COD"
```
It is needed because UNDP and Yale write country names differently from each other and from the World Bank.

---

### `src/harmonize.py` — Step 2: The Organiser

**Job:** Take the 4 separate CSV files from Step 1 and merge them into one big, tidy table called `panel_raw.csv`.

**The key idea — the "grid":**
First, it builds a complete grid of every (country, year) pair that should exist:
```
THA 2000, THA 2001, THA 2002, ..., THA 2024
NOR 2000, NOR 2001, ..., NOR 2024
...180 countries × 25 years = 4,500 rows
```
Then it LEFT-JOINs each data source onto this grid. This guarantees that every country appears for every year — even if some values are missing (NaN). Those gaps get filled in Step 3.

**Why left join?** If WHO doesn't have data for a country in 2003, we still want that row to exist in our table (we'll fill it in next step). A left join keeps all rows from the grid even when there's no match.

**Deduplication:** WHO returns one row per gender (male/female/total). We collapse these to a single row by taking the average (`groupby + mean`).

**Output:** `data/processed/panel_raw.csv` — a table with ~4,500 rows and ~25 columns, but with lots of NaN gaps.

---

### `src/impute.py` — Step 3: The Gap Filler

**Job:** Fill in every single missing value so the ML model never sees a NaN.

**Why do we have missing values?**
- Yale EPI is published every 2 years (so odd years are missing)
- WHO does not have data for every country every year
- Small countries have patchy reporting

**Two-stage approach:**

**Stage 1 — Forward-fill within each country:**
```
Country THA, year 2002: air_quality = 48.0  ← real value
Country THA, year 2003: air_quality = NaN   ← gap
Country THA, year 2004: air_quality = NaN   ← gap
Country THA, year 2005: air_quality = 51.2  ← real value
```
After forward-fill (then backward-fill for leading gaps):
```
THA 2002: 48.0  (real)
THA 2003: 48.0  (copied from 2002)
THA 2004: 48.0  (copied)
THA 2005: 51.2  (real)
```
This is sensible — a country's air quality does not change drastically in one year.

**Stage 2 — IterativeImputer (the smart filler):**
For values that are still missing after forward-fill (e.g. countries with almost no data at all), it uses scikit-learn's `IterativeImputer` with a `BayesianRidge` model.

Think of it like this: "Singapore is missing its 2001 TB rate. But we know its GDP, HDI, and healthcare spending. Countries with similar GDP/HDI/healthcare tend to have TB rates around 4. So let's use 4."

It repeats this process 10 times, each time getting more accurate estimates.

**Final check:** An `assert` statement verifies zero NaN values remain before saving.

**Output:** `data/processed/panel_imputed.csv` — same ~4,500 rows, 0 NaN values.

---

### `src/features.py` — Step 4: The Feature Factory

**Job:** Take the clean imputed data and create **extra columns** that help the model learn patterns better.

**Why create extra features?** Raw data is good. But the model can learn much more from:
- "What was this country's GDP *last year*?" (lag feature)
- "How *fast* is GDP growing?" (rate of change)
- "Countries with both high education spend AND high HDI tend to score especially well" (interaction)

**What it creates:**

#### Lag Features (looking backward in time)
For every indicator, it creates 2 new columns:
- `gdp_per_capita_ppp_lag1` — last year's GDP
- `gdp_per_capita_ppp_lag2` — two years ago's GDP

This gives the model a sense of *trajectory* — is the country improving or declining?

#### Rate-of-Change (ROC) Features
For 6 key indicators, calculates the % change from last year:
```
air_quality_roc = (this_year - last_year) / last_year
```
A positive ROC means things are improving; negative means declining.

#### Interaction Features
Cross-multiplies related indicators to capture synergies:
- `healthcare_spend × life_expectancy` — richer healthcare countries live longer; this amplifies that signal
- `education_spend × hdi_score` — education investment × human development
- `co2_emissions × air_quality_score` — carbon + air pollution together

#### Country One-Hot Encoding
Converts the `iso3` column into dummy columns:
```
iso3="THA" → country_THA=1, country_NOR=0, country_DEU=0, ...
```
This lets the model learn "Thailand tends to score around 60" as a baseline.

#### Year Since 2000
Adds `year_since_2000 = year - 2000` as a simple trend feature.

**Output:** `data/features/features.csv` — same rows, but now ~300+ columns including all the engineered features.

---

### `src/target.py` — Step 5: The Scorekeeper

**Job:** Calculate the actual **Livability Score (0–100)** for every country and every year. This is the number the model will try to predict.

**The scoring formula — 4 steps:**

#### Step 1: Normalize each indicator to 0–100
```
normalized = (value - global_min) / (global_max - global_min) × 100
```
This puts all indicators on the same scale. A life expectancy of 83 years becomes ~95/100; a value of 52 years becomes ~10/100.

#### Step 2: Invert "lower is better" indicators
Some indicators are bad when high (e.g. infant mortality, homicide rate, CO2 emissions):
```
inverted_score = 100 - normalized_score
```
So a country with very low infant mortality gets a *high* score.

#### Step 3: Average within each pillar
```
health_score = average(life_expectancy_norm, infant_mortality_inverted,
                       healthcare_spend_norm, hospital_beds_norm)
```
The 5 pillars are: health, economy, environment, education, safety.

#### Step 4: Weighted sum across pillars
```
livability_score = (health_score × 0.30) + (economy_score × 0.25)
                 + (environment_score × 0.20) + (education_score × 0.15)
                 + (safety_score × 0.10)
```
The weights come from `config.yaml` and can be changed by the user in the dashboard sidebar.

**Sanity check:** After scoring, the script verifies that one of the known high-development countries (Norway, Singapore, Switzerland, Germany, etc.) comes out on top. If some obscure country wins, it logs a warning.

**Output:** Adds `target_score` and 5 `pillar_*` columns to `features.csv`. Also saves `target_debug.csv` with just the pillar breakdown for inspection.

---

### `src/tune.py` — Step 6: The Settings Searcher

**Job:** Automatically find the best hyperparameters (settings) for both XGBoost and Random Forest models.

**What are hyperparameters?** Imagine the ML model is a car engine. You can adjust:
- How many "trees" it builds (depth of analysis)
- How fast it learns (`learning_rate`)
- How much randomness to use (`subsample`)
- How harshly to penalise complexity (`reg_alpha`, `reg_lambda`)

Bad settings → the model memorises training data but fails on new countries.
Good settings → the model generalises well to unseen data.

**How Optuna works:**
Optuna is like a smart experiment manager. It tries 50–100 different combinations of settings, measures how well each combination performs on validation data, and zeroes in on the best combination.

**Validation strategy — TimeSeriesSplit:**
Normal cross-validation would be *cheating* for time-series data. If you train on 2015 data and validate on 2010 data, the model has "seen the future".

TimeSeriesSplit enforces that validation always comes *after* training:
```
Fold 1: Train 2000–2005, Validate 2006–2008
Fold 2: Train 2000–2008, Validate 2009–2011
Fold 3: Train 2000–2011, Validate 2012–2014
```

**Output:** `models/best_params_xgb.yaml` and `models/best_params_rf.yaml` — YAML files with the winning settings.

---

### `src/train.py` — Step 7: The Teacher

**Job:** Use the best settings from Step 6 to train the final model. Test it on data it has never seen (2020–2024). Save the best model.

**Train/test split:**
```
Training data:  years 2000–2019  (learning the patterns)
Test data:      years 2020–2024  (checking the predictions)
```
The model never sees 2020–2024 during training — this proves it can generalise.

**Stacking ensemble (automatic upgrade):**
If neither XGBoost nor Random Forest alone achieves R² > 0.85, the script automatically builds a **stacking ensemble** — it trains both models and then trains a third simple model (Ridge Regression) to combine their predictions. Usually this pushes R² above 0.90.

**Metrics logged:**

| Metric | What it means |
|---|---|
| RMSE | Average prediction error in score points. RMSE=2 means predictions are off by ~2 points on average |
| MAE | Similar to RMSE but less sensitive to big outliers |
| R² | How much of the variance the model explains. R²=0.95 means 95% of score differences are explained |
| DirAcc | Does the model correctly predict "going up" vs "going down"? |

**Leakage check:** Before training, the script verifies that no year appears in both training and validation folds. If it does, it crashes loudly — data leakage makes model results meaningless.

**Output:** `models/best_model.pkl` — the saved model. `models/feature_columns.txt` — the list of feature columns the model expects (needed by `explain.py` and `app.py`).

---

### `src/explain.py` — Step 8: The Explainer

**Job:** Figure out *why* the model gives each country its score. Which factors matter most?

**What is SHAP?**
SHAP (SHapley Additive exPlanations) comes from game theory. It answers: "Of this country's score of 72, how much came from its high GDP? From its clean air? From its good healthcare?"

Every feature gets a SHAP value for every prediction:
- Positive SHAP → this feature pushed the score up
- Negative SHAP → this feature pushed the score down
- Bigger absolute value → bigger impact on the score

**What it produces:**

| File | What it shows |
|---|---|
| `app/assets/shap_global.png` | Bar chart: which features matter most across all countries (mean absolute SHAP) |
| `app/assets/shap_{iso3}.png` | Waterfall chart: for one specific country, how each feature contributed to its score |
| `data/features/shap_values.csv` | Full table of all SHAP values — used by the dashboard for interactive filtering |

**Integrity check:** The script verifies that `base_value + sum(all_shap_values) ≈ prediction`. If this does not hold, something is wrong with the explainer.

**Which countries get a chart?** The top 30 countries by latest livability score.

---

### `src/forecast.py` — Step 9: The Fortune Teller

**Job:** Predict each country's livability score for the next 5 years beyond the last observed year.

**Method — Polynomial Trend + Bootstrap:**

Instead of using the ML model (which needs full feature data for future years that do not exist yet), this script fits a **polynomial curve** to each country's historical score trend:
- If a country has 8 or more years of data: use a degree-2 curve (can bend up or down)
- If fewer: use a degree-1 curve (straight line trend)

**Bootstrap confidence intervals:**
To show uncertainty, it runs 200 simulations:
1. Randomly resample the historical data with replacement
2. Fit a trend to each resample
3. Make a prediction for each future year
4. Take the 2.5th and 97.5th percentiles as the 95% confidence interval

This gives a band like "Thailand's score in 2029 will be between 58 and 67, most likely around 63."

**Holdout validation:**
To check the forecast is not total nonsense, it withholds 2022–2024 data, trains on data before 2022, and checks if the forecast comes close to reality.

**Output:** `data/features/forecast_{iso3}.csv` for every country with enough data, plus `app/assets/forecast_{iso3}.png` charts. Also saves a combined `data/forecasts/forecasts.csv`.

---

### `app/app.py` — The Dashboard

**Job:** A web app where users can explore all results visually. No coding needed.

**Launch it:**
```powershell
.venv\Scripts\streamlit.exe run app\app.py
```
Then open http://localhost:8501 in your browser.

**Sidebar controls:**

| Control | What it does |
|---|---|
| **Mode** radio button | Switch between "Single Country" deep-dive and "Compare Two Countries" |
| **Country A / B** dropdown | Pick any country in the world |
| **Year Range** slider | Filter data to a specific time period |
| **Pillar Weights** expander | Drag sliders to change how much health/economy/environment count — scores recalculate live |

**Tab 1 — World Map:**
- A full-world choropleth (colour map) showing every country's latest score
- Green = good livability, Red = low livability
- Hover over any country for its name, score, and rank
- Two tables below: Top 10 and Bottom 10 countries

**Tab 2 — Analysis:**

*Single Country mode:*
- 3 KPI cards: Score, Global Rank, Year-over-Year change
- Line chart of score over time
- Radar chart of 5 pillar scores
- Forecast chart (5 years ahead)
- SHAP bar chart (what drove this score)

*Compare Two Countries mode:*
- 4 KPI cards side by side (score + rank for each country)
- Overlapping line chart (both countries on same chart)
- Grouped bar chart comparing all 5 pillars
- Summary comparison table
- Two forecast charts side by side

**Tab 3 — Drivers:**
- Global SHAP importance chart (which features matter globally)
- Per-country SHAP breakdown (pick any country)
- Download button for the SHAP CSV

**Tab 4 — Data Explorer:**
- Full feature table, filterable to one country
- Download button for CSV

**Live score recalculation:** When the user moves the pillar weight sliders, the app instantly recalculates all scores without re-running any pipeline script. This is done by reading `panel_imputed.csv` directly and applying the weights in real time.

---

## How to Run the Full Pipeline

### One-time setup
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run the pipeline (in order)
```powershell
# Steps 1–3: Collect and clean data (~20–40 min for 180 countries)
python src/collect.py
python src/harmonize.py
python src/impute.py

# Steps 4–5: Build features and target scores
python src/features.py
python src/target.py

# Steps 6–7: Find best settings and train the model (~10–20 min)
python src/tune.py
python src/train.py

# Steps 8–9: Explain and forecast
python src/explain.py
python src/forecast.py

# Launch the dashboard
.venv\Scripts\streamlit.exe run app\app.py
```

---

## The Data Sources

| Source | What it provides | Format | Update frequency |
|---|---|---|---|
| **World Bank** | GDP, life expectancy, education spend, internet users, CO2, unemployment, etc. | REST API (JSON) | Annual |
| **UNDP HDI** | Human Development Index — composite of education, health, income | Excel file download | Annual |
| **WHO GHO** | Universal health coverage, tuberculosis rates, financial hardship from healthcare | REST API (OData/JSON) | Irregular |
| **Yale EPI** | Environmental Performance Index — air quality, ecosystem health, water/sanitation | Excel file download | Every 2 years |

---

## The 5 Livability Pillars

| Pillar | Weight | What it measures | Key indicators |
|---|---|---|---|
| **Health** | 30% | How healthy the population is | Life expectancy, infant mortality, healthcare spending, hospital beds, UHC coverage |
| **Economy** | 25% | How wealthy and stable | GDP per capita, GNI per capita, unemployment rate |
| **Environment** | 20% | How clean and sustainable | Air quality, ecosystem vitality, CO2 emissions, water/sanitation, electricity access |
| **Education** | 15% | Investment in learning | Education spending % of GDP, expected years of schooling, HDI |
| **Safety** | 10% | How safe people are | Homicide rate, TB incidence |

---

## Frequently Asked Questions

**Q: Can I add a new country?**
A: Run `python src/collect.py` — it automatically fetches all World Bank member countries. Any country with at least 5 years of data is included.

**Q: Can I change how much Health vs Economy matters?**
A: Yes, two ways: (1) Edit `config.yaml` and re-run the pipeline, or (2) drag the sliders in the app sidebar — scores update instantly without re-running anything.

**Q: Why does the model need "lag features"? Can't it just use current values?**
A: Current values alone make the model too short-sighted. Knowing *where a country came from* (last year's values) helps predict *where it is going*. A country with rapidly improving health scores is likely to keep improving, even if its current score is only average.

**Q: What is R² = 0.95?**
A: It means the model explains 95% of the variation in livability scores. If you plotted predicted vs actual scores, 95% of the pattern would be captured. An R² of 1.0 would be perfect. Anything above 0.85 is considered very good for this type of data.

**Q: Why use XGBoost instead of simple linear regression?**
A: Linear regression can only find straight-line relationships. XGBoost builds hundreds of decision trees that can capture complex non-linear patterns — like "healthcare spending only helps a lot once a country passes a certain GDP threshold". It is also naturally robust to outliers and works well when features are correlated.

**Q: Why is the forecast based on polynomial trends instead of the ML model?**
A: The ML model needs 300+ features to make a prediction. For future years (2025–2030), we do not have future values of `internet_users_lag1` or `gdp_roc` yet. Polynomial trend fitting only needs the historical score values — much simpler and still useful for showing likely trajectory.

## Quick Start

```bash
pip install -r requirements.txt
make data        # collect + harmonize + impute
make features    # lag/RoC/interaction features + composite target
make train       # Optuna HP tuning + XGBoost/RF training + SHAP
make forecast    # Prophet per-country forecasts
make app         # Launch Streamlit dashboard
```

## Pipeline Stages

| Stage | Script | Output |
|-------|--------|--------|
| Collect | `src/collect.py` | `data/raw/*.csv` |
| Harmonize | `src/harmonize.py` | `data/processed/panel_raw.csv` |
| Impute | `src/impute.py` | `data/processed/panel_imputed.csv` |
| Features | `src/features.py` | `data/features/features.csv` |
| Target | `src/target.py` | adds `target_score` column |
| Tune | `src/tune.py` | `models/best_params_*.yaml` |
| Train | `src/train.py` | `models/best_model.pkl` |
| Explain | `src/explain.py` | `app/assets/shap_*.png`, `data/features/shap_values.csv` |
| Forecast | `src/forecast.py` | `data/features/forecast_*.csv`, `app/assets/forecast_*.png` |
| Dashboard | `app/app.py` | Streamlit web app |

## Data Sources
- **World Bank** — 13 socio-economic indicators via `wbdata` API
- **UNDP HDI** — Human Development Index + education metrics
- **WHO GHO** — UHC index, TB incidence
- **Yale EPI** — Environmental Performance Index

## Model
- XGBoost + RandomForest with Optuna hyperparameter tuning (100 + 50 trials)
- Temporal validation: train 2000–2019, test 2020–2024, `TimeSeriesSplit(n_splits=5)`
- Stacking ensemble if best single-model R² < 0.85
- SHAP TreeExplainer for global + per-country explainability

## Composite Target (0–100)
| Pillar | Weight | Indicators |
|--------|--------|-----------|
| Health | 30% | Life expectancy, UHC, healthcare spend, infant mortality |
| Economy | 25% | GDP PPP, GNI, unemployment |
| Education | 15% | Schooling years, education spend |
| Environment | 20% | EPI, air quality, CO₂ |
| Safety/Infra | 10% | Homicide rate, electricity, internet |

## Deployment
Push to GitHub → connect to [Streamlit Community Cloud](https://streamlit.io/cloud) → select `app/app.py`.
