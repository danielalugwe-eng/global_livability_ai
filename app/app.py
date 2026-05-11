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
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

from country_profiles import COUNTRY_PROFILES, get_col_labels, get_profile
from image_utils import (
    cost_of_living_url,
    country_hero_url,
    tourist_spot_url,
    transport_url,
)

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


def _mode_with_emoji(mode: str) -> str:
    icon_map = {
        "Flight": "✈️",
        "Train": "🚂",
        "Bus": "🚌",
        "Ferry": "⛴️",
        "Road": "🚗",
    }
    return f"{icon_map.get(mode, '🧭')} {mode}"


def _render_tourist_cards(cname: str, tourist_spots: list[dict], show_images: bool,
                          cards_per_row: int = 3, max_items: int | None = None) -> None:
    if not tourist_spots:
        st.info("Tourist spot data coming soon.")
        return

    spots = tourist_spots[:max_items] if max_items else tourist_spots
    if show_images:
        with st.spinner("Loading..."):
            for i in range(0, len(spots), cards_per_row):
                row = spots[i:i + cards_per_row]
                cols = st.columns(cards_per_row)
                for idx, spot in enumerate(row):
                    with cols[idx]:
                        st.image(
                            tourist_spot_url(spot.get("name", "Travel Spot"), cname),
                            use_column_width=True,
                        )
                        st.markdown(f"**{spot.get('name', 'Spot')}**")
                        st.markdown(spot.get("description", ""))
                        fee = spot.get("entry_fee_usd")
                        fee_label = "Free" if fee is None else f"${float(fee):.0f}"
                        st.caption(
                            f"Type: {spot.get('type', 'N/A')} | Best Season: {spot.get('best_season', 'N/A')} | Entry: {fee_label}"
                        )
    else:
        for i in range(0, len(spots), cards_per_row):
            row = spots[i:i + cards_per_row]
            cols = st.columns(cards_per_row)
            for idx, spot in enumerate(row):
                with cols[idx]:
                    st.markdown(f"**{spot.get('name', 'Spot')}**")
                    st.markdown(spot.get("description", ""))
                    fee = spot.get("entry_fee_usd")
                    fee_label = "Free" if fee is None else f"${float(fee):.0f}"
                    st.caption(
                        f"Type: {spot.get('type', 'N/A')} | Best Season: {spot.get('best_season', 'N/A')} | Entry: {fee_label}"
                    )


