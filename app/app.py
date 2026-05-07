"""
app/app.py
==========
Streamlit dashboard -- SE Asia Livability AI

Tabs:
  1. World Map        -- choropleth of latest livability scores
  2. Country Analysis -- deep-dive for a single selected country
  3. Compare Countries -- side-by-side comparison (two dropdown menus)
  4. Forecast         -- multi-country forecast with dropdown selector
  5. Data Explorer    -- raw feature matrix, downloadable CSV
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"
ASSETS_DIR = ROOT / "app" / "assets"
FEATURES_DIR = ROOT / "data" / "features"
RAW_DIR = ROOT / "data" / "raw"

# ---------------------------------------------------------------------------
# Data loaders (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


@st.cache_data
def load_country_names() -> dict[str, str]:
    """Return {iso3: display_name}. Falls back to built-in SEA dict if CSV missing."""
    p = RAW_DIR / "country_names.csv"
    if p.exists():
        df = pd.read_csv(p)
        return dict(zip(df["iso3"], df["country_name"]))
    return {
        "THA": "Thailand",
        "MYS": "Malaysia",
        "VNM": "Viet Nam",
        "IDN": "Indonesia",
        "PHL": "Philippines",
        "SGP": "Singapore",
    }


@st.cache_data
def load_features() -> pd.DataFrame:
    return pd.read_csv(FEATURES_DIR / "features.csv")


@st.cache_data
def load_shap_values() -> pd.DataFrame | None:
    p = FEATURES_DIR / "shap_values.csv"
    return pd.read_csv(p) if p.exists() else None


@st.cache_data
def load_forecasts() -> pd.DataFrame | None:
    p = ROOT / "data" / "forecasts" / "forecasts.csv"
    return pd.read_csv(p) if p.exists() else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def compute_live_scores(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Re-score every (iso3, year) row using the custom pillar weights."""
    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    total_w = sum(weights.get(c, 0.0) for c in pillar_cols) or 1.0
    score = sum(
        df[c].fillna(df[c].median()).clip(0, 100) * weights.get(c, 0.0) / total_w
        for c in pillar_cols
    )
    df2 = df.copy()
    df2["target_score"] = score
    return df2


def _rank_latest(df: pd.DataFrame, country_names: dict) -> pd.DataFrame:
    latest = df["year"].max()
    sub = (
        df[df["year"] == latest]
        .sort_values("target_score", ascending=False)
        .reset_index(drop=True)
    )
    sub["rank"] = sub.index + 1
    sub["country"] = sub["iso3"].map(country_names).fillna(sub["iso3"])
    return sub


def _country_dropdown(label: str, iso_list: list[str], country_names: dict,
                      default_isos: list[str], key: str) -> str:
    """Render a selectbox and return the chosen ISO3 code."""
    options = [f"{country_names.get(i, i)} ({i})" for i in iso_list]
    default_idx = 0
    for pref in default_isos:
        if pref in iso_list:
            default_idx = iso_list.index(pref)
            break
    chosen_label = st.selectbox(label, options, index=default_idx, key=key)
    # Extract ISO from the "Name (ISO)" format
    return chosen_label.split("(")[-1].rstrip(")")


# ---------------------------------------------------------------------------
# Tab renderers
# ---------------------------------------------------------------------------

