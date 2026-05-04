
"""
app/app.py
==========
Streamlit dashboard â€” Global Livability AI

Modes:
  Single Country  â€” deep-dive with score, rank, time-series, pillars, SHAP, forecast
  Compare Two     â€” side-by-side comparison of any two countries

Tabs:
  1. World Map      â€” choropleth of latest livability scores (all countries)
  2. Analysis       â€” single deep-dive OR side-by-side comparison
  3. Drivers (SHAP) â€” global feature importance + per-country SHAP
  4. Data Explorer  â€” raw feature matrix, downloadable CSV
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

# â”€â”€ Paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"
ASSETS_DIR = ROOT / "app" / "assets"
FEATURES_DIR = ROOT / "data" / "features"
RAW_DIR = ROOT / "data" / "raw"


# â”€â”€ Config & loaders â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@st.cache_data
def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


@st.cache_data
def load_country_names() -> dict[str, str]:
    """Return {iso3: name}. Falls back to a minimal dict if CSV not yet generated."""
    p = RAW_DIR / "country_names.csv"
    if p.exists():
        df = pd.read_csv(p)
        return dict(zip(df["iso3"], df["country_name"]))
    return {
        "THA": "Thailand", "MYS": "Malaysia", "VNM": "Viet Nam",
        "IDN": "Indonesia", "PHL": "Philippines", "SGP": "Singapore",
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


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def compute_live_scores(df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Re-score every (iso3, year) with custom pillar weights."""
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
    sub = df[df["year"] == latest].sort_values("target_score", ascending=False).reset_index(drop=True)
    sub["rank"] = sub.index + 1
    sub["country"] = sub["iso3"].map(country_names).fillna(sub["iso3"])
    return sub


def _render_single(iso3: str, df: pd.DataFrame, fcast: pd.DataFrame | None,
                   shap_df: pd.DataFrame | None, country_names: dict) -> None:
    """Full deep-dive for a single country."""
    cname = country_names.get(iso3, iso3)
    ranked = _rank_latest(df, country_names)
    latest_year = df["year"].max()
    score_row = df[(df["iso3"] == iso3) & (df["year"] == latest_year)]
    rank_row = ranked[ranked["iso3"] == iso3]
    score = score_row["target_score"].values[0] if len(score_row) else float("nan")
    rank = rank_row["rank"].values[0] if len(rank_row) else "â€“"
    n_countries = len(ranked)

    col1, col2, col3 = st.columns(3)
    col1.metric("Livability Score", f"{score:.1f} / 100")
    col2.metric("Global Rank", f"#{rank} / {n_countries}")
    country_ts = df[df["iso3"] == iso3].sort_values("year")
    if len(country_ts) >= 2:
        trend = country_ts["target_score"].iloc[-1] - country_ts["target_score"].iloc[-2]
        col3.metric("YoY Change", f"{trend:+.2f}")

    st.markdown("---")

    st.subheader(f"{cname} â€” Livability Over Time")
    fig_ts = px.line(country_ts, x="year", y="target_score",
                     markers=True, labels={"target_score": "Score", "year": "Year"})
    fig_ts.update_layout(height=300)
    st.plotly_chart(fig_ts, use_container_width=True)

    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    if pillar_cols and len(score_row):
        vals = [float(score_row[c].values[0]) for c in pillar_cols]
        labels = [c.replace("_score", "").replace("_", " ").title() for c in pillar_cols]
        fig_radar = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=labels + [labels[0]],
            fill="toself", name=cname,
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 100])),
                                title="Pillar Scores", height=420)
        st.plotly_chart(fig_radar, use_container_width=True)

    if fcast is not None:
        fc = fcast[fcast["iso3"] == iso3]
        if len(fc):
            st.subheader("Forecast (2025â€“2030)")
            fig_fc = px.line(fc, x="year", y="yhat",
                             error_y_minus="yhat_lower", error_y="yhat_upper",
                             labels={"yhat": "Score", "year": "Year"})
            fig_fc.update_layout(height=280)
            st.plotly_chart(fig_fc, use_container_width=True)

    if shap_df is not None and "iso3" in shap_df.columns:
        shap_c = shap_df[shap_df["iso3"] == iso3]
        if len(shap_c):
            feat_cols = [c for c in shap_c.columns if c not in ("iso3", "year")]
            means = shap_c[feat_cols].mean().sort_values(key=abs, ascending=False).head(15)
            fig_shap = px.bar(x=means.values, y=means.index, orientation="h",
                              labels={"x": "Mean SHAP", "y": "Feature"},
                              title=f"Feature Drivers â€” {cname}")
            fig_shap.update_layout(height=380)
            st.plotly_chart(fig_shap, use_container_width=True)


