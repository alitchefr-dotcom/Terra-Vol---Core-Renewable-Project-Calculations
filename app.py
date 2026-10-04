import streamlit as st
import pandas as pd
import os
import requests
import base64
import math
from datetime import date
from io import BytesIO

# ---------------------------------------------------------
# 1. חוק ברזל בסטרימלייט: st.set_page_config חייב להיות ראשון!
# ---------------------------------------------------------
possible_logo_names = ["logo.png", "logo.png.png", "Logo.png"]
logo_path = None
for name in possible_logo_names:
    full_path = os.path.join(os.path.dirname(__file__), name)
    if os.path.exists(full_path):
        logo_path = full_path
        break

st.set_page_config(
    page_title="Terra Vol - Renewable Energy Budgeting",
    page_icon=logo_path if logo_path else "⚡",
    layout="wide"
)

from calc import calculate_project_costs

# ---------------------------------------------------------
# מנגנון אבטחה וסיסמה (Authentication) עם תיקון לוגאוט נקי
# ---------------------------------------------------------
def check_password():
    def password_entered():
        if (
            st.session_state.get("username") in st.secrets.get("passwords", {})
            and st.session_state.get("password") == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            st.session_state.pop("password", None)
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("## 🔐 Terra Vol — Secure Login")
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Login", on_click=password_entered)
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 User not found or incorrect password")
    return False

if not check_password():
    st.stop()

if st.sidebar.button("התנתק / Logout"):
    st.session_state.pop("password_correct", None)
    st.rerun()

# ---------------------------------------------------------
# לוגו ושפה
# ---------------------------------------------------------
def get_base64_of_bin_file(bin_file):
    if not bin_file or not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_of_bin_file(logo_path) if logo_path else ""

if logo_base64:
    st.sidebar.markdown(
        f'<div style="text-align: center; margin-bottom: 1.5rem;"><img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: auto;" /></div>',
        unsafe_allow_html=True
    )

st.sidebar.header("🌐 שפה / Language")
lang_options = {"עברית": "he", "English": "en"}
selected_lang_label = st.sidebar.radio("בחר שפה / Select Language:", list(lang_options.keys()), index=0, key="lang_radio_select")
current_lang = lang_options[selected_lang_label]
is_hebrew = (current_lang == "he")

T = {
    "he": {
        "caption": "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, תנאי סחר, רגולציה וקיימות",
        "incoterm_label": "תנאי סחר מסחרי (אחריות ספק):",
        "currency_label": "מטבע תצוגה ראשי:",
        "origin_port": "נמל מוצא:",
        "dest_port": "נמל פריקה (יעד):",
        "dest_country": "מדינת יעד לפרויקט:",
        "site_label": "שם אתר הפרויקט:",
        "site_ph": "פרויקט אלפא / אתר פרויקט",
        "vat_label": "שיעור מע\"מ",
        "vat_rec": "אחוז החזר מע\"מ (%)",
        "vat_sup": "המע\"מ משולם על ידי הספק במסגרת תנאי המסחר",
        "eq_header": "הגדרת רכיבי הציוד וכמויות לפרויקט",
        "eq_info": "הזן את כמויות מכולות הסוללה, הממירים, השנאים ועלויות הייצור במפעל (EXW).",
        "tab1": "📋 תמהיל ציוד וכמויות לפרויקט",
        "tab2": "⚓ שרשרת אספקה ותנאי סחר",
        "tab3": "📦 אחסנה, השהיות והובלת משאיות לאתר",
        "tab4": "⚖️ רגולציה, קיימות ואישורים",
        "tab5_eu": "🗺 הנחות מסלולים באירופה",
        "tab_projects": "📂 פרויקטי אנרגיה תשתיות ואגירה",
        "tab_summary": "📊 דוח בקרה תקציבית ופחמנית",
        "summary_title": "📊 דוח בקרה פיננסית וסביבתית (Carbon & Cost)",
        "breakdown_title": "📋 פירוט רכיבי תקציב וטביעת רגל פחמנית",
        "excel_btn": "📥 הורד דוח פיננסי מלא לאקסל",
        "projects_header": "📂 פרויקטי אנרגיה תשתיות ואגירה (ניהול ומעקב מלא באירופה)",
        "col_item": "רכיב עלות בפרויקט",
        "col_qty": "כמות / בסיס חישוב",
        "col_unit": "עלות ליחידה (קטגוריה)",
        "col_total": "סה\"כ סעיף",
        "qty_differential": "דיפרנציאלי",
        "qty_expense": "הוצאה",
        "qty_survey": "סקר",
        "qty_global": "גלובלי"
    },
    "en": {
        "caption": "Professional Project Calculator for Target Costs, Incoterms, Regulation & Sustainability",
        "incoterm_label": "Commercial Incoterm (Supplier Scope):",
        "currency_label": "Main Display Currency:",
        "origin_port": "Origin Port:",
        "dest_port": "Destination Port:",
        "dest_country": "Project Destination Country:",
        "site_label": "Project Site Name:",
        "site_ph": "Project Site Name / Alpha Site",
        "vat_label": "VAT Rate",
        "vat_rec": "VAT Recovery Rate (%)",
        "vat_sup": "VAT paid by supplier under commercial terms",
        "eq_header": "Equipment Mix & Quantities Configuration",
        "eq_info": "Enter BESS container quantities, inverters, transformers, and factory EXW production costs.",
        "tab1": "📋 Equipment Mix & Quantities",
        "tab2": "⚓ Supply Chain & Incoterms",
        "tab3": "📦 Storage, Demurrage & Inland Drayage",
        "tab4": "⚖️ Regulation, Sustainability & Approvals",
        "tab5_eu": "🗺️ European Route Options",
        "tab_projects": "📂 Infrastructure & Energy Projects",
        "tab_summary": "📊 Budget & Carbon Control Report",
        "summary_title": "📊 Financial & Environmental Control Report (Carbon & Cost)",
        "breakdown_title": "📋 Project Budget & Carbon Footprint Breakdown",
        "excel_btn": "📥 Download Full Excel Report",
        "projects_header": "📂 Infrastructure & Energy Projects (Full European Tracking)",
        "col_item": "Project Cost Item",
        "col_qty": "Basis / Qty",
        "col_unit": "Unit Cost (Category)",
        "col_total": "Total Amount",
        "qty_differential": "Differential",
        "qty_expense": "Expense",
        "qty_survey": "Survey",
        "qty_global": "Global"
    }
}

txt = T[current_lang]
direction_css = "rtl" if is_hebrew else "ltr"
text_align_css = "right" if is_hebrew else "left"

st.markdown(
    f"""
    <style>
    .stApp {{ direction: {direction_css}; text-align: {text_align_css}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    h1, h2, h3, h4, h5, h6, p, label {{ direction: {direction_css}; text-align: {text_align_css}; }}
    .stTextInput label, .stSelectbox label, .stNumberInput label {{ direction: {direction_css}; text-align: {text_align_css}; width: 100%; font-weight: 600; }}
    input[type=number] {{ direction: ltr; text-align: right; }}
    
    .metric-container {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }}
    .metric-title {{
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
        text-align: {text_align_css};
    }}
    .metric-value {{
        font-size: 1.5rem;
        color: #1e3d59;
        font-weight: 700;
        direction: ltr;
        text-align: right;
    }}
    
    .custom-finance-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        margin-bottom: 2rem;
        background-color: white;
        color: #1e293b;
        font-size: 0.95rem;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    .custom-finance-table th {{
        background-color: #f1f5f9;
        color: #1e3d59;
        font-weight: 700;
        padding: 12px 16px;
        text-align: {text_align_css};
        border-bottom: 2px solid #e2e8f0;
    }}
    .custom-finance-table td {{
        padding: 12px 16px;
        border-bottom: 1px solid #e2e8f0;
        text-align: {text_align_css};
    }}
    .custom-finance-table tr.total-row {{
        background-color: #f8fafc;
        font-weight: 700;
        border-top: 2px solid #cbd5e1;
    }}
    .center {{ text-align: center; }}
    .left {{ text-align: left; }}
    .ltr-val {{
        direction: ltr;
        unicode-bidi: embed;
        display: inline-block;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" style="width: 140px; height: auto;" />' if logo_base64 else '⚡'

header_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; width: 100%; direction: {direction_css}; margin-bottom: 0rem;">
    <h1 style="margin: 0; font-size: 3rem; font-weight: 700; color: #1e3d59;">Terra Vol</h1>
    <div>{logo_img_tag}</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.caption(txt["caption"])

ORIGIN_PORTS = {
    "SHA": "שאנגחאי (Shanghai)" if is_hebrew else "Shanghai, China",
    "NGB": "נינגבו (Ningbo)" if is_hebrew else "Ningbo, China",
    "SZX": "שנג'ן (Shenzhen)" if is_hebrew else "Shenzhen, China",
    "TAO": "צ'ינגדאו (Qingdao)" if is_hebrew else "Qingdao, China"
}

DESTINATION_PORTS = {
    "IL": [
        ("HAIF", "נמל חיפה (קבוצת עדני)" if is_hebrew else "Haifa Port (Adani Group)"),
        ("BAY", "נמל המפרץ (SIPG - חיפה)" if is_hebrew else "Bay Port (SIPG — Haifa)"),
        ("ASHD", "נמל אשדוד (הממשלתי)" if is_hebrew else "Ashdod Port (Government)"),
        ("TIL", "מסוף TIL (קבוצת MSC - אשדוד)" if is_hebrew else "TIL Terminal (MSC Group — Ashdod)")
    ],
    "RO": [("CT", "קונסטנצה, רומניה (Constanța)" if is_hebrew else "Constanța, Romania"), ("BOJ", "בורגס, בולגריה (Burgas)" if is_hebrew else "Burgas, Bulgaria")],
    "PL": [("GDN", "גדנסק, פולין (Gdansk)" if is_hebrew else "Gdansk, Poland"), ("GDY", "גדיניה, פולין (Gdynia)" if is_hebrew else "Gdynia, Poland")],
    "DE": [("HAM", "המבורג, גרמניה (Hamburg)" if is_hebrew else "Hamburg, Germany"), ("BRV", "ברמרהאפן, גרמניה (Bremerhaven)" if is_hebrew else "Bremerhaven, Germany")],
    "SE": [("GOT", "גטבורג, שוודיה (Gothenburg)" if is_hebrew else "Gothenburg, Sweden"), ("STO", "סטוקהולם, שוודיה (Stockholm)" if is_hebrew else "Stockholm, Sweden")],
    "GR": [("PIR", "פיראוס, יוון (Piraeus)" if is_hebrew else "Piraeus, Greece"), ("THE", "סלוניקי, יוון (Thessaloniki)" if is_hebrew else "Thessaloniki, Greece")],
    "ES": [("VLC", "ולנסיה, ספרד (Valencia)" if is_hebrew else "Valencia, Spain"), ("BCN", "ברצלונה, ספרד (Barcelona)" if is_hebrew else "Barcelona, Spain")],
    "IT": [("GOA", "ג'נואה, איטליה (Genoa)" if is_hebrew else "Genoa, Italy"), ("TRS", "טרייסטה, איטליה (Trieste)" if is_hebrew else "Trieste, Italy")],
    "BG": [("VAR", "וורנה, בולגריה (Varna)" if is_hebrew else "Varna, Bulgaria"), ("BOJ", "בורגס, בולגריה (Burgas)" if is_hebrew else "Burgas, Bulgaria")],
    "HU": [("BUD", "בודפשט, הונגריה (Budapest - Rail/Multimodal)" if is_hebrew else "Budapest, Hungary (Rail/Multimodal)")],
    "FI": [("HEL", "הלסינקי, פינלנד (Helsinki)" if is_hebrew else "Helsinki, Finland"), ("KTK", "קוטקה, פינלנד (Kotka)" if is_hebrew else "Kotka, Finland")],
    "OTHER": [("RTM", "רוטרדם, הולנד (Rotterdam)" if is_hebrew else "Rotterdam, Netherlands"), ("ANR", "אנטוורפן, בלגיה (Antwerp)" if is_hebrew else "Antwerp, Belgium")]
}

PORT_COORDINATES = {
    "HAIF": (32.8192, 34.9900), "BAY": (32.8250, 35.0100),
    "ASHD": (31.8333, 34.6500), "TIL": (31.8200, 34.6400),
    "CT": (44.1792, 28.6500), "BOJ": (42.5048, 27.4626),
    "GDN": (54.3520, 18.6466), "GDY": (54.5189, 18.5305),
    "HAM": (53.5511, 9.9937), "BRV": (53.5705, 8.5771),
    "GOT": (57.7089, 11.9746), "STO": (59.3293, 18.0686),
    "PIR": (37.9475, 23.6378), "THE": (40.6401, 22.9444),
    "VLC": (39.4699, -0.3763), "BCN": (41.3851, 2.1734),
    "GOA": (44.4056, 8.9463), "TRS": (45.6495, 13.7768),
    "VAR": (43.2141, 27.9147), "BUD": (47.4979, 19.0402),
    "HEL": (60.1699, 24.9384), "KTK": (60.4667, 26.9333),
    "RTM": (51.9244, 4.4777), "ANR": (51.2194, 4.4025)
}

def calculate_road_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c * 1.3

VAT_RATES = {
    "IL": 18.0, "RO": 19.0, "PL": 23.0, "DE": 19.0, "SE": 25.0, 
    "GR": 24.0, "ES": 21.0, "IT": 22.0, "BG": 20.0, "HU": 27.0,
    "FI": 25.5, "OTHER": 0.0
}
DEFAULT_INSURANCE_RATES = {
    "IL": 0.08, "RO": 0.15, "PL": 0.15, "DE": 0.15, "SE": 0.15, 
    "GR": 0.15, "ES": 0.15, "IT": 0.15, "BG": 0.15, "HU": 0.15,
    "FI": 0.15, "OTHER": 0.15
}
DEFAULT_FREE_DAYS = {
    "IL": 4, "RO": 7, "PL": 7, "DE": 7, "SE": 7, 
    "GR": 7, "ES": 7, "IT": 7, "BG": 7, "HU": 7,
    "FI": 7, "OTHER": 7
}

COUNTRY_CODES = ["IL", "RO", "PL", "DE", "SE", "GR", "ES", "IT", "BG", "HU", "FI", "OTHER"]
COUNTRY_NAMES = {
    "IL": "ישראל" if is_hebrew else "Israel",
    "RO": "רומניה" if is_hebrew else "Romania",
    "PL": "פולין" if is_hebrew else "Poland",
    "DE": "גרמניה" if is_hebrew else "Germany",
    "SE": "שוודיה" if is_hebrew else "Sweden",
    "GR": "יוון" if is_hebrew else "Greece",
    "ES": "ספרד" if is_hebrew else "Spain",
    "IT": "איטליה" if is_hebrew else "Italy",
    "BG": "בולגריה" if is_hebrew else "Bulgaria",
    "HU": "הונגריה" if is_hebrew else "Hungary",
    "FI": "פינלנד" if is_hebrew else "Finland",
    "OTHER": "אחר / מותאם" if is_hebrew else "Other / Custom",
}

incoterm_map = {
    "DDP": "DDP (אחריות מלאה כולל מיסים)" if is_hebrew else "DDP (Delivered Duty Paid — Full Scope)",
    "DAP": "DAP (מסירה באתר ללא פריקה ומכס ומע\"מ יבוא)" if is_hebrew else "DAP (Delivered at Place — Excl. Unloading, Duty & Import VAT)",
    "CIF": "CIF (עלות, ביטוח והובלה ימית)" if is_hebrew else "CIF (Cost, Insurance and Freight)",
    "FOB": "FOB (מסירה על הסיפון בנמל מוצא)" if is_hebrew else "FOB (Free On Board)",
    "EXW": "EXW (איסוף עצמי ממפעל הספק)" if is_hebrew else "EXW (Ex Works — Factory Pickup)"
}

selected_incoterm_code = st.sidebar.selectbox(txt["incoterm_label"], list(incoterm_map.keys()), format_func=lambda k: incoterm_map[k], key="sidebar_incoterm_code")
display_currency = st.sidebar.selectbox(txt["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"], key="sidebar_currency")

forecast_date = st.sidebar.date_input("תאריך יעד לאספקה באתר:" if is_hebrew else "Delivery Target Date:", value=date(2027, 6, 30), key="sidebar_forecast_date")
market_scenario_map = {
    "CONS": "שמרני (+8.0% לשנה)" if is_hebrew else "Conservative (+8.0% p.a.)",
    "BASE": "בסיסי (+4.5% לשנה)" if is_hebrew else "Baseline (+4.5% p.a.)",
    "STABLE": "יציב / ללא שינוי (0.0%)" if is_hebrew else "Stable / No Change (0.0%)"
}
selected_market_code = st.sidebar.selectbox("תחזית אינפלציה ומגמת שוק:" if is_hebrew else "Inflation & Market Trend Scenario:", list(market_scenario_map.keys()), format_func=lambda k: market_scenario_map[k], key="sidebar_market_code")

today_date = date.today()
delta_days = (forecast_date - today_date).days
years_diff = max(0.0, delta_days / 365.25)
annual_inflation = 0.08 if selected_market_code == "CONS" else (0.045 if selected_market_code == "BASE" else 0.0)
trend_multiplier = (1.0 + annual_inflation) ** years_diff

@st.cache_data(ttl=300)
def fetch_live_exchange_rates():
    try:
        response = requests.get("https://api.frankfurter.dev/v1/latest?from=USD&to=EUR,ILS", timeout=5)
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            return rates.get("EUR", 0.92), rates.get("ILS", 3.70)
    except Exception:
        pass
    return None, None

live_eur, live_ils = fetch_live_exchange_rates()
if live_eur is None or live_ils is None:
    st.sidebar.warning("⚠️ שרת המרה חי נכשל. נעשה שימוש שערי המרה חלופיים (EUR: 0.92, ILS: 3.70)." if is_hebrew else "⚠️ Live FX API failed. Using fallback rates.")
    live_eur, live_ils = 0.92, 3.70

if "fx_eur" not in st.session_state:
    st.session_state["fx_eur"] = live_eur
if "fx_ils" not in st.session_state:
    st.session_state["fx_ils"] = live_ils

usd_to_eur = st.sidebar.number_input("שער המרה USD ל־EUR:" if is_hebrew else "USD to EUR Exchange Rate:", step=0.01, min_value=0.0001, format="%.4f", key="fx_eur")
usd_to_ils = st.sidebar.number_input("שער המרה USD ל־ILS:" if is_hebrew else "USD to ILS Exchange Rate:", step=0.01, min_value=0.0001, format="%.4f", key="fx_ils")

def refresh_fx():
    fetch_live_exchange_rates.clear()
    ne, ni = fetch_live_exchange_rates()
    if ne and ni:
        st.session_state["fx_eur"] = ne
        st.session_state["fx_ils"] = ni

st.sidebar.button("🔄 רענן שערים" if is_hebrew else "🔄 Refresh Rates", on_click=refresh_fx)

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

curr_symbol = "$" if "USD" in display_currency else ("€" if "EUR" in display_currency else "₪")

if "sidebar_dest_country_code" not in st.session_state:
    st.session_state["sidebar_dest_country_code"] = "IL" if is_hebrew else "RO"

dest_country_code = st.sidebar.selectbox(
    txt["dest_country"],
    COUNTRY_CODES,
    format_func=lambda k: COUNTRY_NAMES[k],
    key="sidebar_dest_country_code"
)
dest_country_name = COUNTRY_NAMES[dest_country_code]
is_european_dest = (dest_country_code != "IL")

if dest_country_code == "OTHER":
    st.sidebar.warning("⚠️ שיעור המע\"מ מוגדר כ־0% (יעד מותאם)." if is_hebrew else "⚠ VAT rate is set to 0% (Custom destination).")

if is_european_dest:
    CARRIER_FUEL_SURCHARGES = {
        "ZIM": {"name": "ZIM (שירות מועדף למטעני חומ\"ס וגמישות)" if is_hebrew else "ZIM (Preferred DG & Flexible Service)", "bess_mult": 1.0, "dthc_mult": 1.0},
        "MSC": {"name": "MSC (תעריפים מועדפים לנמלי אירופה)" if is_hebrew else "MSC (Preferred European Tariffs)", "bess_mult": 0.82, "dthc_mult": 0.90},
        "CMA": {"name": "CMA CGM (שירות מרכזי למערב ומרכז אירופה)" if is_hebrew else "CMA CGM (Core West/Central Europe Service)", "bess_mult": 0.92, "dthc_mult": 0.92},
        "COSCO": {"name": "COSCO Shipping (שירות אסיאתי-אירופאי ישיר)" if is_hebrew else "COSCO Shipping (Direct Asia-Europe Service)", "bess_mult": 0.88, "dthc_mult": 0.88},
        "HAPAG": {"name": "Hapag-Lloyd (סטנדרטי מזרח-מערב)" if is_hebrew else "Hapag-Lloyd (Standard East-West)", "bess_mult": 0.95, "dthc_mult": 0.95},
        "ONE": {"name": "ONE - Ocean Network Express", "bess_mult": 0.90, "dthc_mult": 0.90},
        "EVG": {"name": "Evergreen Marine", "bess_mult": 0.89, "dthc_mult": 0.89},
        "SPOT": {"name": "שוק חופשי / ספוט" if is_hebrew else "Spot Market / Free Carrier", "bess_mult": 0.90, "dthc_mult": 0.90}
    }
else:
    CARRIER_FUEL_SURCHARGES = {
        "ZIM": {"name": "ZIM (שירות מועדף למטעני חומ\"ס וגמישות)" if is_hebrew else "ZIM (Preferred DG & Flexible Service)", "bess_mult": 1.0, "dthc_mult": 1.0},
        "MSC": {"name": "MSC (תעריפים מועדפים)" if is_hebrew else "MSC (Preferred Tariffs)", "bess_mult": 0.82, "dthc_mult": 0.90},
        "HAPAG": {"name": "Hapag-Lloyd (סטנדרטי)" if is_hebrew else "Hapag-Lloyd (Standard)", "bess_mult": 0.95, "dthc_mult": 0.95},
        "SPOT": {"name": "שוק חופשי / ספוט" if is_hebrew else "Spot Market / Free Carrier", "bess_mult": 0.90, "dthc_mult": 0.90}
    }

if is_european_dest:
    tab1, tab2, tab3, tab4, tab5_eu, tab_projects, tab_summary = st.tabs([
        txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"], txt["tab5_eu"], txt["tab_projects"], txt["tab_summary"]
    ])
else:
    tab1, tab2, tab3, tab4, tab_summary = st.tabs([
        txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"], txt["tab_summary"]
    ])
    tab5_eu = None
    tab_projects = None

with tab1:
    st.subheader(txt["eq_header"])
    st.info(txt["eq_info"])

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        origin_port_code = st.selectbox(txt["origin_port"], list(ORIGIN_PORTS.keys()), format_func=lambda k: ORIGIN_PORTS[k], key="tab1_origin_port_code")
        available_dest_tuples = DESTINATION_PORTS.get(dest_country_code, DESTINATION_PORTS["OTHER"])
        dest_port_code = st.selectbox(
            txt["dest_port"],
            [t[0] for t in available_dest_tuples],
            format_func=lambda code: next(t[1] for t in available_dest_tuples if t[0] == code),
            key=f"tab1_dest_port_{dest_country_code}"
        )
        site_address = st.text_input(txt["site_label"], key="site_name_input", placeholder=txt["site_ph"])

        st.markdown("##### 📍 פרטי מיקום מדויקים של אתר הפרויקט:" if is_hebrew else "##### 📍 Detailed Project Site Location:")
        site_street_address = st.text_input("כתובת אתר מלאה (רחוב ומספר):" if is_hebrew else "Full Street Address:", key="site_street_address_input")
        site_postal_code = st.text_input("מיקוד (Postal Code):" if is_hebrew else "Postal Code:", key="site_postal_code_input")
        site_coordinates = st.text_input("קואורדינטות GPS (Latitude, Longitude):" if is_hebrew else "GPS Coordinates (Lat, Long):", key="site_coordinates_input", placeholder="32.0853, 34.7818")

        calculated_distance_km = 50.0
        if site_coordinates:
            try:
                lat_str, lon_str = site_coordinates.replace("°", "").split(",")
                s_lat = float(lat_str.strip())
                s_lon = float(lon_str.strip())
                if dest_port_code in PORT_COORDINATES:
                    p_lat, p_lon = PORT_COORDINATES[dest_port_code]
                    calculated_distance_km = calculate_road_distance_km(p_lat, p_lon, s_lat, s_lon)
                    st.info(f"📍 **מרחק נסיעה מחושב מהנמל ({dest_port_code}) לאתר:** כ־{calculated_distance_km:,.1f} ק\"מ" if is_hebrew else f"📍 Calculated road distance: ~{calculated_distance_km:,.1f} km")
                else:
                    st.warning("⚠️ נמל היעד אינו במילון הקואורדינטות. מוגדר מרחק ברירת מחדל של 50 ק\"מ." if is_hebrew else "⚠️ Port not in dictionary. Default 50 km applied.")
            except Exception:
                st.warning("⚠️️ פורמט קואורדינטות שגוי. נא להזין: `32.0853, 34.7818`" if is_hebrew else "⚠️ Invalid coordinates format.")

    with col_meta2:
        applied_vat = st.number_input(f"{txt['vat_label']} ({dest_country_name}) %:", value=float(VAT_RATES[dest_country_code]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country_code}")
        vat_recovery_pct = st.number_input(txt["vat_rec"], value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        vat_paid_by_supplier = st.checkbox(txt["vat_sup"], value=False, key="tab1_vat_supplier")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("#### מכולות סוללה (BESS)" if is_hebrew else "#### BESS Containers")
        bess_count = st.number_input("כמות מכולות BESS (40' HC DG):" if is_hebrew else "BESS Containers (40' HC DG):", min_value=0, value=20, step=1, key="proj_bess_count")
        bess_exw = st.number_input("עלות EXW ליחידת BESS ($):" if is_hebrew else "EXW Unit Cost per BESS ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_bess_exw")

        oog_count = st.number_input("כמות מכולות חריגות (OOG):" if is_hebrew else "OOG Containers:", min_value=0, value=0, step=1, key="proj_oog_count")
        oog_exw = st.number_input("עלות EXW ליחידת OOG ($):" if is_hebrew else "EXW Unit Cost per OOG ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_oog_exw")

    with col_q2:
        st.markdown("#### תחנות המרה ושנאים" if is_hebrew else "#### MVS & Transformers")
        mvs_count = st.number_input("כמות תחנות מתח גבוה (MVS):" if is_hebrew else "MVS Stations:", min_value=0, value=4, step=1, key="proj_mvs_count")
        mvs_exw = st.number_input("עלות EXW ליחידת MVS ($):" if is_hebrew else "EXW Unit Cost per MVS ($):", min_value=0.0, value=250000.0, step=10000.0, key="proj_mvs_exw")

        transformer_count = st.number_input("כמות שנאים ראשיים:" if is_hebrew else "Main Transformers:", min_value=0, value=2, step=1, key="proj_trans_count")
        transformer_exw = st.number_input("עלות EXW ליחידת שנאי ($):" if is_hebrew else "EXW Unit Cost per Transformer ($):", min_value=0.0, value=120000.0, step=10000.0, key="proj_trans_exw")

    with col_q3:
        st.markdown("#### ציוד נלווה וסולארי" if is_hebrew else "#### Accessories & PV")
        access_count = st.number_input("מכולות ציוד נלווה / יבש:" if is_hebrew else "Accessory Containers:", min_value=0, value=2, step=1, key="proj_access_count")
        access_exw = st.number_input("עלות EXW ליחידת ציוד נלווה ($):" if is_hebrew else "EXW Unit Cost per Accessory Container ($):", min_value=0.0, value=50000.0, step=5000.0, key="proj_access_exw")

        solar_count = st.number_input("יחידות פאנלים סולאריים (PV):" if is_hebrew else "Solar PV Units:", min_value=0, value=0, step=1, key="proj_solar_count")
        solar_exw = st.number_input("עלות EXW ליחידה סולארית ($):" if is_hebrew else "EXW Unit Cost per Solar Unit ($):", min_value=0.0, value=300000.0, step=10000.0, key="proj_solar_exw")

    total_containers_project = max(1, bess_count + oog_count + mvs_count + transformer_count + access_count + solar_count)
    total_exw_project = (
        (bess_count * bess_exw) + (oog_count * oog_exw) + 
        (mvs_count * mvs_exw) + (transformer_count * transformer_exw) + 
        (access_count * access_exw) + (solar_count * solar_exw)
    )
    is_bess = (bess_count > 0 or oog_count > 0)
    is_dg = is_bess

    exw_display_val, _ = convert_from_usd(total_exw_project, display_currency)
    success_msg = f'📊 יחידות בפרויקט: {total_containers_project:,} | סה"כ עלות EXW במפעל: {curr_symbol} {exw_display_val:,.2f}' if is_hebrew else f'📊 Project Units: {total_containers_project:,} | Total Factory EXW Value: {curr_symbol} {exw_display_val:,.2f}'
    st.success(success_msg)

with tab2:
    st.subheader("🚢 תעריפי הובלה ימית, היטל דלק (BAF) ודמי טיפול בנמל יעד (DTHC)" if is_hebrew else "🚢 Ocean Freight, BAF & Destination THC")
    
    selected_carrier_code = st.selectbox("בחירת חברת ספנות:" if is_hebrew else "Shipping Line / Carrier:", list(CARRIER_FUEL_SURCHARGES.keys()), format_func=lambda k: CARRIER_FUEL_SURCHARGES[k]["name"], key="tab2_carrier_code")
    carrier_data = CARRIER_FUEL_SURCHARGES[selected_carrier_code]

    baf_included = st.checkbox("תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית" if is_hebrew else "Bunker Adjustment Factor (BAF) included in ocean freight", value=False, key="tab2_baf_incl")
    include_baf_calculation = not baf_included

    st.markdown("##### 1. עלות הובלה ימית ליחידה:" if is_hebrew else "##### 1. Ocean Freight per Unit:")
    oc_col1, oc_col2, oc_col3 = st.columns(3)
    with oc_col1:
        unit_freight_bess = st.number_input("הובלת BESS ($):" if is_hebrew else "BESS Freight ($):", value=21000.0 * carrier_data["bess_mult"], step=500.0, key=f"freight_bess_{selected_carrier_code}")
        unit_freight_oog = st.number_input("הובלת OOG ($):" if is_hebrew else "OOG Freight ($):", value=29900.0, step=500.0, key=f"freight_oog_{selected_carrier_code}")
    with oc_col2:
        unit_freight_mvs = st.number_input("הובלת MVS ($):" if is_hebrew else "MVS Freight ($):", value=4200.0, step=200.0, key=f"freight_mvs_{selected_carrier_code}")
        unit_freight_trans = st.number_input("הובלת שנאי ($):" if is_hebrew else "Transformer Freight ($):", value=5500.0, step=200.0, key=f"freight_trans_{selected_carrier_code}")
    with oc_col3:
        unit_freight_access = st.number_input("הובלת ציוד נלווה ($):" if is_hebrew else "Accessory Freight ($):", value=3200.0, step=200.0, key=f"freight_access_{selected_carrier_code}")
        unit_freight_solar = st.number_input("הובלת סולארי ($):" if is_hebrew else "Solar PV Freight ($):", value=3360.0, step=200.0, key=f"freight_solar_{selected_carrier_code}")

    st.markdown("---")
    if include_baf_calculation:
        st.markdown("##### 2. היטל דלק ימי (BAF) מחושב לפי נפח TEU:" if is_hebrew else "##### 2. Bunker Adjustment Factor (BAF) per TEU:")
        baf_mult = carrier_data["dthc_mult"]
        base_baf_per_teu = st.number_input("תעריף BAF בסיסי ל־TEU יחיד ($):" if is_hebrew else "Base BAF Rate per TEU ($):", value=420.0 * baf_mult, step=20.0, key=f"baf_per_teu_{selected_carrier_code}")

        teu_bess, teu_oog, teu_mvs, teu_trans, teu_access, teu_solar = 2.0, 2.0, 1.0, 1.0, 1.0, 1.0
        baf_bess = (base_baf_per_teu * teu_bess)
        baf_oog = (base_baf_per_teu * teu_oog)
        baf_mvs = (base_baf_per_teu * teu_mvs)
        baf_trans = (base_baf_per_teu * teu_trans)
        baf_access = (base_baf_per_teu * teu_access)
        baf_solar = (base_baf_per_teu * teu_solar)
    else:
        baf_bess, baf_oog, baf_mvs, baf_trans, baf_access, baf_solar = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    st.markdown("---")
    st.markdown("##### 3. דמי טיפול בנמל יעד (Destination THC):" if is_hebrew else "##### 3. Destination Terminal Handling Charges (Destination THC):")
    dthc_mult = carrier_data["dthc_mult"]
    
    dh_col1, dh_col2, dh_col3 = st.columns(3)
    with dh_col1:
        dthc_bess = st.number_input("DTHC מכולת BESS ($):" if is_hebrew else "BESS Destination THC ($):", value=650.0 * dthc_mult, step=50.0, key=f"dthc_bess_{selected_carrier_code}")
        dthc_oog = st.number_input("DTHC מכולת OOG ($):" if is_hebrew else "OOG Destination THC ($):", value=850.0 * dthc_mult, step=50.0, key=f"dthc_oog_{selected_carrier_code}")
    with dh_col2:
        dthc_mvs = st.number_input("DTHC תחנת MVS ($):" if is_hebrew else "MVS Destination THC ($):", value=420.0 * dthc_mult, step=30.0, key=f"dthc_mvs_{selected_carrier_code}")
        dthc_trans = st.number_input("DTHC שנאי ($):" if is_hebrew else "Transformer Destination THC ($):", value=480.0 * dthc_mult, step=30.0, key=f"dthc_trans_{selected_carrier_code}")
    with dh_col3:
        dthc_access = st.number_input("DTHC ציוד נלווה ($):" if is_hebrew else "Accessory Destination THC ($):", value=280.0 * dthc_mult, step=20.0, key=f"dthc_access_{selected_carrier_code}")
        dthc_solar = st.number_input("DTHC פאנלים ($):" if is_hebrew else "Solar PV Destination THC ($):", value=300.0 * dthc_mult, step=20.0, key=f"dthc_solar_{selected_carrier_code}")

    customs_duty_pct_default = 0.0 if dest_country_code == "IL" else 2.7
    customs_duty_pct = st.number_input(
        "שיעור מכס יבוא כללי לציוד אגירה וציוד נלווה (%) — (פאנלים סולאריים פטורים אוטומטית 0%):" if is_hebrew else
        "General Import Customs Duty Rate (%) for BESS/MVS (Solar PV is automatically 0% exempt):",
        value=float(customs_duty_pct_default), min_value=0.0, max_value=100.0, step=0.1,
        key=f"customs_duty_input_{dest_country_code}"
    )
    insurance_pct = DEFAULT_INSURANCE_RATES.get(dest_country_code, 0.15)

with tab3:
    st.subheader("📦 אחסנה, השהיות והובלת משאיות לאתר" if is_hebrew else "📦 Storage, Demurrage & Inland Drayage")
    
    dk = int(calculated_distance_km * 100)
    distance_factor = max(1.0, calculated_distance_km / 50.0)

    st.markdown("##### 1. הובלה יבשתית מנמל הפריקה לאתר הפרויקט (Port to Site)" if is_hebrew else "##### 1. Port-to-Site Inland Drayage")
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        drayage_bess = st.number_input("הובלת משאיות BESS ליחידה ($):" if is_hebrew else "BESS Trucking per unit ($):", value=4500.0 * distance_factor, step=200.0, key=f"dray_bess_{dk}")
        drayage_oog = st.number_input("הובלת משאיות OOG ליחידה ($):" if is_hebrew else "OOG Trucking per unit ($):", value=4800.0 * distance_factor, step=200.0, key=f"dray_oog_{dk}")
    with dr_col2:
        drayage_mvs = st.number_input("הובלת משאיות MVS ליחידה ($):" if is_hebrew else "MVS Trucking per unit ($):", value=1400.0 * distance_factor, step=100.0, key=f"dray_mvs_{dk}")
        drayage_trans = st.number_input("הובלת משאיות שנאי ליחידה ($):" if is_hebrew else "Transformer Trucking per unit ($):", value=1800.0 * distance_factor, step=100.0, key=f"dray_trans_{dk}")
    with dr_col3:
        drayage_access = st.number_input("הובלת ציוד נלווה ליחידה ($):" if is_hebrew else "Accessory Trucking per unit ($):", value=850.0 * distance_factor, step=100.0, key=f"dray_access_{dk}")
        drayage_solar = st.number_input("הובלת ציוד סולארי ליחידה ($):" if is_hebrew else "Solar PV Trucking per unit ($):", value=950.0 * distance_factor, step=100.0, key=f"dray_solar_{dk}")

    st.markdown("---")
    st.markdown("##### 2. דמי השהייה בנמל ואחסנה חיצונית" if is_hebrew else "##### 2. Port Demurrage & External Storage")
    st_col1, st_col2 = st.columns(2)
    with st_col1:
        actual_port_days = st.number_input("ימי שהייה בפועל בנמל:" if is_hebrew else "Actual Port Days:", value=12, min_value=1, step=1, key="tab3_actual_days")
        free_days = st.number_input("ימי פטור (Free Days):" if is_hebrew else "Free Days:", value=int(DEFAULT_FREE_DAYS.get(dest_country_code, 7)), min_value=0, step=1, key=f"tab3_free_days_{dest_country_code}")
        demurrage_daily_rate = st.number_input("עלות השהייה יומית בנמל ($):" if is_hebrew else "Demurrage Daily Rate ($):", value=250.0 if is_dg else 150.0, step=25.0, key=f"tab3_dem_rate_{is_dg}")
    with st_col2:
        use_external_storage = st.checkbox("השתמש באחסנה חיצונית (External Storage)" if is_hebrew else "Use External Storage", value=True, key="tab3_ext_storage_toggle")
        ext_storage_days = st.number_input("ימי אחסנה חיצונית:" if is_hebrew else "External Storage Days:", value=15, min_value=0, step=1, key="tab3_ext_days")
        ext_storage_daily_rate = st.number_input("עלות אחסנה יומית ($):" if is_hebrew else "Daily External Storage Rate ($):", value=65.0 if is_dg else 45.0, step=10.0, key=f"tab3_ext_rate_{is_dg}")

    st.markdown("---")
    st.markdown("##### 3. מנוף ופריקה באתר" if is_hebrew else "##### 3. Site Crane & Unloading")
    cr_col1, cr_col2 = st.columns(2)
    with cr_col1:
        include_site_crane = st.checkbox("הכלל עלות מנוף עוגן / פריקה באתר" if is_hebrew else "Include Site Crane & Unloading", value=True, key="tab3_crane_toggle")
    with cr_col2:
        site_crane_unloading = st.number_input("עלות כוללת למנוף ופריקה ($):" if is_hebrew else "Total Crane & Unloading Cost ($):", value=8500.0, step=500.0, key="tab3_crane_cost")

    include_delay_scenario = False

with tab4:
    st.subheader("⚖️ רגולציה, קיימות ואישורים מנדטוריים" if is_hebrew else "⚖ Regulation, Sustainability & Approvals")

    bess_capacity_mwh = 4.0
    decom_cost_per_kwh = 0.0 if dest_country_code == "IL" else 75.0

    if dest_country_code == "IL":
        mot_fee_per_bess = st.number_input("עלות אגרת אישור הובלה ממשרד התחבורה ליחידת BESS ($):" if is_hebrew else "MOT approval fee per BESS unit ($):", value=350.0, step=50.0, key="mot_fee_input_il")
        mot_total_approval_cost = mot_fee_per_bess * float(bess_count + oog_count)
        local_regulatory_permits = st.number_input("עלות כוללת להיתרי חומ\"ס נמלים ($):" if is_hebrew else "Port hazmat permits cost ($):", value=1500.0, step=100.0, key="reg_cost_input_il")
        
        epr_recycling_total_usd = 0.0
        battery_passport_total_usd = 0.0
        include_mot_approval = True
        include_regulatory = True
    else:
        battery_passport_flat = st.number_input("עלות כוללת לדרכון סוללות ותיעוד ($):" if is_hebrew else "Total Battery Passport Cost ($):", value=1200.0, step=100.0, key="bp_cost_input_eu")
        battery_passport_total_usd = battery_passport_flat

        epr_fee_per_unit = st.number_input("עלות EPR שוטף ליחידת BESS ($):" if is_hebrew else "Ongoing EPR Fee per BESS unit ($):", value=450.0, step=50.0, key="epr_unit_input_eu")
        epr_recycling_total_usd = epr_fee_per_unit * float(bess_count + oog_count)

        include_regulatory = st.checkbox("הכלל אגרות היתרי כניסה והיערכות אתר מקומיים באירופה" if is_hebrew else "Include local site entry permits", value=True, key="reg_permits_toggle_eu")
        local_regulatory_permits = st.number_input("עלות היתרים מקומיים ($):" if is_hebrew else "Local Permits Cost ($):", value=600.0, step=100.0, key="reg_cost_input_eu") if include_regulatory else 0.0

        mot_total_approval_cost = 0.0
        include_mot_approval = False

        st.markdown("---")
        st.markdown("### 🔄 תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning & Recycling Provision)" if is_hebrew else "### 🔄 Decommissioning & End-of-Life Financial Provision")
        with st.expander("📌 ניהול והפרשה לעתיד (תקן אירופי $60–$90 ל־kWh)" if is_hebrew else "📌 Future Provision (EU Benchmark $60–$90/kWh)", expanded=True):
            decom_col1, decom_col2 = st.columns(2)
            with decom_col1:
                bess_capacity_mwh = st.number_input(
                    "קיבולת ממוצעת למכולת BESS (MWh):" if is_hebrew else "Average BESS Container Capacity (MWh):",
                    min_value=0.1, value=4.0, step=0.5, key="decom_capacity_mwh"
                )
            with decom_col2:
                decom_cost_per_kwh = st.number_input(
                    "עלות פירוק ומחזור סוף חיים ל־kWh ($) [בנצ'מרק $75]:" if is_hebrew else "Decommissioning & Recycling Cost per kWh ($) [Benchmark $75]:",
                    min_value=0.0, value=75.0, step=5.0, key="decom_cost_per_kwh"
                )
            
            decom_cost_per_bess = bess_capacity_mwh * 1000.0 * decom_cost_per_kwh
            decom_per_unit_disp, _ = convert_from_usd(decom_cost_per_bess, display_currency)
            decom_total_disp, _ = convert_from_usd(decom_cost_per_bess * float(bess_count + oog_count), display_currency)
            st.info(
                f'✅ {bess_capacity_mwh:.1f} MWh × ${decom_cost_per_kwh:,.0f}/kWh = **{curr_symbol} {decom_per_unit_disp:,.2f}** ' + ("למכולה אחת" if is_hebrew else "per container") + '. ' +
                (f'סה"כ הפרשה ל־{int(bess_count + oog_count)} מכולות BESS: **{curr_symbol} {decom_total_disp:,.2f}**' if is_hebrew else f'Total provision for {int(bess_count + oog_count)} BESS containers: **{curr_symbol} {decom_total_disp:,.2f}**')
            )

    st.markdown("---")
    requires_heavy_lift = st.checkbox("נדרש סקר מטענים כבדים / מנוף עוגן (Heavy-Lift Survey)" if is_hebrew else "Heavy-Lift Survey Required", value=is_bess, key="hl_survey_toggle")
    heavy_lift_survey_cost = st.number_input("עלות סקר מטענים כבדים ($):" if is_hebrew else "Heavy-Lift Survey Cost ($):", value=2500.0, step=250.0, key="hl_cost_input") if requires_heavy_lift else 0.0

if is_european_dest and tab5_eu is not None:
    with tab5_eu:
        st.subheader("🗺️ הנחות מסלולים אינדיקטיביות באירופה (Route & Corridor Analysis)")
        st.warning("⚠️ נתונים אינדיקטיביים בלבד, לאימות מול משלח." if is_hebrew else "⚠ Indicative data only, subject to freight forwarder verification.")
        if is_hebrew:
            eu_route_data = [
                {"מסלול": "אסיה דרך קונסטנצה (רומניה)", "זמן מעבר": "32-35 ימים", "יתרון מרכזי": "אופטימלי לפרויקטים במזרח אירופה ובבלקן", "התאמה": "גבוהה לפאנלים ו־BESS"},
                {"מסלול": "אסיה דרך פיראוס (יוון)", "זמן מעבר": "28-31 ימים", "יתרון מרכזי": "כניסה ימית מהירה לדרום ומרכז אירופה", "התאמה": "גבוהה מאוד"},
                {"מסלול": "אסיה דרך רוטרדם / אנטוורפן (צפון אירופה)", "זמן מעבר": "30-33 ימים", "יתרון מרכזי": "תשתיות מטענים כבדים ומדוברות מתקדמות", "התאמה": "גמישות מקסימלית"},
                {"מסלול": "מולטימודלי דרך המבורג לפולין/גרמניה", "זמן מעבר": "35-38 ימים", "יתרון מרכזי": "שילוח רכבתי ישיר למרכז אירופה", "התאמה": "פרויקטי רשת סטנדרטיים"}
            ]
        else:
            eu_route_data = [
                {"Route": "Asia via Constanța (Romania)", "Transit": "32-35 Days", "Advantage": "Optimal for Eastern Europe / Balkan projects", "Suitability": "High for Solar + BESS"},
                {"Route": "Asia via Piraeus (Greece)", "Transit": "28-31 Days", "Advantage": "Fastest maritime entry to Southern/Central Europe", "Suitability": "High"},
                {"Route": "Asia via Rotterdam / Antwerp (North Europe)", "Transit": "30-33 Days", "Advantage": "Unmatched heavy-lift and barge infrastructure", "Suitability": "Maximum Flexibility"},
                {"Route": "Multimodal via Hamburg to Poland/Germany", "Transit": "35-38 Days", "Advantage": "Direct rail/multimodal forwarding to Central European hubs", "Suitability": "Standard Grid Projects"}
            ]
        st.dataframe(pd.DataFrame(eu_route_data), use_container_width=False, hide_index=True)

if is_european_dest and tab_projects is not None:
    with tab_projects:
        st.subheader(txt["projects_header"])
        csv_path = os.path.join(os.path.dirname(__file__), "projects.csv")
        try:
            df_projects = pd.read_csv(csv_path)
            if "CONT" in df_projects.columns:
                df_projects["Over 50"] = (pd.to_numeric(df_projects["CONT"], errors="coerce") > 50).map({True: "Yes", False: "No"})
                cols = list(df_projects.columns)
                if "Over 50" in cols:
                    cols.remove("Over 50")
                    insert_idx = cols.index("SPV") if "SPV" in cols else len(cols)
                    cols.insert(insert_idx, "Over 50")
                    df_projects = df_projects[cols]
            st.dataframe(df_projects, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.error("⚠️ קובץ הנתונים `projects.csv` אינו נמצא בתיקייה." if is_hebrew else "⚠️ `projects.csv` file not found.")
        except Exception as e:
            st.error(f"⚠ שגיאה בטעינת הקובץ / Error loading file: {e}")

calc_results = calculate_project_costs(
    bess_count=bess_count, bess_exw=bess_exw,
    oog_count=oog_count, oog_exw=oog_exw,
    mvs_count=mvs_count, mvs_exw=mvs_exw,
    transformer_count=transformer_count, transformer_exw=transformer_exw,
    access_count=access_count, access_exw=access_exw,
    solar_count=solar_count, solar_exw=solar_exw,
    unit_freight_bess=unit_freight_bess, unit_freight_oog=unit_freight_oog,
    unit_freight_mvs=unit_freight_mvs, unit_freight_trans=unit_freight_trans,
    unit_freight_access=unit_freight_access, unit_freight_solar=unit_freight_solar,
    baf_bess=baf_bess, baf_oog=baf_oog, baf_mvs=baf_mvs, baf_trans=baf_trans, baf_access=baf_access, baf_solar=baf_solar,
    dthc_bess=dthc_bess, dthc_oog=dthc_oog, dthc_mvs=dthc_mvs, dthc_trans=dthc_trans, dthc_access=dthc_access, dthc_solar=dthc_solar,
    drayage_bess=drayage_bess, drayage_oog=drayage_oog, drayage_mvs=drayage_mvs,
    drayage_trans=drayage_trans, drayage_access=drayage_access, drayage_solar=drayage_solar,
    trend_multiplier=trend_multiplier, insurance_pct=insurance_pct,
    customs_duty_pct=customs_duty_pct, applied_vat=applied_vat, vat_recovery_pct=vat_recovery_pct,
    vat_paid_by_supplier=vat_paid_by_supplier, incoterm_code=selected_incoterm_code,
    dest_country_code=dest_country_code,
    local_regulatory_permits=local_regulatory_permits, mot_total_approval_cost=mot_total_approval_cost,
    include_regulatory=include_regulatory, include_mot_approval=include_mot_approval,
    site_crane_unloading=site_crane_unloading, include_site_crane=include_site_crane,
    epr_recycling_total_usd=epr_recycling_total_usd, battery_passport_total_usd=battery_passport_total_usd,
    requires_heavy_lift=requires_heavy_lift, heavy_lift_survey_cost=heavy_lift_survey_cost,
    actual_port_days=actual_port_days, free_days=free_days, demurrage_daily_rate=demurrage_daily_rate,
    use_external_storage=use_external_storage, ext_storage_days=ext_storage_days,
    ext_storage_daily_rate=ext_storage_daily_rate, include_delay_scenario=include_delay_scenario,
    bess_capacity_mwh=bess_capacity_mwh, decom_cost_per_kwh=decom_cost_per_kwh
)

total_landed_cost_ex_vat = calc_results["total_landed_cost_ex_vat"]
economic_cost_ex_vat = calc_results["economic_cost_ex_vat"]
total_cash_requirement_incl_vat = calc_results["total_cash_requirement_incl_vat"]
supplier_scope_total = calc_results["supplier_scope_total"]

display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_scope_total, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
econ_val, _ = convert_from_usd(economic_cost_ex_vat, display_currency)

with tab_summary:
    st.subheader(f"{txt['summary_title']} — {incoterm_map[selected_incoterm_code]} ({display_currency})")
    
    m1_title = "עלות נחיתה (לפני מע\"מ)" if is_hebrew else "Total Landed Cost (Excl. VAT)"
    m2_title = "עלות כלכלית כוללת" if is_hebrew else "Total Economic Cost"
    m3_title = "דרישת מזומנים כוללת" if is_hebrew else "Total Cash Requirement"
    m4_title = "טביעת רגל פחמנית מוערכת" if is_hebrew else "Estimated Carbon Footprint"

    # חישוב טביעת רגל פחמנית (CO2): אומדן ממוצע למכולות בהובלה ימית (כ־0.02 קילו לטון-קילומטר) ומשאיות (כ־0.08 קילו לטון-קילומטר)
    # בהנחת מרחק ימי ממוצע מסין לאירופה/ישראל של כ־18,000 ק"מ, ומרחק משאית מחושב מהנמל לאתר.
    total_units_for_calc = calc_results["total_containers_project"]
    ocean_distance_approx_km = 18000.0
    carbon_ocean_tons = (total_units_for_calc * 25.0 * ocean_distance_approx_km * 0.02) / 1000.0
    carbon_road_tons = (total_units_for_calc * 25.0 * calculated_distance_km * 0.08) / 1000.0
    total_carbon_footprint_tons = carbon_ocean_tons + carbon_road_tons

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="metric-container"><div class="metric-title">{m1_title}</div><div class="metric-value"><span class="ltr-val">{curr_symbol} {display_val:,.2f}</span></div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="metric-container"><div class="metric-title">{m2_title}</div><div class="metric-value"><span class="ltr-val">{curr_symbol} {econ_val:,.2f}</span></div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="metric-container"><div class="metric-title">{m3_title}</div><div class="metric-value"><span class="ltr-val">{curr_symbol} {cash_val:,.2f}</span></div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="metric-container"><div class="metric-title">{m4_title}</div><div class="metric-value"><span class="ltr-val">{total_carbon_footprint_tons:,.1f} טון CO2</span></div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(txt["breakdown_title"])

    bess_oog_units = max(1.0, float(bess_count + oog_count))

    ex_exw, _ = convert_from_usd(calc_results["trended_exw"], display_currency)
    u_bess_exw, _ = convert_from_usd(bess_exw * trend_multiplier, display_currency)

    ex_ch_inland, _ = convert_from_usd(calc_results["china_inland_drayage"] + calc_results["china_origin_thc"], display_currency)
    u_ch_inland, _ = convert_from_usd((calc_results["china_inland_drayage"] + calc_results["china_origin_thc"]) / total_units_for_calc, display_currency)

    ex_ocean, _ = convert_from_usd(calc_results["total_base_ocean_freight"], display_currency)
    u_ocean_bess, _ = convert_from_usd(unit_freight_bess * trend_multiplier, display_currency)

    ex_baf, _ = convert_from_usd(calc_results["total_baf_ocean"], display_currency)
    ex_dthc, _ = convert_from_usd(calc_results["destination_thc_total"], display_currency)
    ex_insur, _ = convert_from_usd(calc_results["insurance_total_usd"], display_currency)
    ex_customs, _ = convert_from_usd(calc_results["customs_duty_usd"], display_currency)

    ex_drayage, _ = convert_from_usd(calc_results["inland_drayage_total_usd"], display_currency)
    u_drayage_bess, _ = convert_from_usd(drayage_bess * trend_multiplier, display_currency)

    ex_reg, _ = convert_from_usd(calc_results["active_regulatory_permits"], display_currency)
    ex_crane, _ = convert_from_usd(calc_results["active_site_crane"], display_currency)
    
    ex_epr, _ = convert_from_usd(calc_results["epr_recycling_total_usd"], display_currency)
    u_epr, _ = convert_from_usd(calc_results["epr_recycling_total_usd"] / bess_oog_units, display_currency)

    ex_bp, _ = convert_from_usd(calc_results["battery_passport_total_usd"], display_currency)
    ex_hl, _ = convert_from_usd(calc_results["active_heavy_lift"], display_currency)
    
    ex_decom, _ = convert_from_usd(calc_results["decommissioning_total_usd"], display_currency)
    u_decom, _ = convert_from_usd(calc_results["decommissioning_total_usd"] / bess_oog_units, display_currency)

    ex_cont, _ = convert_from_usd(calc_results["contingency_usd"], display_currency)
    ex_total, _ = convert_from_usd(total_landed_cost_ex_vat, display_currency)

    item_exw = "ערך ציוד במפעל (Equipment EXW)" if is_hebrew else "Equipment EXW Value"
    item_china = "הובלה יבשתית ונמלית במוצא" if is_hebrew else "China Inland & Origin THC"
    item_ocean = "הובלה ימית בסיסית" if is_hebrew else "Ocean Freight (Base)"
    item_baf = "היטל דלק ימי לפי TEU (BAF)" if is_hebrew else "Bunker Adjustment Factor (BAF)"
    item_dthc = "דמי טיפול בנמל יעד (Destination THC)" if is_hebrew else "Destination THC"
    item_insur = "ביטוח ימי" if is_hebrew else "Marine Insurance"
    item_customs = f"מכס יבוא לפי קטגוריה ({customs_duty_pct}% לציוד אגירה/ממירים | 0% פטור לפאנלים סולאריים)" if is_hebrew else f"Differential Customs Duty ({customs_duty_pct}% for BESS | 0% for PV)"
    item_drayage = "הובלה יבשתית מנמל לאתר" if is_hebrew else "Inland Drayage (Port to Site)"
    item_reg = "רגולציה מקומית ואישורי חומ\"ס / משרד התחבורה" if is_hebrew else "Regulatory & Local Permits"
    item_crane = "עגורן מנוף ופריקה באתר" if is_hebrew else "Site Crane & Unloading"
    item_epr = "דמי EPR שוטפים / מיחזור" if is_hebrew else "EPR / Recycling Fees"
    item_bp = "דרכון סוללות דיגיטלי (EU Battery Passport)" if is_hebrew else "EU Battery Passport"
    item_hl = "סקר מטענים כבדים (Heavy-Lift Survey)" if is_hebrew else "Heavy-Lift Survey"
    item_decom = f"הפרשת מחזור סוף חיים — {bess_capacity_mwh}MWh @ ${decom_cost_per_kwh}/kWh" if is_hebrew else f"Decommissioning Provision ({bess_capacity_mwh}MWh)"
    item_carbon = f"טביעת רגל פחמנית כוללת (הובלה ימית + יבשתית)" if is_hebrew else f"Total Carbon Footprint (Ocean + Road)"
    item_cont = "בלת״ם פרויקטי (5%)" if is_hebrew else "Contingency (5%)"
    item_tot = "סה\"כ עלות נחיתה לפני מע\"מ (Total Landed Cost)" if is_hebrew else "Total Landed Cost (Excl. VAT)"

    decom_row_html = f'<tr style="background-color: #fbf8f0;"><td>{item_decom}</td><td class="center">{int(bess_count + oog_count):,} BESS</td><td class="left"><span class="ltr-val">{curr_symbol} {u_decom:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_decom:,.2f}</span></b></td></tr>' if dest_country_code != "IL" else ""
    carbon_row_html = f'<tr style="background-color: #f0fdf4;"><td>{item_carbon}</td><td class="center">{int(total_units_for_calc):,} units</td><td class="left"><span class="ltr-val">{(total_carbon_footprint_tons/total_units_for_calc):,.2f} t/unit</span></td><td class="left"><b><span class="ltr-val">{total_carbon_footprint_tons:,.1f} טון CO2</span></b></td></tr>'

    html_table = f"""
    <table class="custom-finance-table">
        <thead>
            <tr>
                <th style="width: 40%;">{txt["col_item"]}</th>
                <th class="center" style="width: 20%;">{txt["col_qty"]}</th>
                <th class="left" style="width: 20%;">{txt["col_unit"]}</th>
                <th class="left" style="width: 20%;">{txt["col_total"]}</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>{item_exw}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left"><span class="ltr-val">BESS: {curr_symbol} {u_bess_exw:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_exw:,.2f}</span></b></td></tr>
            <tr><td>{item_china}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left"><span class="ltr-val">{curr_symbol} {u_ch_inland:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_ch_inland:,.2f}</span></b></td></tr>
            <tr><td>{item_ocean}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left"><span class="ltr-val">BESS: {curr_symbol} {u_ocean_bess:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_ocean:,.2f}</span></b></td></tr>
            <tr><td>{item_baf}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_baf:,.2f}</span></b></td></tr>
            <tr><td>{item_dthc}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_dthc:,.2f}</span></b></td></tr>
            <tr><td>{item_insur}</td><td class="center">% CIF</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_insur:,.2f}</span></b></td></tr>
            <tr><td>{item_customs}</td><td class="center">{txt["qty_differential"]}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_customs:,.2f}</span></b></td></tr>
            <tr><td>{item_drayage}</td><td class="center">{int(total_units_for_calc):,}</td><td class="left"><span class="ltr-val">BESS: {curr_symbol} {u_drayage_bess:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_drayage:,.2f}</span></b></td></tr>
            <tr><td>{item_reg}</td><td class="center">{txt["qty_expense"]}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_reg:,.2f}</span></b></td></tr>
            <tr><td>{item_crane}</td><td class="center">{txt["qty_expense"]}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_crane:,.2f}</span></b></td></tr>
            <tr><td>{item_epr}</td><td class="center">{int(bess_count + oog_count):,} BESS</td><td class="left"><span class="ltr-val">{curr_symbol} {u_epr:,.2f}</span></td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_epr:,.2f}</span></b></td></tr>
            <tr><td>{item_bp}</td><td class="center">{txt["qty_global"]}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_bp:,.2f}</span></b></td></tr>
            <tr><td>{item_hl}</td><td class="center">{txt["qty_survey"]}</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_hl:,.2f}</span></b></td></tr>
            <tr><td>{item_cont}</td><td class="center">5%</td><td class="left">-</td><td class="left"><b><span class="ltr-val">{curr_symbol} {ex_cont:,.2f}</span></b></td></tr>
            <tr class="total-row"><td>{item_tot}</td><td class="center">-</td><td class="left">-</td><td class="left" style="color: #1e3d59;"><b><span class="ltr-val">{curr_symbol} {ex_total:,.2f}</span></b></td></tr>
            {decom_row_html}
            {carbon_row_html}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    
    excel_summary_data = [
        [txt["col_item"], txt["col_qty"], f'{txt["col_total"]} ({display_currency})'],
        [item_exw, f"{int(total_units_for_calc):,} units", ex_exw],
        [item_china, f"{int(total_units_for_calc):,} units", ex_ch_inland],
        [item_ocean, f"{int(total_units_for_calc):,} containers", ex_ocean],
        [item_baf, f"{int(total_units_for_calc):,} units", ex_baf],
        [item_dthc, f"{int(total_units_for_calc):,} units", ex_dthc],
        [item_insur, "% of CIF", ex_insur],
        [item_customs, txt["qty_differential"], ex_customs],
        [item_drayage, f"{int(total_units_for_calc):,} trucks", ex_drayage],
        [item_reg, txt["qty_expense"], ex_reg],
        [item_crane, txt["qty_expense"], ex_crane],
        [item_epr, f"{int(bess_count + oog_count):,} BESS", ex_epr],
        [item_bp, txt["qty_global"], ex_bp],
        [item_hl, txt["qty_survey"], ex_hl],
        [item_cont, "5%", ex_cont],
        [item_tot, "-", ex_total]
    ]
    if dest_country_code != "IL":
        excel_summary_data.append([item_decom, f"{int(bess_count + oog_count):,} BESS (Lifecycle)", ex_decom])
    excel_summary_data.append([item_carbon, f"{int(total_units_for_calc):,} units", f"{total_carbon_footprint_tons:,.1f} tons CO2"])

    main_rows_for_rec = [r for r in excel_summary_data[1:] if r[0] not in (item_tot, item_decom, item_carbon)]
    sum_main_rows = sum(r[2] for r in main_rows_for_rec if isinstance(r[2], (int, float)))
    if abs(sum_main_rows - ex_total) >= 1.0:
        st.error(f"Reconciliation mismatch: {sum_main_rows:,.2f} vs {ex_total:,.2f}")

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = pd.DataFrame(excel_summary_data[1:], columns=excel_summary_data[0])
        df_export.to_excel(writer, sheet_name='Cost Summary', index=False)
        ws = writer.sheets['Cost Summary']
        ws.views.sheetView[0].rightToLeft = is_hebrew

        for row in ws.iter_rows(min_row=2, min_col=3, max_col=3):
            if isinstance(row[0].value, (int, float)):
                row[0].number_format = '#,##0.00'

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(max_len + 5, 15)

    excel_data = output.getvalue()
    st.download_button(
        label=txt["excel_btn"],
        data=excel_data,
        file_name=f"TerraVol_Project_Report_Modular_{dest_country_code}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
