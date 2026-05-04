
"""
src/collect.py
==============
Download raw data from all four sources:
  1. World Bank  (wbdata)
  2. UNDP HDI    (Excel download)
  3. WHO GHO     (OData REST API)
  4. Yale EPI    (Excel download)

Outputs → data/raw/*.csv
"""

from __future__ import annotations

import io
import logging
import time
from pathlib import Path

import pandas as pd
import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"


def load_config() -> dict:
    with open(CFG_PATH) as f:
        return yaml.safe_load(f)


# ── 1. World Bank ──────────────────────────────────────────────────────────────

# ── Country name → ISO3 mapping (for UNDP/EPI Excel parsing) ──────────────────
_NAME_TO_ISO3: dict[str, str] = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Andorra": "AND",
    "Angola": "AGO", "Antigua and Barbuda": "ATG", "Argentina": "ARG",
    "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
    "Bahamas": "BHS", "Bahrain": "BHR", "Bangladesh": "BGD", "Barbados": "BRB",
    "Belarus": "BLR", "Belgium": "BEL", "Belize": "BLZ", "Benin": "BEN",
    "Bhutan": "BTN", "Bolivia": "BOL", "Bolivia (Plurinational State of)": "BOL",
    "Bosnia and Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Brunei Darussalam": "BRN", "Brunei": "BRN", "Bulgaria": "BGR",
    "Burkina Faso": "BFA", "Burundi": "BDI", "Cabo Verde": "CPV",
    "Cape Verde": "CPV", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Central African Republic": "CAF", "Chad": "TCD", "Chile": "CHL",
    "China": "CHN", "Colombia": "COL", "Comoros": "COM",
    "Congo": "COG", "Congo, Rep.": "COG", "Congo, Dem. Rep.": "COD",
    "Democratic Republic of the Congo": "COD",
    "Congo (Democratic Republic of the)": "COD",
    "Costa Rica": "CRI", "Côte d'Ivoire": "CIV", "Cote d'Ivoire": "CIV",
    "Croatia": "HRV", "Cuba": "CUB", "Cyprus": "CYP",
    "Czechia": "CZE", "Czech Republic": "CZE",
    "Denmark": "DNK", "Djibouti": "DJI", "Dominica": "DMA",
    "Dominican Republic": "DOM", "Ecuador": "ECU", "Egypt": "EGY",
    "Egypt, Arab Rep.": "EGY", "El Salvador": "SLV", "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI", "Estonia": "EST", "Eswatini": "SWZ", "Swaziland": "SWZ",
    "Ethiopia": "ETH", "Fiji": "FJI", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Gambia": "GMB", "Gambia, The": "GMB",
    "Georgia": "GEO", "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC",
    "Grenada": "GRD", "Guatemala": "GTM", "Guinea": "GIN",
    "Guinea-Bissau": "GNB", "Guyana": "GUY", "Haiti": "HTI",
    "Honduras": "HND", "Hong Kong SAR, China": "HKG", "Hungary": "HUN",
    "Iceland": "ISL", "India": "IND", "Indonesia": "IDN", "Iran": "IRN",
    "Iran (Islamic Republic of)": "IRN", "Iran, Islamic Rep.": "IRN",
    "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR", "Italy": "ITA",
    "Jamaica": "JAM", "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ",
    "Kenya": "KEN", "Kiribati": "KIR", "Korea (Republic of)": "KOR",
    "Korea, Rep.": "KOR", "Korea, South": "KOR",
    "Korea (Democratic People's Rep.)": "PRK", "Kuwait": "KWT",
    "Kyrgyzstan": "KGZ", "Kyrgyz Republic": "KGZ",
    "Lao PDR": "LAO", "Lao People's Democratic Republic": "LAO", "Laos": "LAO",
    "Latvia": "LVA", "Lebanon": "LBN", "Lesotho": "LSO", "Liberia": "LBR",
    "Libya": "LBY", "Liechtenstein": "LIE", "Lithuania": "LTU",
    "Luxembourg": "LUX", "Macao SAR, China": "MAC",
    "Madagascar": "MDG", "Malawi": "MWI", "Malaysia": "MYS",
    "Maldives": "MDV", "Mali": "MLI", "Malta": "MLT",
    "Marshall Islands": "MHL", "Mauritania": "MRT", "Mauritius": "MUS",
    "Mexico": "MEX", "Micronesia (Federated States of)": "FSM",
    "Micronesia, Fed. Sts.": "FSM", "Moldova (Republic of)": "MDA",
    "Moldova": "MDA", "Monaco": "MCO", "Mongolia": "MNG",
    "Montenegro": "MNE", "Morocco": "MAR", "Mozambique": "MOZ",
    "Myanmar": "MMR", "Burma": "MMR", "Namibia": "NAM", "Nauru": "NRU",
    "Nepal": "NPL", "Netherlands": "NLD", "New Zealand": "NZL",
    "Nicaragua": "NIC", "Niger": "NER", "Nigeria": "NGA",
    "North Macedonia": "MKD", "Macedonia": "MKD", "Norway": "NOR",
    "Oman": "OMN", "Pakistan": "PAK", "Palau": "PLW",
    "State of Palestine": "PSE", "West Bank and Gaza": "PSE",
    "Panama": "PAN", "Papua New Guinea": "PNG", "Paraguay": "PRY",
    "Peru": "PER", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
    "Qatar": "QAT", "Romania": "ROU", "Russian Federation": "RUS",
    "Russia": "RUS", "Rwanda": "RWA", "Saint Kitts and Nevis": "KNA",
    "Saint Lucia": "LCA", "Saint Vincent and the Grenadines": "VCT",
    "Samoa": "WSM", "San Marino": "SMR", "Sao Tome and Principe": "STP",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB",
    "Seychelles": "SYC", "Sierra Leone": "SLE", "Singapore": "SGP",
    "Slovakia": "SVK", "Slovenia": "SVN", "Solomon Islands": "SLB",
    "Somalia": "SOM", "South Africa": "ZAF", "South Sudan": "SSD",
    "Spain": "ESP", "Sri Lanka": "LKA", "Sudan": "SDN", "Suriname": "SUR",
    "Sweden": "SWE", "Switzerland": "CHE", "Syrian Arab Republic": "SYR",
    "Syria": "SYR", "Tajikistan": "TJK",
    "Tanzania (United Republic of)": "TZA", "Tanzania": "TZA",
    "Thailand": "THA", "Timor-Leste": "TLS", "Togo": "TGO", "Tonga": "TON",
    "Trinidad and Tobago": "TTO", "Tunisia": "TUN",
    "Turkiye": "TUR", "Türkiye": "TUR", "Turkey": "TUR",
    "Turkmenistan": "TKM", "Tuvalu": "TUV", "Uganda": "UGA",
    "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR",
    "United States": "USA", "United States of America": "USA",
    "Uruguay": "URY", "Uzbekistan": "UZB", "Vanuatu": "VUT",
    "Venezuela (Bolivarian Republic of)": "VEN", "Venezuela, RB": "VEN",
    "Venezuela": "VEN", "Viet Nam": "VNM", "Vietnam": "VNM",
    "Yemen, Rep.": "YEM", "Yemen": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE",
}