def render_map(df: pd.DataFrame, country_names: dict) -> None:
    st.subheader("Livability Scores -- Latest Year")
    st.markdown(
        "The map shows each country's composite livability score (0 = worst, 100 = best). "
        "Hover over a country to see its exact score and rank."
    )

    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()
    latest["country"] = latest["iso3"].map(country_names).fillna(latest["iso3"])
    latest = latest.sort_values("target_score", ascending=False).reset_index(drop=True)
    latest["rank"] = latest.index + 1

    fig_map = px.choropleth(
        latest,
        locations="iso3",
        color="target_score",
        hover_name="country",
        hover_data={"target_score": ":.1f", "rank": True, "iso3": False},
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        labels={"target_score": "Livability Score"},
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Score (0-100)"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.markdown("### Top Countries")
    c1.dataframe(
        latest[["rank", "country", "target_score"]]
        .rename(columns={"rank": "Rank", "country": "Country", "target_score": "Score"})
        .head(10),
        use_container_width=True,
        hide_index=True,
    )
    c2.markdown("### Bottom Countries")
    c2.dataframe(
        latest[["rank", "country", "target_score"]]
        .rename(columns={"rank": "Rank", "country": "Country", "target_score": "Score"})
        .tail(10)
        .sort_values("Rank", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


def render_single(df: pd.DataFrame, fcast: pd.DataFrame | None,
                  shap_df: pd.DataFrame | None, country_names: dict,
                  iso_list: list[str]) -> None:
    st.markdown("Select a country from the dropdown below to see its full livability profile.")

    iso3 = _country_dropdown(
        "Select a country", iso_list, country_names,
        default_isos=["SGP", "THA"], key="single_sel",
    )

    cname = country_names.get(iso3, iso3)
    ranked = _rank_latest(df, country_names)
    latest_year = df["year"].max()
    score_row = df[(df["iso3"] == iso3) & (df["year"] == latest_year)]
    rank_row = ranked[ranked["iso3"] == iso3]
    score = score_row["target_score"].values[0] if len(score_row) else float("nan")
    rank = rank_row["rank"].values[0] if len(rank_row) else "-"
    n_countries = len(ranked)

    st.markdown(f"## {cname}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Livability Score", f"{score:.1f} / 100")
    col2.metric("Regional Rank", f"#{rank} of {n_countries}")
    country_ts = df[df["iso3"] == iso3].sort_values("year")
    if len(country_ts) >= 2:
        trend = country_ts["target_score"].iloc[-1] - country_ts["target_score"].iloc[-2]
        col3.metric("Year-on-Year Change", f"{trend:+.2f} pts")

    st.markdown("---")
    st.subheader("Livability Score Over Time")
    fig_ts = px.line(
        country_ts, x="year", y="target_score", markers=True,
        labels={"target_score": "Livability Score", "year": "Year"},
    )
    fig_ts.update_layout(height=300)
    st.plotly_chart(fig_ts, use_container_width=True)

    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    if pillar_cols and len(score_row):
        st.subheader("Pillar Breakdown")
        st.markdown("Radar chart showing how this country scores across each livability pillar.")
        vals = [float(score_row[c].values[0]) for c in pillar_cols]
        labels = [c.replace("_score", "").replace("_", " ").title() for c in pillar_cols]
        fig_radar = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=labels + [labels[0]],
            fill="toself", name=cname,
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(range=[0, 100])),
            title=f"Pillar Scores -- {cname}",
            height=420,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    if fcast is not None:
        fc = fcast[fcast["iso3"] == iso3]
        future_fc = fc[fc["year"] > latest_year] if len(fc) else fc
        if len(future_fc):
            st.subheader("Forecast (Next 5 Years)")
            st.markdown(
                "The shaded band shows the 95% confidence interval. "
                "Scores are modelled using a polynomial trend fitted to historical data."
            )
            fig_fc = px.line(
                future_fc, x="year", y="yhat",
                error_y_minus="yhat_lower", error_y="yhat_upper",
                labels={"yhat": "Predicted Score", "year": "Year"},
            )
            fig_fc.update_layout(height=300)
            st.plotly_chart(fig_fc, use_container_width=True)

    if shap_df is not None and "iso3" in shap_df.columns:
        shap_c = shap_df[shap_df["iso3"] == iso3]
        if len(shap_c):
            st.subheader("What Drives This Country's Score?")
            st.markdown(
                "SHAP values show how much each feature pushes the score up (+) or down (-)."
            )
            feat_cols = [c for c in shap_c.columns if c not in ("iso3", "year")]
            means = shap_c[feat_cols].mean().sort_values(key=abs, ascending=False).head(15)
            fig_shap = px.bar(
                x=means.values, y=means.index, orientation="h",
                labels={"x": "Mean SHAP Value", "y": "Feature"},
                title=f"Top Feature Drivers -- {cname}",
            )
            fig_shap.update_layout(height=400)
            st.plotly_chart(fig_shap, use_container_width=True)


def render_compare(df: pd.DataFrame, fcast: pd.DataFrame | None,
                   country_names: dict, iso_list: list[str]) -> None:
    st.markdown(
        "Use the two dropdowns below to pick any two countries. "
        "Charts and tables update automatically."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        iso_a = _country_dropdown(
            "Country A", iso_list, country_names,
            default_isos=["SGP", "THA"], key="cmp_a",
        )
    with col_b:
        iso_b = _country_dropdown(
            "Country B", iso_list, country_names,
            default_isos=["MYS", "VNM"], key="cmp_b",
        )

    if iso_a == iso_b:
        st.warning("Please select two different countries to compare.")
        return

    name_a = country_names.get(iso_a, iso_a)
    name_b = country_names.get(iso_b, iso_b)
    ranked = _rank_latest(df, country_names)
    latest_year = df["year"].max()
    n_countries = len(ranked)

    def _get(iso, col):
        row = ranked[ranked["iso3"] == iso]
        return row[col].values[0] if len(row) else "-"

    score_a = _get(iso_a, "target_score")
    score_b = _get(iso_b, "target_score")
    rank_a = _get(iso_a, "rank")
    rank_b = _get(iso_b, "rank")

    st.markdown("---")
    st.subheader("Overall Scores")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric(f"{name_a} -- Score", f"{score_a:.1f}" if isinstance(score_a, float) else score_a)
    mc2.metric(f"{name_a} -- Rank", f"#{rank_a} of {n_countries}")
    mc3.metric(f"{name_b} -- Score", f"{score_b:.1f}" if isinstance(score_b, float) else score_b)
    mc4.metric(f"{name_b} -- Rank", f"#{rank_b} of {n_countries}")

    st.markdown("---")
    st.subheader("Livability Score Over Time")
    ts_a = df[df["iso3"] == iso_a][["year", "target_score"]].assign(country=name_a)
    ts_b = df[df["iso3"] == iso_b][["year", "target_score"]].assign(country=name_b)
    fig_ts = px.line(
        pd.concat([ts_a, ts_b]), x="year", y="target_score", color="country",
        markers=True,
        labels={"target_score": "Livability Score", "year": "Year", "country": "Country"},
    )
    fig_ts.update_layout(height=340)
    st.plotly_chart(fig_ts, use_container_width=True)

    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    if pillar_cols:
        st.subheader("Pillar-by-Pillar Comparison")
        row_a = df[(df["iso3"] == iso_a) & (df["year"] == latest_year)]
        row_b = df[(df["iso3"] == iso_b) & (df["year"] == latest_year)]
        pillar_labels = [c.replace("_score", "").replace("_", " ").title() for c in pillar_cols]
        vals_a = [float(row_a[c].values[0]) if len(row_a) else 0.0 for c in pillar_cols]
        vals_b = [float(row_b[c].values[0]) if len(row_b) else 0.0 for c in pillar_cols]

        fig_bars = go.Figure([
            go.Bar(name=name_a, x=pillar_labels, y=vals_a),
            go.Bar(name=name_b, x=pillar_labels, y=vals_b),
        ])
        fig_bars.update_layout(barmode="group", height=380, yaxis_title="Score (0-100)")
        st.plotly_chart(fig_bars, use_container_width=True)

        st.subheader("Summary Table")
        metrics = {"Metric": ["Overall Score", "Regional Rank"] + pillar_labels}
        metrics[name_a] = (
            [f"{score_a:.1f}", f"#{rank_a}"] + [f"{v:.1f}" for v in vals_a]
        )
        metrics[name_b] = (
            [f"{score_b:.1f}", f"#{rank_b}"] + [f"{v:.1f}" for v in vals_b]
        )
        st.dataframe(pd.DataFrame(metrics), use_container_width=True, hide_index=True)

    if fcast is not None:
        fc_a = fcast[fcast["iso3"] == iso_a]
        fc_b = fcast[fcast["iso3"] == iso_b]
        future_a = fc_a[fc_a["year"] > latest_year] if len(fc_a) else fc_a
        future_b = fc_b[fc_b["year"] > latest_year] if len(fc_b) else fc_b
        if len(future_a) or len(future_b):
            st.markdown("---")
            st.subheader("Forecast Comparison (Next 5 Years)")
            st.markdown("Side-by-side forecast with 95% confidence band for each country.")
            fc1, fc2 = st.columns(2)
            for col, fc_sub, name in [(fc1, future_a, name_a), (fc2, future_b, name_b)]:
                if len(fc_sub):
                    fig = px.line(
                        fc_sub, x="year", y="yhat",
                        error_y_minus="yhat_lower", error_y="yhat_upper",
                        title=name,
                        labels={"yhat": "Predicted Score", "year": "Year"},
                    )
                    fig.update_layout(height=280)
                    col.plotly_chart(fig, use_container_width=True)


def render_forecast(df: pd.DataFrame, fcast: pd.DataFrame | None,
                    country_names: dict, iso_list: list[str]) -> None:
    st.markdown(
        "Select one or more countries from the dropdown below to compare their "
        "projected livability scores through to 2029."
    )

    # Country multiselect dropdown
    chosen_isos = st.multiselect(
        "Select countries to include in the forecast",
        options=iso_list,
        default=iso_list,
        format_func=lambda i: f"{country_names.get(i, i)} ({i})",
        key="fc_sel",
    )
    if not chosen_isos:
        st.info("Please select at least one country from the dropdown above.")
        return

    # Section 1: Historical scores
    st.markdown("---")
    st.subheader("Section 1 -- Historical Scores (Observed Data)")
    st.markdown(
        "This chart shows the actual recorded livability scores from 2000 onwards."
    )
    hist_frames = []
    for iso in chosen_isos:
        sub = df[df["iso3"] == iso][["year", "target_score"]].copy()
        sub["Country"] = country_names.get(iso, iso)
        hist_frames.append(sub)
    if hist_frames:
        fig_hist = px.line(
            pd.concat(hist_frames), x="year", y="target_score", color="Country",
            markers=True,
            labels={"target_score": "Livability Score", "year": "Year"},
        )
        fig_hist.update_layout(height=360, legend_title_text="Country")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Section 2: Forecast overlay
    st.markdown("---")
    st.subheader("Section 2 -- Predicted Scores (Next 5 Years)")
    st.markdown(
        "Each line is the model's predicted score. "
        "The shaded band is the 95% confidence interval -- the likely range the score will fall in."
    )

    if fcast is None:
        st.warning(
            "Forecast data not found. "
            "Run the command: python src/forecast.py"
        )
        return

    latest_year = df["year"].max()
    fc_frames = []
    for iso in chosen_isos:
        fc = fcast[fcast["iso3"] == iso].copy()
        if len(fc):
            fc["Country"] = country_names.get(iso, iso)
            fc_frames.append(fc)

    if not fc_frames:
        st.info("No forecast data available for the selected countries.")
        return

    fc_all = pd.concat(fc_frames)
    future_all = fc_all[fc_all["year"] > latest_year]

    # Overlay chart with confidence bands
    fig_fc = go.Figure()
    palette = px.colors.qualitative.Safe
    for idx, iso in enumerate(chosen_isos):
        fc_iso = fcast[fcast["iso3"] == iso]
        future_iso = fc_iso[fc_iso["year"] > latest_year]
        if not len(future_iso):
            continue
        cname = country_names.get(iso, iso)
        colour = palette[idx % len(palette)]
        fig_fc.add_trace(go.Scatter(
            x=future_iso["year"], y=future_iso["yhat"],
            mode="lines+markers", name=cname,
            line=dict(color=colour, width=2),
        ))
        fig_fc.add_trace(go.Scatter(
            x=pd.concat([future_iso["year"], future_iso["year"].iloc[::-1]]),
            y=pd.concat([future_iso["yhat_upper"], future_iso["yhat_lower"].iloc[::-1]]),
            fill="toself", fillcolor=colour,
            opacity=0.15, line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, name=f"{cname} confidence band",
        ))
    fig_fc.update_layout(
        height=420,
        xaxis_title="Year",
        yaxis_title="Predicted Livability Score (0 - 100)",
        legend_title_text="Country",
        yaxis=dict(range=[0, 100]),
    )
    st.plotly_chart(fig_fc, use_container_width=True)

    # Section 3: Ranked table for a chosen year
    st.markdown("---")
    st.subheader("Section 3 -- Predicted Rankings")
    st.markdown(
        "Use the slider to pick a future year and see the predicted ranking table "
        "for all selected countries."
    )

    if not len(future_all):
        st.info("Forecast data does not extend beyond the latest observed year.")
        return

    future_years = sorted(future_all["year"].unique())
    sel_year = st.select_slider(
        "Choose a future year to inspect",
        options=[int(y) for y in future_years],
        value=int(future_years[-1]),
    )
    yr_fc = (
        future_all[future_all["year"] == sel_year]
        .sort_values("yhat", ascending=False)
        .reset_index(drop=True)
        .copy()
    )
    yr_fc["Rank"] = yr_fc.index + 1
    yr_fc["Country"] = yr_fc["Country"]
    yr_fc["Predicted Score"] = yr_fc["yhat"].round(1)
    yr_fc["Lower Bound (95%)"] = yr_fc["yhat_lower"].round(1)
    yr_fc["Upper Bound (95%)"] = yr_fc["yhat_upper"].round(1)
    st.dataframe(
        yr_fc[["Rank", "Country", "Predicted Score", "Lower Bound (95%)", "Upper Bound (95%)"]],
        use_container_width=True,
        hide_index=True,
    )

    # Section 4: Score change bar chart
    st.markdown("---")
    st.subheader(f"Section 4 -- Score Change: Now vs {sel_year}")
    st.markdown(
        "Green bars mean the country is predicted to improve. "
        "Red bars mean the score is expected to fall."
    )

    today_scores = (
        df[df["year"] == latest_year][["iso3", "target_score"]]
        .set_index("iso3")["target_score"]
    )
    iso_lookup = {
        fc_all[fc_all["iso3"] == iso]["Country"].iloc[0]: iso
        for iso in chosen_isos
        if len(fc_all[fc_all["iso3"] == iso])
    }
    delta_rows = []
    for _, row in yr_fc.iterrows():
        iso = iso_lookup.get(row["Country"], "")
        today = today_scores.get(iso, float("nan"))
        delta_rows.append({
            "Country": row["Country"],
            "Score Today": round(today, 1),
            f"Score in {sel_year}": row["Predicted Score"],
            "Change": round(row["Predicted Score"] - today, 1),
        })
    delta_df = pd.DataFrame(delta_rows).sort_values("Change", ascending=False)

    fig_delta = px.bar(
        delta_df, x="Country", y="Change", color="Change",
        color_continuous_scale=["#d73027", "#fee08b", "#1a9850"],
        range_color=[-20, 20],
        labels={"Change": "Score Change"},
        text="Change",
    )
    fig_delta.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_delta.update_traces(texttemplate="%{text:+.1f}", textposition="outside")
    fig_delta.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(fig_delta, use_container_width=True)

    st.dataframe(delta_df, use_container_width=True, hide_index=True)


def render_data_explorer(df: pd.DataFrame, country_names: dict,
                         iso_list: list[str]) -> None:
    st.markdown("Browse and download the full feature matrix used to train the model.")

    filter_country = st.selectbox(
        "Filter by country (or leave on 'All Countries' to see everything)",
        options=["All Countries"] + [f"{country_names.get(i, i)} ({i})" for i in iso_list],
        key="data_exp_sel",
    )

    show_df = df.copy()
    if filter_country != "All Countries":
        iso_filter = filter_country.split("(")[-1].rstrip(")")
        show_df = show_df[show_df["iso3"] == iso_filter]

    show_df = show_df.copy()
    show_df.insert(0, "Country", show_df["iso3"].map(country_names).fillna(show_df["iso3"]))

    st.markdown(f"Showing **{len(show_df):,}** rows.")
    st.dataframe(show_df, use_container_width=True)
    st.download_button(
        label="Download as CSV",
        data=show_df.to_csv(index=False).encode(),
        file_name="livability_features.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="SE Asia Livability AI",
        page_icon="\U0001f30f",
        layout="wide",
    )
    st.title("\U0001f30f SE Asia Livability AI")
    st.markdown(
        "An AI-powered dashboard tracking and forecasting quality of life across "
        "Southeast Asia using health, economy, education, environment, and infrastructure data."
    )

    cfg = load_config()
    country_names = load_country_names()

    feat_path = FEATURES_DIR / "features.csv"
    if not feat_path.exists():
        st.error(
            "No feature data found. Run the pipeline first:\n\n"
            "```\npython src/collect.py\npython src/harmonize.py\n"
            "python src/impute.py\npython src/features.py\npython src/target.py\n```"
        )
        return

    df_raw = load_features()
    pillar_w_cfg: dict = cfg.get("pillar_weights", {})

    # ---- Sidebar -----------------------------------------------------------
    st.sidebar.header("Settings")

    all_iso = sorted(df_raw["iso3"].unique())
    all_opts = sorted(
        [(iso, country_names.get(iso, iso)) for iso in all_iso], key=lambda x: x[1]
    )
    iso_list = [iso for iso, _ in all_opts]

    years = sorted(df_raw["year"].unique())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(years[0]),
        max_value=int(years[-1]),
        value=(int(years[0]), int(years[-1])),
        help="Filter which years appear in all charts.",
    )

    with st.sidebar.expander("Adjust Pillar Weights"):
        st.markdown(
            "Move the sliders to change how much each pillar contributes to the "
            "overall livability score. Charts update instantly."
        )
        pillar_cols = [c for c in df_raw.columns if c.endswith("_score") and c != "target_score"]
        weights: dict[str, float] = {}
        for col in pillar_cols:
            label = col.replace("_score", "").replace("_", " ").title()
            default = float(pillar_w_cfg.get(col, 1.0 / max(len(pillar_cols), 1)))
            weights[col] = st.slider(label, 0.0, 1.0, default, 0.05, key=f"w_{col}")

    df = compute_live_scores(df_raw, weights)
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    shap_df = load_shap_values()
    fcast = load_forecasts()

    # ---- Tabs --------------------------------------------------------------
    tab_map, tab_single, tab_compare, tab_forecast, tab_data = st.tabs([
        "\U0001f5fa  World Map",
        "\U0001f50d  Country Analysis",
        "\U0001f4ca  Compare Countries",
        "\U0001f52e  Forecast",
        "\U0001f5c3  Data Explorer",
    ])

    with tab_map:
        render_map(df, country_names)

    with tab_single:
        st.subheader("Country Deep-Dive")
        render_single(df, fcast, shap_df, country_names, iso_list)

    with tab_compare:
        st.subheader("Compare Two Countries")
        render_compare(df, fcast, country_names, iso_list)

    with tab_forecast:
        st.subheader("Forecast and Predict")
        render_forecast(df, fcast, country_names, iso_list)

    with tab_data:
        st.subheader("Data Explorer")
        render_data_explorer(df, country_names, iso_list)


if __name__ == "__main__":
    main()