def _render_routes_table(routes: list[dict], country_names: dict) -> None:
    if not routes:
        st.info("Route data coming soon.")
        return
    rows = []
    for route in routes:
        from_iso = route.get("from_iso3", "")
        rows.append(
            {
                "From": country_names.get(from_iso, from_iso),
                "Mode": _mode_with_emoji(route.get("mode", "Road")),
                "Duration": f"{float(route.get('duration_hrs', 0.0)):.1f} hrs",
                "Cost": f"${float(route.get('estimated_cost_usd', 0.0)):.0f}",
                "Reliability": f"{float(route.get('reliability_score', 0.0)):.0f}/100",
                "Carbon": f"{float(route.get('carbon_kg', 0.0)):.0f} kg",
                "Visa Friction": route.get("visa_friction", "N/A"),
                "Notes": route.get("notes", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


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
                  iso_list: list[str], show_images: bool,
                  traveler_profile: str) -> None:
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
    profile = get_profile(iso3) or {}

    st.markdown(f"## {cname}")
    if show_images:
        st.image(country_hero_url(cname), use_column_width=True, caption=f"{cname} - Hero")

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

    st.markdown("---")
    st.subheader(f"Getting Around {cname}")
    transport = profile.get("transport_internal", {})
    if show_images:
        st.image(transport_url(cname, "public transport"), use_column_width=True)
    if transport:
        st.markdown(f"**Metro cities:** {', '.join(transport.get('metro_cities', [])) or 'N/A'}")
        st.markdown("**Intercity options:**")
        for opt in transport.get("intercity_options", []):
            st.markdown(f"- {opt}")
        st.markdown(f"**Ride-hailing apps:** {', '.join(transport.get('ride_hailing_apps', [])) or 'N/A'}")
        st.markdown(f"**Notes:** {transport.get('notes', 'N/A')}")
    else:
        st.info("Transport data coming soon.")

    st.markdown("---")
    st.subheader(f"How to Reach {cname}")
    _render_routes_table(profile.get("fastest_routes", []), country_names)

    st.markdown("---")
    st.subheader(f"Cost of Living in {cname}")
    if show_images:
        st.image(cost_of_living_url(cname), use_column_width=True)

    if profile.get("cost_of_living"):
        labels = get_col_labels()
        cdf = pd.DataFrame(
            {
                "Category": [labels[k] for k in labels],
                "Value (USD)": [profile["cost_of_living"].get(k, 0) for k in labels],
            }
        )
        st.dataframe(cdf, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Tourist Spots")
    _render_tourist_cards(cname, profile.get("tourist_spots", []), show_images, cards_per_row=3)

    st.markdown("---")
    st.subheader("2026 Decision Readiness")
    readiness = profile.get("move_readiness", {})
    quality = profile.get("data_quality", {})
    if readiness:
        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Visa Ease", f"{readiness.get('visa_friction', 0):.0f}/100")
        r2.metric("Healthcare", f"{readiness.get('healthcare_access', 0):.0f}/100")
        r3.metric("Internet", f"{readiness.get('internet_reliability', 0):.0f}/100")
        r4.metric("Climate Risk", f"{readiness.get('climate_risk', 0):.0f}/100")
        r5.metric("Safety Risk", f"{readiness.get('safety_risk', 0):.0f}/100")
    if quality:
        st.caption(
            f"Source: {quality.get('source', 'N/A')} | Updated: {quality.get('updated_at', 'N/A')} | Confidence: {float(quality.get('confidence_score', 0.0)):.2f}"
        )
        st.caption(quality.get("quality_notes", ""))

    st.markdown("---")
    st.subheader("Personalized Monthly Budget (USD)")
    budgets = profile.get("budget_profiles", {})
    profile_key_map = {
        "Budget Backpacker": "budget_backpacker",
        "Digital Nomad": "digital_nomad",
        "Family (1 Child)": "family_one_child",
        "Retiree Comfort": "retiree_comfort",
    }
    selected_key = profile_key_map.get(traveler_profile, "digital_nomad")
    suggested = float(budgets.get(selected_key, 0.0))
    if suggested:
        st.metric(f"Recommended budget for {traveler_profile}", f"${suggested:,.0f}")
    if budgets:
        pretty = {k.replace('_', ' ').title(): v for k, v in budgets.items()}
        st.dataframe(pd.DataFrame([pretty]), use_container_width=True, hide_index=True)


def render_compare(df: pd.DataFrame, fcast: pd.DataFrame | None,
                   country_names: dict, iso_list: list[str], show_images: bool,
                   traveler_profile: str) -> None:
    st.markdown(
        "Pick two countries to compare side-by-side — livability scores, cost of living, "
        "currency, history, and everything a potential mover needs to know."
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
    prof_a = get_profile(iso_a) or {}
    prof_b = get_profile(iso_b) or {}
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

    # ── Section 1: Livability Scores ─────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Livability Scores")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric(f"🏆 {name_a} — Score", f"{score_a:.1f}" if isinstance(score_a, float) else score_a)
    mc2.metric(f"📍 {name_a} — Rank", f"#{rank_a} of {n_countries}")
    mc3.metric(f"🏆 {name_b} — Score", f"{score_b:.1f}" if isinstance(score_b, float) else score_b)
    mc4.metric(f"📍 {name_b} — Rank", f"#{rank_b} of {n_countries}")

    ts_a = df[df["iso3"] == iso_a][["year", "target_score"]].assign(country=name_a)
    ts_b = df[df["iso3"] == iso_b][["year", "target_score"]].assign(country=name_b)
    fig_ts = px.line(
        pd.concat([ts_a, ts_b]), x="year", y="target_score", color="country",
        markers=True,
        labels={"target_score": "Livability Score", "year": "Year", "country": "Country"},
    )
    fig_ts.update_layout(height=320)
    st.plotly_chart(fig_ts, use_container_width=True)

    # ── Section 2: Pillar breakdown ──────────────────────────────────────────
    pillar_cols = [c for c in df.columns if c.endswith("_score") and c != "target_score"]
    if pillar_cols:
        st.markdown("---")
        st.subheader("🧩 Pillar-by-Pillar Comparison")
        row_a = df[(df["iso3"] == iso_a) & (df["year"] == latest_year)]
        row_b = df[(df["iso3"] == iso_b) & (df["year"] == latest_year)]
        pillar_labels = [c.replace("_score", "").replace("_", " ").title() for c in pillar_cols]
        vals_a = [float(row_a[c].values[0]) if len(row_a) else 0.0 for c in pillar_cols]
        vals_b = [float(row_b[c].values[0]) if len(row_b) else 0.0 for c in pillar_cols]

        tab_bar, tab_radar, tab_table = st.tabs(["Bar Chart", "Radar", "Table"])
        with tab_bar:
            fig_bars = go.Figure([
                go.Bar(name=name_a, x=pillar_labels, y=vals_a, marker_color="#457b9d"),
                go.Bar(name=name_b, x=pillar_labels, y=vals_b, marker_color="#e63946"),
            ])
            fig_bars.update_layout(barmode="group", height=380, yaxis_title="Score (0-100)")
            st.plotly_chart(fig_bars, use_container_width=True)
        with tab_radar:
            fig_radar = go.Figure()
            for name, vals, colour in [
                (name_a, vals_a, "#457b9d"), (name_b, vals_b, "#e63946")
            ]:
                fig_radar.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]], theta=pillar_labels + [pillar_labels[0]],
                    fill="toself", name=name, line=dict(color=colour),
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])), height=420,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        with tab_table:
            metrics = {"Metric": ["Overall Score", "Regional Rank"] + pillar_labels}
            metrics[name_a] = [f"{score_a:.1f}", f"#{rank_a}"] + [f"{v:.1f}" for v in vals_a]
            metrics[name_b] = [f"{score_b:.1f}", f"#{rank_b}"] + [f"{v:.1f}" for v in vals_b]
            st.dataframe(pd.DataFrame(metrics), use_container_width=True, hide_index=True)

    # ── Section 3: Country Profiles (for movers) ────────────────────────────
    st.markdown("---")
    st.subheader("🌏 Country Overview")
    ca, cb = st.columns(2)

    for col, name, prof in [(ca, name_a, prof_a), (cb, name_b, prof_b)]:
        with col:
            st.markdown(f"### {name}")
            if prof:
                st.markdown(f"**🏛️ Capital:** {prof.get('capital', '—')}")
                st.markdown(f"**👥 Population:** {prof.get('population', '—')}")
                st.markdown(f"**📐 Area:** {prof.get('area_km2', 0):,} km²")
                langs = prof.get("languages", [])
                st.markdown(f"**🗣️ Languages:** {', '.join(langs)}")
            else:
                st.info("No profile data available.")

    # ── Section 4: History side-by-side ─────────────────────────────────────
    st.markdown("---")
    st.subheader("📖 Brief History")
    ha, hb = st.columns(2)
    with ha:
        st.markdown(f"**{name_a}**")
        st.markdown(prof_a.get("history", "No history available.") if prof_a else "No history available.")
    with hb:
        st.markdown(f"**{name_b}**")
        st.markdown(prof_b.get("history", "No history available.") if prof_b else "No history available.")

    # ── Section 5: Currency comparison ──────────────────────────────────────
    st.markdown("---")
    st.subheader("💱 Currency")
    curr_a = prof_a.get("currency", {}) if prof_a else {}
    curr_b = prof_b.get("currency", {}) if prof_b else {}
    cu1, cu2 = st.columns(2)
    for col, name, curr in [(cu1, name_a, curr_a), (cu2, name_b, curr_b)]:
        with col:
            st.markdown(f"**{name}**")
            if curr:
                rate = curr.get("approx_usd_rate", None)
                if rate is not None:
                    label = f"1 {curr.get('code','?')} = ${1/rate:.2f} USD" if rate < 1 else f"1 USD ≈ {rate:,.2f} {curr.get('code','?')}"
                else:
                    label = "—"
                st.markdown(
                    f"**{curr.get('name','—')}** &nbsp; `{curr.get('code','—')}` &nbsp; {curr.get('symbol','—')}"
                )
                st.markdown(f"📈 Exchange Rate: **{label}**")
            else:
                st.info("No currency data.")
    st.caption("Exchange rates are approximate 2024 averages.")

    # ── Section 6: Cost of Living side-by-side ───────────────────────────────
    st.markdown("---")
    st.subheader("🏠 Cost of Living — Side-by-Side (Monthly USD, 2024 approx.)")

    col_labels = get_col_labels()
    col_a_data = prof_a.get("cost_of_living", {}) if prof_a else {}
    col_b_data = prof_b.get("cost_of_living", {}) if prof_b else {}

    if col_a_data or col_b_data:
        # Comparison bar chart
        expense_keys = [k for k in col_labels if k != "avg_monthly_salary_net"]
        chart_rows = []
        for k in expense_keys:
            chart_rows.append({"Category": col_labels[k], "Country": name_a, "Cost (USD)": col_a_data.get(k, 0)})
            chart_rows.append({"Category": col_labels[k], "Country": name_b, "Cost (USD)": col_b_data.get(k, 0)})
        fig_col = px.bar(
            pd.DataFrame(chart_rows),
            x="Cost (USD)", y="Category", color="Country", orientation="h",
            barmode="group",
            color_discrete_map={name_a: "#457b9d", name_b: "#e63946"},
            text="Cost (USD)",
        )
        fig_col.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")
        fig_col.update_layout(
            height=340, margin=dict(l=0, r=60, t=10, b=10), coloraxis_showscale=False,
        )
        st.plotly_chart(fig_col, use_container_width=True)

        # Metric cards
        cla, clb = st.columns(2)
        for col, name, data in [(cla, name_a, col_a_data), (clb, name_b, col_b_data)]:
            with col:
                st.markdown(f"**{name}**")
                if data:
                    total_exp = sum(data.get(k, 0) for k in expense_keys)
                    salary = data.get("avg_monthly_salary_net", 0)
                    surplus = salary - total_exp
                    for k in expense_keys:
                        st.markdown(f"- {col_labels[k]}: **${data.get(k, 0):,.0f}**")
                    st.markdown(f"- {col_labels['avg_monthly_salary_net']}: **${salary:,.0f}**")
                    st.markdown(
                        f"- 💰 Monthly surplus: **${abs(surplus):,.0f}** "
                        f"({'✅ surplus' if surplus >= 0 else '⚠️ deficit'})"
                    )
                else:
                    st.info("No cost-of-living data.")
        st.caption("Expenses = rent + groceries + transport + utilities. All figures are approximate 2024 averages.")

    # ── Section 6B: Tourist highlights ─────────────────────────────────────
    st.markdown("---")
    st.subheader("🗺️ Tourist Highlights")
    th_a, th_b = st.columns(2)
    with th_a:
        st.markdown(f"**{name_a}**")
        _render_tourist_cards(name_a, prof_a.get("tourist_spots", []), show_images, cards_per_row=1, max_items=3)
    with th_b:
        st.markdown(f"**{name_b}**")
        _render_tourist_cards(name_b, prof_b.get("tourist_spots", []), show_images, cards_per_row=1, max_items=3)

    # ── Section 6C: Fastest direct routes between the two countries ────────
    st.markdown("---")
    st.subheader("🚀 Fastest Route Between Countries")
    route_a_to_b = next((r for r in prof_a.get("fastest_routes", []) if r.get("from_iso3") == iso_b), None)
    route_b_to_a = next((r for r in prof_b.get("fastest_routes", []) if r.get("from_iso3") == iso_a), None)
    if not route_a_to_b and not route_b_to_a:
        st.info("No direct route data available between these countries.")
    else:
        ra, rb = st.columns(2)
        with ra:
            st.markdown(f"**{name_b} → {name_a}**")
            if route_a_to_b:
                st.markdown(f"Mode: {_mode_with_emoji(route_a_to_b.get('mode', 'Road'))}")
                st.markdown(f"Duration: {float(route_a_to_b.get('duration_hrs', 0.0)):.1f} hrs")
                st.markdown(f"Notes: {route_a_to_b.get('notes', 'N/A')}")
            else:
                st.info("No route found.")

        route_candidates = [r for r in [route_a_to_b, route_b_to_a] if r]
        if route_candidates:
            def _value_score(r: dict) -> float:
                # Higher is better: reliability rewarded, cost/time/carbon penalized.
                return (
                    float(r.get("reliability_score", 0.0))
                    - float(r.get("estimated_cost_usd", 0.0)) * 0.08
                    - float(r.get("duration_hrs", 0.0)) * 3.0
                    - float(r.get("carbon_kg", 0.0)) * 0.02
                )

            best_route = max(route_candidates, key=_value_score)
            st.success(
                "Best value route now: "
                f"{_mode_with_emoji(best_route.get('mode', 'Road'))}, "
                f"{float(best_route.get('duration_hrs', 0.0)):.1f} hrs, "
                f"${float(best_route.get('estimated_cost_usd', 0.0)):.0f}, "
                f"reliability {float(best_route.get('reliability_score', 0.0)):.0f}/100."
            )
        with rb:
            st.markdown(f"**{name_a} → {name_b}**")
            if route_b_to_a:
                st.markdown(f"Mode: {_mode_with_emoji(route_b_to_a.get('mode', 'Road'))}")
                st.markdown(f"Duration: {float(route_b_to_a.get('duration_hrs', 0.0)):.1f} hrs")
                st.markdown(f"Notes: {route_b_to_a.get('notes', 'N/A')}")
            else:
                st.info("No route found.")

    # ── Section 7: Mover's Verdict ───────────────────────────────────────────
    st.markdown("---")
    st.subheader("✈️ Mover's Verdict")
    mv_a, mv_b = st.columns(2)
    for col, name, prof, iso, score, rank in [
        (mv_a, name_a, prof_a, iso_a, score_a, rank_a),
        (mv_b, name_b, prof_b, iso_b, score_b, rank_b),
    ]:
        with col:
            st.markdown(f"#### 🌍 {name}")
            if prof:
                curr = prof.get("currency", {})
                col_data = prof.get("cost_of_living", {})
                expense_keys = [k for k in col_labels if k != "avg_monthly_salary_net"]
                total = sum(col_data.get(k, 0) for k in expense_keys) if col_data else 0
                salary = col_data.get("avg_monthly_salary_net", 0) if col_data else 0
                rate = curr.get("approx_usd_rate", None)
                rate_str = (f"1 USD ≈ {rate:,.1f} {curr.get('code','?')}" if rate and rate >= 1
                            else f"1 {curr.get('code','?')} = ${1/rate:.2f} USD" if rate else "—")
                st.markdown(
                    f"| | |\n|---|---|\n"
                    f"| 🏆 Livability Score | **{score:.1f}/100** |\n"
                    f"| 📍 Regional Rank | **#{rank} of {n_countries}** |\n"
                    f"| 💱 Currency | **{curr.get('name','—')} ({curr.get('code','—')})** |\n"
                    f"| 📈 Exchange Rate | **{rate_str}** |\n"
                    f"| 🏠 Est. Monthly Expenses | **${total:,.0f} USD** |\n"
                    f"| 💰 Avg Net Salary | **${salary:,.0f} USD** |\n"
                    f"| 🗣️ Language | **{', '.join(prof.get('languages', ['—'])[:2])}** |\n"
                    f"| 👥 Population | **{prof.get('population','—')}** |"
                )
                facts = prof.get("fun_facts", [])
                if facts:
                    st.markdown("**💡 Key Facts:**")
                    for fact in facts:
                        st.markdown(f"- {fact}")
            else:
                st.info("No profile data available.")

    # ── Section 8: Forecast comparison ───────────────────────────────────────
    if fcast is not None:
        fc_a = fcast[fcast["iso3"] == iso_a]
        fc_b = fcast[fcast["iso3"] == iso_b]
        future_a = fc_a[fc_a["year"] > latest_year] if len(fc_a) else fc_a
        future_b = fc_b[fc_b["year"] > latest_year] if len(fc_b) else fc_b
        if len(future_a) or len(future_b):
            st.markdown("---")
            st.subheader("🔮 Forecast Comparison (Next 5 Years)")
            st.markdown("Side-by-side forecast with 95% confidence band.")
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

    st.markdown("---")
    st.subheader("Profile Recommendation")
    budget_key = {
        "Budget Backpacker": "budget_backpacker",
        "Digital Nomad": "digital_nomad",
        "Family (1 Child)": "family_one_child",
        "Retiree Comfort": "retiree_comfort",
    }.get(traveler_profile, "digital_nomad")

    def _country_fit(name: str, prof: dict, score: float) -> float:
        readiness = prof.get("move_readiness", {})
        budgets = prof.get("budget_profiles", {})
        budget = float(budgets.get(budget_key, 0.0))
        readiness_avg = 0.0
        if readiness:
            readiness_avg = (
                float(readiness.get("visa_friction", 0.0))
                + float(readiness.get("healthcare_access", 0.0))
                + float(readiness.get("internet_reliability", 0.0))
                - float(readiness.get("climate_risk", 0.0)) * 0.6
                - float(readiness.get("safety_risk", 0.0)) * 0.6
            ) / 3.0
        affordability_boost = max(0.0, 1800.0 - budget) / 18.0 if budget else 0.0
        return float(score if isinstance(score, float) else 0.0) * 0.55 + readiness_avg * 0.35 + affordability_boost * 0.10

    fit_a = _country_fit(name_a, prof_a, score_a)
    fit_b = _country_fit(name_b, prof_b, score_b)
    if fit_a == fit_b:
        st.info(f"For {traveler_profile}, both countries are currently a near tie based on livability, readiness, and affordability.")
    else:
        winner = name_a if fit_a > fit_b else name_b
        st.success(f"For {traveler_profile}, **{winner}** is currently the stronger fit.")


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