def _render_compare(iso_a: str, iso_b: str, df: pd.DataFrame,
                    fcast: pd.DataFrame | None, country_names: dict) -> None:
    """Side-by-side comparison for two countries."""
    name_a = country_names.get(iso_a, iso_a)
    name_b = country_names.get(iso_b, iso_b)
    ranked = _rank_latest(df, country_names)
    latest_year = df["year"].max()
    n_countries = len(ranked)

    def _get(iso, col):
        row = ranked[ranked["iso3"] == iso]
        return row[col].values[0] if len(row) else ("â€“" if col == "rank" else float("nan"))

    score_a, score_b = _get(iso_a, "target_score"), _get(iso_b, "target_score")
    rank_a, rank_b = _get(iso_a, "rank"), _get(iso_b, "rank")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"{name_a} Score", f"{score_a:.1f}" if isinstance(score_a, float) else score_a)
    col2.metric(f"{name_a} Rank", f"#{rank_a} / {n_countries}")
    col3.metric(f"{name_b} Score", f"{score_b:.1f}" if isinstance(score_b, float) else score_b)
    col4.metric(f"{name_b} Rank", f"#{rank_b} / {n_countries}")

    st.markdown("---")

    ts_a = df[df["iso3"] == iso_a][["year", "target_score"]].assign(country=name_a)
    ts_b = df[df["iso3"] == iso_b][["year", "target_score"]].assign(country=name_b)
    fig_ts = px.line(pd.concat([ts_a, ts_b]), x="year", y="target_score", color="country",
                     markers=True, labels={"target_score": "Score", "year": "Year"},
                     title="Livability Score Over Time")
    fig_ts.update_layout(height=320)
    st.plotly_chart(fig_ts, use_container_width=True)

    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    if pillar_cols:
        row_a = df[(df["iso3"] == iso_a) & (df["year"] == latest_year)]
        row_b = df[(df["iso3"] == iso_b) & (df["year"] == latest_year)]
        labels = [c.replace("_score", "").replace("_", " ").title() for c in pillar_cols]
        vals_a = [float(row_a[c].values[0]) if len(row_a) else 0.0 for c in pillar_cols]
        vals_b = [float(row_b[c].values[0]) if len(row_b) else 0.0 for c in pillar_cols]
        fig_bars = go.Figure([
            go.Bar(name=name_a, x=labels, y=vals_a),
            go.Bar(name=name_b, x=labels, y=vals_b),
        ])
        fig_bars.update_layout(barmode="group", title="Pillar Comparison", height=360)
        st.plotly_chart(fig_bars, use_container_width=True)

        metrics = {"Metric": ["Overall Score", "Rank"] + labels}
        metrics[name_a] = ([f"{score_a:.1f}", f"#{rank_a}"] +
                           [f"{v:.1f}" for v in vals_a])
        metrics[name_b] = ([f"{score_b:.1f}", f"#{rank_b}"] +
                           [f"{v:.1f}" for v in vals_b])
        st.dataframe(pd.DataFrame(metrics), use_container_width=True)

    if fcast is not None:
        fc_a = fcast[fcast["iso3"] == iso_a]
        fc_b = fcast[fcast["iso3"] == iso_b]
        if len(fc_a) or len(fc_b):
            st.subheader("Forecast Comparison (2025â€“2030)")
            c1, c2 = st.columns(2)
            for col, fc, name in [(c1, fc_a, name_a), (c2, fc_b, name_b)]:
                if len(fc):
                    fig = px.line(fc, x="year", y="yhat",
                                  error_y_minus="yhat_lower", error_y="yhat_upper",
                                  title=name, labels={"yhat": "Score", "year": "Year"})
                    fig.update_layout(height=260)
                    col.plotly_chart(fig, use_container_width=True)


