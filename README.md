# SE Asia Livability AI

Predict, compare, and forecast livability scores (0 to 100) for 6 Southeast Asian countries using real-world data and machine learning.

**Countries covered:** Thailand, Malaysia, Viet Nam, Indonesia, Philippines, Singapore

---

## Quick Start

```powershell
# 1 - Install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2 - Run the full pipeline (run each script in this order)
python src/collect.py       # Download raw data from World Bank, WHO, UNDP, Yale EPI
python src/harmonize.py     # Merge all sources into one panel
python src/impute.py        # Fill missing values
python src/features.py      # Build machine learning features
python src/target.py        # Calculate livability scores and pillar sub-scores
python src/tune.py          # Find the best model settings (takes about 10 minutes)
python src/train.py         # Train the final XGBoost / Random Forest model
python src/explain.py       # Generate SHAP feature importance charts
python src/forecast.py      # Forecast scores for the next 5 years

# 3 - Launch the dashboard
.venv\Scripts\streamlit.exe run app\app.py
# Then open http://localhost:8501 in your browser
```

On Linux or Git Bash you can also run:
```bash
make data && make features && make train && make forecast && make app
```

---

## Using the Dashboard

Open **http://localhost:8501** in your browser after starting the app.

The dashboard has five tabs across the top and a settings panel on the left.

---

### Sidebar Settings

| Control | What it does |
|---|---|
| **Year Range** slider | Filters all charts to show only a chosen time window, for example 2010 to 2024 |
| **Adjust Pillar Weights** expander | Drag the sliders to change how much each pillar (Health, Economy, etc.) contributes to the overall score. Charts update instantly with no need to re-run the pipeline. |

---

### Tab 1 - World Map

**What you see:**
- A colour-coded map of Southeast Asia showing each country's latest livability score
- Green means a higher score and red means a lower score
- Hover over any country to see its name, score out of 100, and rank
- Two tables below: the top-ranked countries and the bottom-ranked countries

**How to use it:**
1. Drag the Year Range slider to see how the map changes over time
2. Open Pillar Weights and move the sliders to re-rank countries based on what matters most to you, for example set Environment to 100% to find the greenest country

---

### Tab 2 - Country Analysis

**What you see:**
- A dropdown menu to pick any country
- Three summary cards showing the overall score, regional rank, and year-on-year change
- A line chart of the score from 2000 to 2024
- A radar (spider) chart breaking the score into 5 pillars: Health, Economy, Environment, Education, and Safety
- A forecast chart showing the predicted score for the next 5 years with a confidence band
- A SHAP bar chart showing which indicators are pushing the score up or down

**How to use it:**
1. Select a country from the dropdown at the top of the tab
2. Read the three summary cards for a quick snapshot
3. Use the radar chart to spot which pillar is strongest or weakest
4. Check the forecast chart to see whether the score is expected to rise or fall
5. Read the SHAP chart to understand the specific indicators behind the score

---

### Tab 3 - Compare Countries

**What you see:**
- Two dropdown menus, one for Country A and one for Country B
- Four summary cards showing the score and rank for each country side by side
- A line chart with both countries on the same axis so you can see crossovers and trends
- A grouped bar chart comparing all 5 pillars for both countries at once
- A summary table with every metric for easy reading
- Two side-by-side forecast charts, one per country

**How to use it:**
1. Choose Country A from the first dropdown and Country B from the second
2. Look at the grouped bar chart to see which pillars explain the gap between the two countries
3. Use the overlapping line chart to see whether the gap between them is growing or closing
4. Check the forecast charts to see which country is expected to improve faster

---

### Tab 4 - Forecast

**What you see:**
- A multi-select dropdown to choose any number of countries at once
- Section 1: Historical scores (actual recorded data) for all selected countries on one chart
- Section 2: Predicted scores for the next 5 years with a shaded 95% confidence band per country
- Section 3: A ranked table for any future year you choose with the slider
- Section 4: A bar chart showing the predicted score change for each country compared to today (green = improving, red = declining)