def render_tourist_explorer(country_names: dict, iso_list: list[str],
                            show_images: bool) -> None:
    st.markdown("Explore travel highlights, fastest routes, and transport options by country.")

    iso3 = _country_dropdown(
        "Select country for tourism insights", iso_list, country_names,
        default_isos=["THA", "JPN", "ARE"], key="tour_sel",
    )
    profile = get_profile(iso3) or {}
    cname = country_names.get(iso3, iso3)
    quality = profile.get("data_quality", {})

    if quality:
        st.caption(
            f"Data source: {quality.get('source', 'N/A')} | Updated: {quality.get('updated_at', 'N/A')} | Confidence: {float(quality.get('confidence_score', 0.0)):.2f}"
        )

    if show_images:
        st.image(country_hero_url(cname), use_column_width=True, caption=f"{cname} - Travel")

    spot_filter = st.radio(
        "Filter spots",
        options=["All", "Heritage", "Nature", "City", "Beach", "Adventure", "Religious", "Museum"],
        horizontal=True,
    )

    spots = profile.get("tourist_spots", [])
    if spot_filter != "All":
        spots = [s for s in spots if s.get("type") == spot_filter]

    st.subheader("Tourist Spots")
    _render_tourist_cards(cname, spots, show_images, cards_per_row=3)

    st.markdown("---")
    st.subheader(f"Top 5 Fastest Ways to Reach {cname}")
    route_strategy = st.selectbox(
        "Route strategy",
        options=["Fastest", "Cheapest", "Best Value", "Low Carbon"],
        index=0,
        key="tour_route_strategy",
    )
    all_routes = profile.get("fastest_routes", [])
    if route_strategy == "Cheapest":
        routes = sorted(all_routes, key=lambda r: r.get("estimated_cost_usd", 0.0))[:5]
    elif route_strategy == "Best Value":
        routes = sorted(
            all_routes,
            key=lambda r: (
                -float(r.get("reliability_score", 0.0))
                + float(r.get("estimated_cost_usd", 0.0)) * 0.08
                + float(r.get("duration_hrs", 0.0)) * 2.5
            ),
        )[:5]
    elif route_strategy == "Low Carbon":
        routes = sorted(all_routes, key=lambda r: r.get("carbon_kg", 0.0))[:5]
    else:
        routes = sorted(all_routes, key=lambda r: r.get("duration_hrs", 0.0))[:5]
    _render_routes_table(routes, country_names)

    st.markdown("---")
    st.subheader("Internal Transport")
    transport = profile.get("transport_internal", {})
    if show_images:
        st.image(transport_url(cname, "public transport"), use_column_width=True)
    if transport:
        st.markdown(f"**Metro cities:** {', '.join(transport.get('metro_cities', [])) or 'N/A'}")
        st.markdown("**Intercity options:**")
        for opt in transport.get("intercity_options", []):
            st.markdown(f"- {opt}")
        st.markdown(f"**Ride-hailing apps:** {', '.join(transport.get('ride_hailing_apps', [])) or 'N/A'}")
        st.markdown(f"**Notes:** {transport.get('notes', 'N/A')}")
    else:
        st.info("Transport data coming soon.")


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
# Country Insights tab
# ---------------------------------------------------------------------------