# â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> None:
    st.set_page_config(page_title="Global Livability AI", page_icon="ðŸŒ", layout="wide")
    st.title("ðŸŒ Global Livability AI")

    cfg = load_config()
    country_names = load_country_names()

    feat_path = FEATURES_DIR / "features.csv"
    if not feat_path.exists():
        st.warning(
            "No feature data found. Run the pipeline first:\n\n"
            "```\npython src/collect.py\npython src/harmonize.py\n"
            "python src/impute.py\npython src/features.py\npython src/target.py\n```"
        )
        return

    df_raw = load_features()
    pillar_w_cfg: dict = cfg.get("pillar_weights", {})

    # â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    st.sidebar.header("Settings")
    mode = st.sidebar.radio("Mode", ["Single Country", "Compare Two Countries"])

    all_iso = sorted(df_raw["iso3"].unique())
    all_opts = sorted([(iso, country_names.get(iso, iso)) for iso in all_iso], key=lambda x: x[1])
    iso_list = [iso for iso, _ in all_opts]
    labels = [f"{name} ({iso})" for iso, name in all_opts]

    def _default_idx(preferred: list[str]) -> int:
        for p in preferred:
            if p in iso_list:
                return iso_list.index(p)
        return 0

    iso_a = iso_list[st.sidebar.selectbox(
        "Country A", range(len(iso_list)),
        index=_default_idx(["SGP", "NOR", "THA"]),
        format_func=lambda i: labels[i],
    )]
    iso_b: str | None = None
    if mode == "Compare Two Countries":
        iso_b = iso_list[st.sidebar.selectbox(
            "Country B", range(len(iso_list)),
            index=_default_idx(["MYS", "DEU", "VNM"]),
            format_func=lambda i: labels[i],
        )]

    years = sorted(df_raw["year"].unique())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(years[0]), max_value=int(years[-1]),
        value=(int(years[0]), int(years[-1])),
    )

    with st.sidebar.expander("Pillar Weights"):
        pillar_cols = [c for c in df_raw.columns if c.endswith("_score") and c != "target_score"]
        weights: dict[str, float] = {}
        for col in pillar_cols:
            label = col.replace("_score", "").replace("_", " ").title()
            default = float(pillar_w_cfg.get(col, 1.0 / max(len(pillar_cols), 1)))
            weights[col] = st.slider(label, 0.0, 1.0, default, 0.05)

    df = compute_live_scores(df_raw, weights)
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    shap_df = load_shap_values()
    fcast = load_forecasts()

    # â”€â”€ Tabs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    tab1, tab2, tab3, tab4 = st.tabs(
        ["ðŸŒ World Map", "ðŸ“Š Analysis", "ðŸ” Drivers", "ðŸ—ƒï¸ Data Explorer"]
    )

    # Tab 1 â€” World Map
    with tab1:
        st.subheader("Global Livability Scores â€” Latest Year")
        latest_year = df["year"].max()
        latest = df[df["year"] == latest_year].copy()
        latest["country"] = latest["iso3"].map(country_names).fillna(latest["iso3"])
        latest = latest.sort_values("target_score", ascending=False).reset_index(drop=True)
        latest["rank"] = latest.index + 1

        fig_map = px.choropleth(
            latest, locations="iso3", color="target_score",
            hover_name="country",
            hover_data={"target_score": ":.1f", "rank": True, "iso3": False},
            color_continuous_scale="RdYlGn", range_color=[0, 100],
            labels={"target_score": "Livability Score"},
        )
        fig_map.update_layout(
            geo=dict(showframe=False, showcoastlines=True,
                     projection_type="natural earth"),
            height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(title="Score"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.markdown("**Top 10 Countries**")
        c1.dataframe(
            latest[["rank", "country", "target_score"]].head(10)
            .rename(columns={"target_score": "Score", "rank": "Rank", "country": "Country"}),
            use_container_width=True,
        )
        c2.markdown("**Bottom 10 Countries**")
        c2.dataframe(
            latest[["rank", "country", "target_score"]].tail(10)
            .sort_values("rank", ascending=False)
            .rename(columns={"target_score": "Score", "rank": "Rank", "country": "Country"}),
            use_container_width=True,
        )

    # Tab 2 â€” Analysis
    with tab2:
        if mode == "Single Country":
            st.subheader(f"Country Deep-Dive: {country_names.get(iso_a, iso_a)}")
            _render_single(iso_a, df, fcast, shap_df, country_names)
        else:
            name_a = country_names.get(iso_a, iso_a)
            name_b = country_names.get(iso_b, iso_b) if iso_b else "?"
            st.subheader(f"Comparison: {name_a} vs {name_b}")
            if iso_b:
                _render_compare(iso_a, iso_b, df, fcast, country_names)

    # Tab 3 â€” Drivers
    with tab3:
        st.subheader("Feature Importance (SHAP)")
        shap_img = ASSETS_DIR / "shap_global.png"
        if shap_img.exists():
            st.image(str(shap_img), caption="Global SHAP Summary",
                     use_container_width=True)
        elif shap_df is not None:
            feat_cols = [c for c in shap_df.columns if c not in ("iso3", "year")]
            if feat_cols:
                means = shap_df[feat_cols].abs().mean().sort_values(ascending=False)
                fig = px.bar(x=means.values, y=means.index, orientation="h",
                             labels={"x": "Mean |SHAP|", "y": "Feature"})
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run `python src/explain.py` to generate SHAP values.")

        if shap_df is not None and "iso3" in shap_df.columns:
            with st.expander("Per-Country SHAP"):
                chosen = st.selectbox(
                    "Country",
                    options=iso_list,
                    index=_default_idx([iso_a]),
                    format_func=lambda i: f"{country_names.get(i, i)} ({i})",
                    key="shap_country_sel",
                )
                shap_c = shap_df[shap_df["iso3"] == chosen]
                if len(shap_c):
                    fcols = [c for c in shap_c.columns if c not in ("iso3", "year")]
                    m = shap_c[fcols].mean().sort_values(key=abs, ascending=False).head(15)
                    fig_c = px.bar(x=m.values, y=m.index, orientation="h",
                                   labels={"x": "Mean SHAP", "y": "Feature"},
                                   title=country_names.get(chosen, chosen))
                    fig_c.update_layout(height=360)
                    st.plotly_chart(fig_c, use_container_width=True)
                    st.download_button(
                        "Download SHAP CSV",
                        shap_c.to_csv(index=False).encode(),
                        file_name=f"shap_{chosen}.csv",
                        mime="text/csv",
                    )

    # Tab 4 â€” Data Explorer
    with tab4:
        st.subheader("Feature Matrix")
        only_selected = st.checkbox(
            f"Show only {country_names.get(iso_a, iso_a)}", value=False
        )
        show_df = df[df["iso3"] == iso_a].copy() if only_selected else df.copy()
        show_df["country"] = show_df["iso3"].map(country_names).fillna(show_df["iso3"])
        st.dataframe(show_df, use_container_width=True)
        st.download_button(
            "Download CSV",
            show_df.to_csv(index=False).encode(),
            file_name="livability_features.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()