**How to use it:**
1. Use the multi-select dropdown to pick the countries you want to compare
2. Read the historical chart to understand the starting trend
3. Look at the forecast overlay to see which country is predicted to pull ahead
4. Drag the Year slider to inspect the predicted rankings at a specific future year
5. Read the score change chart to see which countries are expected to improve the most

---

### Tab 5 - Data Explorer

**What you see:**
- A dropdown to filter the data to one country or view all countries together
- A table showing every country, year, and indicator used by the model
- A Download as CSV button

**How to use it:**
1. Select a country from the dropdown to narrow the table
2. Scroll right to see all indicators such as GDP, life expectancy, HDI, air quality, and more
3. Click Download as CSV to export the data for your own analysis

---

## Pipeline Stages

| Step | Script | Input | Output |
|---|---|---|---|
| 1 | `src/collect.py` | APIs and Excel files | `data/raw/*.csv` |
| 2 | `src/harmonize.py` | `data/raw/*.csv` | `data/processed/panel_raw.csv` |
| 3 | `src/impute.py` | `panel_raw.csv` | `panel_imputed.csv` |
| 4 | `src/features.py` | `panel_imputed.csv` | `data/features/features.csv` |
| 5 | `src/target.py` | `features.csv` | Adds `target_score` and pillar columns |
| 6 | `src/tune.py` | `features.csv` | `models/best_params_*.yaml` |
| 7 | `src/train.py` | `features.csv` and params | `models/best_model.pkl` |
| 8 | `src/explain.py` | Model and features | `app/assets/shap_*.png`, `shap_values.csv` |
| 9 | `src/forecast.py` | `features.csv` | `data/forecasts/forecasts.csv`, `app/assets/forecast_*.png` |
| 10 | `app/app.py` | All of the above | Streamlit dashboard at localhost:8501 |

---

## Data Sources

| Source | What it provides |
|---|---|
| **World Bank** | GDP, life expectancy, unemployment, CO2 emissions, internet users, hospital beds, and more |
| **UNDP HDI** | Human Development Index and years of schooling |
| **WHO GHO** | Universal Health Coverage index, TB incidence, financial hardship |
| **Yale EPI** | Environmental Performance Index, air quality, ecosystem vitality, water and sanitation |

---

## Composite Score (0 to 100)

| Pillar | Default Weight | Key Indicators |
|---|---|---|
| Health | 30% | Life expectancy, infant mortality, UHC coverage, healthcare spending |
| Economy | 25% | GDP per capita (PPP), GNI per capita, unemployment rate |
| Environment | 20% | EPI score, air quality, CO2 emissions per capita |
| Education | 15% | HDI score, mean years of schooling, education spending |
| Safety and Infrastructure | 10% | Homicide rate, internet access, electricity access |

Pillar weights can be changed live in the dashboard sidebar. No re-run is needed.

---

## Model

- **Algorithm:** XGBoost and Random Forest with Optuna hyperparameter tuning (100 trials for XGBoost, 50 for Random Forest)
- **Validation:** TimeSeriesSplit with 5 folds so training data always comes before validation data
- **Train and test split:** 2000 to 2019 for training, 2020 to 2024 held out for testing
- **Ensemble:** If the best single model scores below R-squared of 0.85, a stacking ensemble (XGBoost plus Random Forest into a Ridge meta-model) is used
- **Explainability:** SHAP TreeExplainer for global and per-country feature importance
- **Forecasting:** Polynomial trend (degree 1 or 2 depending on data length) with 200-sample bootstrap confidence intervals

---

## Deployment

Push to GitHub and connect to [Streamlit Community Cloud](https://streamlit.io/cloud), then select `app/app.py` as the entry point.

---

## Adding or Removing Countries

Edit `config.yaml` to add more ISO3 country codes:

```yaml
scope: sea
countries:
  THA: Thailand
  MYS: Malaysia
  VNM: Viet Nam
  IDN: Indonesia
  PHL: Philippines
  SGP: Singapore
  # Add more countries here, for example:
  # MMR: Myanmar
  # KHM: Cambodia
```

Then re-run the full pipeline starting from `src/collect.py`.

To expand to all countries worldwide, change `scope: sea` to `scope: global` and remove the `countries:` block.