def render_insights(df: pd.DataFrame, country_names: dict, iso_list: list[str]) -> None:
    """Render the Country Insights tab: history, currency, and cost-of-living."""

    st.markdown(
        "Select a country to explore its background, currency, and cost-of-living breakdown."
    )

    iso3 = _country_dropdown(
        "Select a country", iso_list, country_names,
        default_isos=["SGP", "JPN", "THA"], key="ins_sel",
    )

    profile = get_profile(iso3)

    if profile is None:
        st.info(
            f"No detailed profile available yet for **{country_names.get(iso3, iso3)}** ({iso3}). "
            "Quantitative data is still shown below."
        )
    else:
        cname = profile["name"]

        # ── Header ─────────────────────────────────────────────────────────
        st.markdown(f"## 🌏 {cname}")

        # ── Quick Facts ─────────────────────────────────────────────────────
        st.subheader("Quick Facts")
        qf1, qf2, qf3, qf4 = st.columns(4)
        qf1.metric("🏛️ Capital", profile.get("capital", "—"))
        qf2.metric("👥 Population", profile.get("population", "—"))
        qf3.metric("📐 Area (km²)", f"{profile.get('area_km2', 0):,}")
        langs = profile.get("languages", [])
        qf4.metric("🗣️ Language(s)", langs[0] if langs else "—")
        if len(langs) > 1:
            st.caption("Also spoken: " + ", ".join(langs[1:]))

        # ── History ─────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📖 Brief History")
        st.markdown(profile.get("history", "No history available."))

        # ── Currency ────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("💱 Currency")
        curr = profile.get("currency", {})
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric("Name", curr.get("name", "—"))
        cc2.metric("ISO Code", curr.get("code", "—"))
        cc3.metric("Symbol", curr.get("symbol", "—"))
        rate = curr.get("approx_usd_rate", None)
        if rate is not None:
            if rate < 1:
                label = f"1 {curr.get('code','?')} = ${1/rate:.2f} USD"
            else:
                label = f"1 USD ≈ {rate:,.2f} {curr.get('code','?')}"
            cc4.metric("Exchange Rate (≈ 2024)", label)
        st.caption(
            "Exchange rates are approximate 2024 averages. Actual rates vary; "
            "always check a live source before transacting."
        )

        # ── Cost of Living ───────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("🏠 Cost of Living (Approximate Monthly USD, 2024)")
        col_labels = get_col_labels()
        col_data = profile.get("cost_of_living", {})

        if col_data:
            # Metric cards for key figures
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🏠 Rent – 1BR City", f"${col_data.get('monthly_rent_city_1br', 0):,.0f}")
            m2.metric("🛒 Groceries", f"${col_data.get('monthly_groceries', 0):,.0f}")
            m3.metric("🚌 Transport Pass", f"${col_data.get('monthly_transport', 0):,.0f}")
            m4.metric("💡 Utilities", f"${col_data.get('monthly_utilities', 0):,.0f}")
            m5, m6 = st.columns(2)
            m5.metric("💰 Avg Net Salary", f"${col_data.get('avg_monthly_salary_net', 0):,.0f}")
            m6.metric("🍜 Cheap Meal", f"${col_data.get('meal_cheap_restaurant', 0):.1f}")

            st.markdown("##### Monthly Expense Breakdown")
            expense_keys = [k for k in col_labels if k != "avg_monthly_salary_net" and k in col_data]
            bar_df = pd.DataFrame({
                "Category": [col_labels[k] for k in expense_keys],
                "Cost (USD)": [col_data[k] for k in expense_keys],
            })

            # Regional benchmark comparison
            latest_year = df["year"].max()
            peers_isos = [
                i for i in iso_list
                if get_profile(i) and i != iso3
            ]
            peer_rents = [
                get_profile(i)["cost_of_living"].get("monthly_rent_city_1br", 0)
                for i in peers_isos
                if get_profile(i).get("cost_of_living")
            ]
            regional_avg_rent = sum(peer_rents) / len(peer_rents) if peer_rents else 0

            fig_bar = px.bar(
                bar_df, x="Cost (USD)", y="Category", orientation="h",
                text="Cost (USD)",
                color="Cost (USD)",
                color_continuous_scale="Blues",
                labels={"Cost (USD)": "Monthly Cost (USD)", "Category": ""},
            )
            fig_bar.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")
            fig_bar.update_layout(
                height=320,
                coloraxis_showscale=False,
                margin=dict(l=0, r=60, t=10, b=10),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Salary vs total expenses gauge
            total_expenses = sum(col_data.get(k, 0) for k in expense_keys)
            salary = col_data.get("avg_monthly_salary_net", 1)
            afford_pct = min(total_expenses / salary * 100, 200) if salary else 0
            surplus = salary - total_expenses

            ae1, ae2, ae3 = st.columns(3)
            ae1.metric("Total Monthly Expenses", f"${total_expenses:,.0f}")
            ae2.metric("Avg Net Salary", f"${salary:,.0f}")
            color = "normal" if surplus >= 0 else "inverse"
            ae3.metric(
                "Monthly Surplus / Deficit",
                f"${abs(surplus):,.0f}",
                delta=f"{'Surplus' if surplus >= 0 else 'Deficit'}",
                delta_color=color,
            )
            st.caption(
                "Expenses = rent + groceries + transport + utilities. "
                "Meal cost is not included in the total. All figures are approximate."
            )

            # Affordability comparison vs regional peers
            all_profiles_col = {
                i: get_profile(i)["cost_of_living"]
                for i in iso_list
                if get_profile(i) and get_profile(i).get("cost_of_living")
            }
            if len(all_profiles_col) > 1:
                st.markdown("##### How does it compare? (Regional Rent Comparison)")
                rent_compare = pd.DataFrame([
                    {
                        "Country": country_names.get(i, i),
                        "Monthly Rent 1BR (USD)": all_profiles_col[i].get("monthly_rent_city_1br", 0),
                        "Selected": (i == iso3),
                    }
                    for i in iso_list
                    if i in all_profiles_col
                ]).sort_values("Monthly Rent 1BR (USD)", ascending=True)

                fig_cmp = px.bar(
                    rent_compare,
                    x="Monthly Rent 1BR (USD)", y="Country",
                    orientation="h",
                    color="Selected",
                    color_discrete_map={True: "#e63946", False: "#457b9d"},
                    labels={"Monthly Rent 1BR (USD)": "Monthly Rent – 1BR City Centre (USD)"},
                )
                fig_cmp.update_layout(
                    height=max(300, 18 * len(rent_compare)),
                    showlegend=False,
                    margin=dict(l=0, r=20, t=10, b=10),
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

        st.caption("Cost-of-living estimates are sourced from Numbeo-style 2024 averages and may vary by city.")

        # ── Fun Facts ────────────────────────────────────────────────────────
        facts = profile.get("fun_facts", [])
        if facts:
            st.markdown("---")
            st.subheader("💡 Did You Know?")
            for fact in facts:
                st.markdown(f"- {fact}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Asia Livability AI",
        page_icon="\U0001f30f",
        layout="wide",
    )
    st.title("\U0001f30f Asia Livability AI")
    st.markdown(
        "An AI-powered dashboard tracking and forecasting quality of life across "
        "49 Asian countriesries using health, economy, education, environment, and infrastructure data."
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

    st.sidebar.markdown("---")
    show_images = st.sidebar.toggle("Show online images", value=True)
    traveler_profile = st.sidebar.selectbox(
        "Traveler / Mover Profile",
        options=["Budget Backpacker", "Digital Nomad", "Family (1 Child)", "Retiree Comfort"],
        index=1,
    )

    st.sidebar.markdown("### Quick Travel Tip")
    tip_isos = [i for i in all_iso if get_profile(i)]
    selected_iso = None
    for key in ("single_sel", "tour_sel", "ins_sel", "cmp_a", "cmp_b"):
        raw_val = st.session_state.get(key)
        if isinstance(raw_val, str) and "(" in raw_val and ")" in raw_val:
            parsed = raw_val.split("(")[-1].rstrip(")")
            if parsed in tip_isos:
                selected_iso = parsed
                break
    if not selected_iso and tip_isos:
        selected_iso = random.choice(tip_isos)

    if selected_iso:
        prof = get_profile(selected_iso) or {}
        facts = prof.get("fun_facts", [])
        if facts:
            st.sidebar.info(random.choice(facts))
        else:
            st.sidebar.info("Plan major routes in advance and compare weekday vs weekend prices.")

    df = compute_live_scores(df_raw, weights)
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    shap_df = load_shap_values()
    fcast = load_forecasts()

    # ---- Tabs --------------------------------------------------------------
    tab_map, tab_single, tab_compare, tab_forecast, tab_data, tab_insights, tab_tourist = st.tabs([
        "\U0001f5fa  World Map",
        "\U0001f50d  Country Analysis",
        "\U0001f4ca  Compare Countries",
        "\U0001f52e  Forecast",
        "\U0001f5c3  Data Explorer",
        "\U0001f4d6  Country Insights",
        "🗺️  Tourist Explorer",
    ])

    with tab_map:
        render_map(df, country_names)

    with tab_single:
        st.subheader("Country Deep-Dive")
        render_single(df, fcast, shap_df, country_names, iso_list, show_images, traveler_profile)

    with tab_compare:
        st.subheader("Compare Two Countries")
        render_compare(df, fcast, country_names, iso_list, show_images, traveler_profile)

    with tab_forecast:
        st.subheader("Forecast and Predict")
        render_forecast(df, fcast, country_names, iso_list)

    with tab_data:
        st.subheader("Data Explorer")
        render_data_explorer(df, country_names, iso_list)

    with tab_insights:
        st.subheader("Country Insights")
        render_insights(df, country_names, iso_list)

    with tab_tourist:
        st.subheader("Tourist Explorer")
        render_tourist_explorer(country_names, iso_list, show_images)


if __name__ == "__main__":
    main()