_WB_COUNTRIES_URL = "https://api.worldbank.org/v2/country/all"
_WB_INDICATOR_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}"


def _get_wb_countries(timeout: int = 30) -> dict[str, str]:
    """Return {iso3: name} for all WB member countries (excludes aggregates)."""
    result: dict[str, str] = {}
    page = 1
    while True:
        try:
            resp = requests.get(
                _WB_COUNTRIES_URL,
                params={"format": "json", "per_page": 300, "page": page},
                timeout=timeout,
            )
            resp.raise_for_status()
            body = resp.json()
            if len(body) < 2 or not body[1]:
                break
            for rec in body[1]:
                iso3 = (rec.get("id") or "").strip()
                region = rec.get("region") or {}
                if len(iso3) == 3 and region.get("id") != "NA":
                    result[iso3] = rec.get("name", iso3)
            total_pages = body[0].get("pages", 1)
            if page >= total_pages:
                break
            page += 1
        except Exception as exc:
            log.warning("WB countries page %d: %s", page, exc)
            break
    log.info("WB country registry: %d countries", len(result))
    return result


def collect_world_bank(cfg: dict) -> pd.DataFrame:
    """Batch-fetch all WB indicators for ALL countries (one API call per indicator)."""
    indicators: dict[str, str] = cfg["sources"]["world_bank"]["indicators"]
    start_year = cfg["years"]["start"]
    end_year = cfg["years"]["end"]
    min_data_years = cfg.get("min_data_years", 5)

    wb_countries = _get_wb_countries()
    valid_iso3 = set(wb_countries.keys())
    log.info("World Bank: fetching %d indicators for all countries", len(indicators))

    frames: list[pd.DataFrame] = []
    for ind_code, col_name in indicators.items():
        url = _WB_INDICATOR_URL.format(indicator=ind_code)
        params: dict = {"format": "json", "per_page": 1000,
                        "date": f"{start_year}:{end_year}"}
        rows: list[dict] = []
        page = 1
        while True:
            params["page"] = page
            try:
                resp = requests.get(url, params=params, timeout=60)
                resp.raise_for_status()
                body = resp.json()
                if len(body) < 2 or not body[1]:
                    break
                for rec in body[1]:
                    iso3 = (rec.get("countryiso3code") or "").strip()
                    if iso3 not in valid_iso3:
                        continue
                    val = rec.get("value")
                    yr = rec.get("date")
                    if yr and val is not None:
                        rows.append({"iso3": iso3, "year": int(yr), col_name: float(val)})
                total_pages = body[0].get("pages", 1)
                if page >= total_pages:
                    break
                page += 1
                time.sleep(0.15)
            except Exception as exc:
                log.warning("WB %s page %d: %s", ind_code, page, exc)
                break
        if rows:
            frames.append(pd.DataFrame(rows))
        log.info("  WB %s (%s): %d records", ind_code, col_name, len(rows))

    if not frames:
        log.error("World Bank: no data fetched!")
        df = pd.DataFrame(columns=["iso3", "year"] + list(indicators.values()))
        out_path = ROOT / cfg["paths"]["raw"] / "world_bank.csv"
        df.to_csv(out_path, index=False)
        return df

    df = frames[0]
    for frame in frames[1:]:
        df = df.merge(frame, on=["iso3", "year"], how="outer")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    ind_cols = [c for c in df.columns if c not in ("iso3", "year")]
    if ind_cols:
        counts = df.groupby("iso3")[ind_cols].count().max(axis=1)
        df = df[df["iso3"].isin(counts[counts >= min_data_years].index)]

    df = df.sort_values(["iso3", "year"]).reset_index(drop=True)
    out_path = ROOT / cfg["paths"]["raw"] / "world_bank.csv"
    df.to_csv(out_path, index=False)
    log.info("World Bank: %d rows, %d countries", len(df), df["iso3"].nunique())

    names_df = pd.DataFrame(
        [(k, v) for k, v in wb_countries.items() if k in set(df["iso3"])],
        columns=["iso3", "country_name"],
    )
    (ROOT / cfg["paths"]["raw"] / "country_names.csv").parent.mkdir(parents=True, exist_ok=True)
    names_df.to_csv(ROOT / cfg["paths"]["raw"] / "country_names.csv", index=False)
    log.info("country_names.csv: %d entries", len(names_df))
    return df


# ── 2. UNDP HDI ────────────────────────────────────────────────────────────────

def collect_undp_hdi(cfg: dict) -> pd.DataFrame:
    """
    Download UNDP HDI Excel and extract HDI scores for all available countries.
    Tries to find an ISO3 column; falls back to country-name mapping.
    """
    url = cfg["sources"]["undp_hdi"]["url"]

    try:
        log.info("UNDP HDI: downloading ...")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        xl = pd.ExcelFile(io.BytesIO(resp.content))
        sheet = next((s for s in xl.sheet_names if "HDI" in s.upper()), xl.sheet_names[0])
        raw = xl.parse(sheet, header=None)
        header_row = 4
        for i, row in raw.iterrows():
            if any("country" in str(c).lower() for c in row.values):
                header_row = i
                break
        df_xl = xl.parse(sheet, header=header_row)
        df_xl.columns = [str(c).strip() for c in df_xl.columns]

        country_col = next(
            (c for c in df_xl.columns if "country" in c.lower()), None
        )
        iso_col = next(
            (c for c in df_xl.columns
             if c.strip().upper() in ("ISO3", "ISO", "CODE", "ISO CODE", "COUNTRY CODE")),
            None,
        )
        year_cols = [c for c in df_xl.columns
                     if str(c).strip().isdigit() and 2000 <= int(c) <= 2030]
        hdi_col = max(year_cols, key=int) if year_cols else next(
            (c for c in df_xl.columns if "hdi" in c.lower()), None
        )
        hdi_year = int(hdi_col) if hdi_col and str(hdi_col).strip().isdigit() else 2022

        rows = []
        for _, row in df_xl.iterrows():
            iso3 = None
            if iso_col:
                raw_iso = str(row.get(iso_col, "")).strip().upper()
                if len(raw_iso) == 3 and raw_iso.isalpha():
                    iso3 = raw_iso
            if iso3 is None and country_col:
                name = str(row.get(country_col, "")).strip()
                iso3 = _NAME_TO_ISO3.get(name)
            if iso3 is None:
                continue
            hdi_val = None
            if hdi_col is not None:
                try:
                    hdi_val = float(row[hdi_col])
                except (ValueError, TypeError):
                    pass
            rows.append({"iso3": iso3, "year": hdi_year, "hdi_score": hdi_val})

        df_hdi = pd.DataFrame(rows).drop_duplicates(["iso3", "year"])

    except Exception as exc:
        log.warning("UNDP HDI download failed (%s); empty fallback.", exc)
        df_hdi = pd.DataFrame(columns=["iso3", "year", "hdi_score"])

    out_path = ROOT / cfg["paths"]["raw"] / "undp_hdi.csv"
    df_hdi.to_csv(out_path, index=False)
    log.info("UNDP HDI: %d rows saved", len(df_hdi))
    return df_hdi


# ── 3. WHO GHO ─────────────────────────────────────────────────────────────────

def collect_who_gho(cfg: dict) -> pd.DataFrame:
    """Fetch WHO GHO indicators via OData REST API (all countries, no filter)."""
    base_url = cfg["sources"]["who_gho"]["base_url"]
    indicators: dict[str, str] = cfg["sources"]["who_gho"]["indicators"]
    start_year = cfg["years"]["start"]
    end_year = cfg["years"]["end"]

    frames: list[pd.DataFrame] = []
    for code, col_name in indicators.items():
        url = f"{base_url}/{code}?$format=json&$top=50000"
        try:
            log.info("WHO GHO: fetching %s", code)
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json().get("value", [])
            rows = []
            for rec in data:
                try:
                    year = int(rec.get("TimeDim", 0))
                    iso3 = (rec.get("SpatialDim") or "").strip()
                    val = rec.get("NumericValue")
                    if start_year <= year <= end_year and len(iso3) == 3 and val is not None:
                        rows.append({"iso3": iso3, "year": year, col_name: float(val)})
                except (ValueError, TypeError):
                    continue
            if rows:
                frames.append(pd.DataFrame(rows))
            log.info("  WHO GHO %s: %d records", code, len(rows))
        except Exception as exc:
            log.warning("WHO GHO %s failed: %s", code, exc)

    if frames:
        df_who = frames[0]
        for frame in frames[1:]:
            df_who = df_who.merge(frame, on=["iso3", "year"], how="outer")
    else:
        log.warning("WHO GHO: all indicators failed; creating empty placeholder.")
        df_who = pd.DataFrame(columns=["iso3", "year"] + list(indicators.values()))

    out_path = ROOT / cfg["paths"]["raw"] / "who_gho.csv"
    df_who.to_csv(out_path, index=False)
    log.info("WHO GHO: %d rows, %d countries", len(df_who),
             df_who["iso3"].nunique() if "iso3" in df_who.columns else 0)
    return df_who


# ── 4. Yale EPI ────────────────────────────────────────────────────────────────

def collect_yale_epi(cfg: dict) -> pd.DataFrame:
    """Download Yale EPI Excel and extract scores for all available countries."""
    url = cfg["sources"]["yale_epi"]["url"]

    try:
        log.info("Yale EPI: downloading ...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        df_xl = pd.read_excel(io.BytesIO(resp.content))
        df_xl.columns = [str(c).strip() for c in df_xl.columns]

        # Try to find an ISO3 column first, then fall back to country name mapping
        iso_col = next(
            (c for c in df_xl.columns
             if c.strip().upper() in ("ISO", "ISO3", "CODE", "ISO CODE", "ISOCODE")),
            None,
        )
        country_col = next((c for c in df_xl.columns if "country" in c.lower()), None)
        score_col = next((c for c in df_xl.columns if "epi" in c.lower() and "score" in c.lower()), None)
        air_col = next((c for c in df_xl.columns if "air" in c.lower()), None)
        eco_col = next((c for c in df_xl.columns if "ecosystem" in c.lower()), None)
        ws_col = next((c for c in df_xl.columns if "water" in c.lower()), None)

        rows = []
        for _, row in df_xl.iterrows():
            iso3 = None
            if iso_col:
                raw_iso = str(row.get(iso_col, "")).strip().upper()
                if len(raw_iso) == 3 and raw_iso.isalpha():
                    iso3 = raw_iso
            if iso3 is None and country_col:
                name = str(row.get(country_col, "")).strip()
                iso3 = _NAME_TO_ISO3.get(name)
            if iso3 is None:
                continue
            rows.append({
                "iso3": iso3,
                "year": 2024,
                "epi_score": _safe_float(row.get(score_col)),
                "air_quality_score": _safe_float(row.get(air_col)),
                "ecosystem_vitality_score": _safe_float(row.get(eco_col)),
                "water_sanitation_score": _safe_float(row.get(ws_col)),
            })

        df_epi = pd.DataFrame(rows).drop_duplicates(["iso3", "year"])

    except Exception as exc:
        log.warning("Yale EPI download failed (%s); empty fallback.", exc)
        df_epi = pd.DataFrame(columns=["iso3", "year", "epi_score",
                                        "air_quality_score", "ecosystem_vitality_score",
                                        "water_sanitation_score"])

    out_path = ROOT / cfg["paths"]["raw"] / "yale_epi.csv"
    df_epi.to_csv(out_path, index=False)
    log.info("Yale EPI: %d rows, %d countries", len(df_epi),
             df_epi["iso3"].nunique() if "iso3" in df_epi.columns else 0)
    return df_epi


def _safe_float(val) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    cfg = load_config()

    raw_dir = ROOT / cfg["paths"]["raw"]
    raw_dir.mkdir(parents=True, exist_ok=True)

    collect_world_bank(cfg)
    collect_undp_hdi(cfg)
    collect_who_gho(cfg)
    collect_yale_epi(cfg)

    log.info("Data collection complete. Raw files in %s", raw_dir)


if __name__ == "__main__":
    main()
