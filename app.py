import streamlit as st
import pandas as pd
import os
import requests
import base64
from datetime import date
from io import BytesIO

# ---------------------------------------------------------
# הגדרת תצורת עמוד ולוגו
# ---------------------------------------------------------
possible_logo_names = ["logo.png", "logo.png.png", "Logo.png"]
logo_path = None
for name in possible_logo_names:
    full_path = os.path.join(os.path.dirname(__file__), name)
    if os.path.exists(full_path):
        logo_path = full_path
        break

st.set_page_config(
    page_title="Terra Vol",
    page_icon=logo_path if logo_path else "⚡",
    layout="wide"
)

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

st.sidebar.header("🌐 Language / שפה")
lang = st.sidebar.radio("Select Language / בחר שפה:", ["English", "עברית"], index=0, key="lang_select")
is_hebrew = (lang == "עברית")
current_lang = "he" if is_hebrew else "en"

# מילון תרגום מקצועי ונפרד לחלוטין לכל שפה
T = {
    "he": {
        "caption": "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, תנאי סחר, רגולציה ותחזית שוק",
        "incoterm_label": "תנאי סחר מסחרי (אחריות ספק):",
        "currency_label": "מטבע תצוגה ראשי:",
        "forecast_label": "תאריך יעד לאספקה באתר:",
        "market_label": "תחזית אינפלציה ומגמת שוק:",
        "rate_usd_eur": "שער המרה USD ל־EUR:",
        "rate_usd_ils": "שער המרה USD ל־ILS:",
        "tab1": "📋 תמהיל ציוד וכמויות לפרויקט",
        "tab2": "⚓ שרשרת אספקה ותנאי סחר",
        "tab3": "📦 אחסנה, השהיות והובלת משאיות לאתר",
        "tab4": "⚖️ רגולציה ואישורים מנדטוריים",
        "tab5_eu": "🗺️ הנחות מסלולים באירופה",
        "tab_projects": "📂 פרויקטי Enlight 2027-2028 (שירה)",
        "tab_summary": "📊 דוח בקרה תקציבית ורגולטורית",
        "origin_port": "נמל מוצא:",
        "dest_port": "נמל פריקה (יעד):",
        "dest_country": "מדינת יעד לפרויקט:",
        "site_name": "שם אתר הפרויקט:",
        "site_placeholder": "אשלים / עמק הירדן (אנלייט)",
        "equipment_header": "הגדרת רכיבי הציוד וכמויות לפרויקט",
        "equipment_info": "הזן את כמויות מכולות הסוללה, הממירים, השנאים ועלויות הייצור במפעל (EXW).",
    },
    "en": {
        "caption": "Professional Project Calculator for Target Costs, Incoterms, Regulation & Market Forecast",
        "incoterm_label": "Commercial Incoterm (Supplier Scope):",
        "currency_label": "Main Display Currency:",
        "forecast_label": "Delivery Target Date:",
        "market_label": "Inflation & Market Trend Scenario:",
        "rate_usd_eur": "USD to EUR Exchange Rate:",
        "rate_usd_ils": "USD to ILS Exchange Rate:",
        "tab1": "📋 Equipment Mix & Quantities",
        "tab2": "⚓ Supply Chain & Incoterms",
        "tab3": "📦 Storage, Demurrage & Inland Drayage",
        "tab4": "⚖️ Regulation & Mandatory Approvals",
        "tab5_eu": "🗺️ European Route Options",
        "tab_projects": "📂 Enlight Projects 2027-2028 (Shira)",
        "tab_summary": "📊 Budget & Regulatory Control Report",
        "origin_port": "Origin Port:",
        "dest_port": "Destination Port:",
        "dest_country": "Project Destination Country:",
        "site_name": "Project Site Name / Address:",
        "site_placeholder": "Project Site / Site Address",
        "equipment_header": "Equipment Mix & Quantities Configuration",
        "equipment_info": "Enter BESS container quantities, inverters, transformers, and factory EXW production costs.",
    }
}

txt = T[current_lang]
direction_css = "rtl" if is_hebrew else "ltr"
text_align_css = "right" if is_hebrew else "left"

st.markdown(
    f"""
    <style>
    .stApp {{ direction: {direction_css}; text-align: {text_align_css}; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    h1, h2, h3, h4, h5, h6, p, label, div, span {{ direction: {direction_css}; text-align: {text_align_css}; }}
    .stTextInput label, .stSelectbox label, .stNumberInput label {{ direction: {direction_css}; text-align: {text_align_css}; width: 100%; font-weight: 600; }}
    
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

ORIGIN_PORTS = ["שאנגחאי (Shanghai)", "נינגבו (Ningbo)", "שנג'ן (Shenzhen)", "צ'ינגדאו (Qingdao)"] if is_hebrew else ["Shanghai, China", "Ningbo, China", "Shenzhen, China", "Qingdao, China"]

DESTINATION_PORTS = {
    "ישראל": ["נמל חיפה", "נמל אשדוד"],
    "רומניה": ["קונסטנצה, רומניה (Constanța)", "בורגס, בולגריה (Burgas)"],
    "פולין": ["גדנסק, פולין (Gdansk)", "גדיניה, פולין (Gdynia)"],
    "גרמניה": ["המבורג, גרמניה (Hamburg)", "ברמרהאפן, גרמניה (Bremerhaven)"],
    "שוודיה": ["גטבורג, שוודיה (Gothenburg)", "סטוקהולם, שוודיה (Stockholm)"],
    "יוון": ["פיראוס, יוון (Piraeus)", "סלוניקי, יוון (Thessaloniki)"],
    "ספרד": ["ולנסיה, ספרד (Valencia)", "ברצלונה, ספרד (Barcelona)"],
    "איטליה": ["ג'נואה, איטליה (Genoa)", "טרייסטה, איטליה (Trieste)"],
    "בולגריה": ["וורנה, בולגריה (Varna)", "בורגס, בולגריה (Burgas)"],
    "הונגריה": ["בודפשט, הונגריה (Budapest - Rail/Multimodal)"],
    "אחר / מותאם": ["רוטרדם, הולנד (Rotterdam)", "אנטוורפן, בלגיה (Antwerp)"]
}

VAT_RATES = {
    "ישראל": 18.0, "רומניה": 19.0, "פולין": 23.0, "גרמניה": 19.0, 
    "שוודיה": 25.0, "יוון": 24.0, "ספרד": 21.0, "איטליה": 22.0, "בולגריה": 20.0, "הונגריה": 27.0, "אחר / מותאם": 0.0
}
DEFAULT_INSURANCE_RATES = {
    "ישראל": 0.08, "רומניה": 0.15, "פולין": 0.15, "גרמניה": 0.15, 
    "שוודיה": 0.15, "יוון": 0.15, "ספרד": 0.15, "איטליה": 0.15, "בולגריה": 0.15, "הונגריה": 0.15, "אחר / מותאם": 0.15
}
DEFAULT_FREE_DAYS = {
    "ישראל": 4, "romania": 7, "פולין": 7, "גרמניה": 7, 
    "שוודיה": 7, "יוון": 7, "ספרד": 7, "איטליה": 7, "בולגריה": 7, "הונגריה": 7, "אחר / מותאם": 7
}

CARRIER_FUEL_SURCHARGES = {
    "ZIM (שירות מועדף למטעני חומ\"ס וגמישות)" if is_hebrew else "ZIM (Preferred DG & Flexible Service)": {"bess_multiplier": 1.0, "dthc_mult": 1.0},
    "MSC (תעריפים מועדפים)" if is_hebrew else "MSC (Preferred Tariffs)": {"bess_multiplier": 0.82, "dthc_mult": 0.90},
    "Hapag-Lloyd (סטנדרטי)" if is_hebrew else "Hapag-Lloyd (Standard)": {"bess_multiplier": 0.95, "dthc_mult": 0.95},
    "שוק חופשי / ספוט" if is_hebrew else "Spot Market / Free Carrier": {"bess_multiplier": 0.90, "dthc_mult": 0.90}
}

incoterm_options = [
    "DDP (אחריות מלאה כולל מיסים)" if is_hebrew else "DDP (Delivered Duty Paid — Full Scope)",
    "DAP (מסירה באתר ללא פריקה ומכס)" if is_hebrew else "DAP (Delivered at Place — Excl. Unloading & Customs)",
    "CIF (עלות, ביטוח והובלה ימית)" if is_hebrew else "CIF (Cost, Insurance and Freight)",
    "FOB (מסירה על הסיפון בנמל מוצא)" if is_hebrew else "FOB (Free On Board)",
    "EXW (איסוף עצמי ממפעל הספק)" if is_hebrew else "EXW (Ex Works — Factory Pickup)"
]

incoterm = st.sidebar.selectbox(txt["incoterm_label"], incoterm_options, key="sidebar_incoterm")
display_currency = st.sidebar.selectbox(txt["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"], key="sidebar_currency")

forecast_date = st.sidebar.date_input(txt["forecast_label"], value=date(2027, 6, 30), key="sidebar_forecast_date")
market_scenario_options = [
    "שמרני (+8.0% לשנה)" if is_hebrew else "Conservative (+8.0% p.a.)",
    "בסיסי (+4.5% לשנה)" if is_hebrew else "Baseline (+4.5% p.a.)",
    "יציב / ללא שינוי (0.0%)" if is_hebrew else "Stable / No Change (0.0%)"
]
market_scenario = st.sidebar.selectbox(txt["market_label"], market_scenario_options, key="sidebar_market_scenario")

today_date = date.today()
delta_days = (forecast_date - today_date).days
years_diff = max(0.0, delta_days / 365.25)
annual_inflation = 0.08 if ("שמרני" in market_scenario or "Conservative" in market_scenario) else (0.045 if ("בסיסי" in market_scenario or "Baseline" in market_scenario) else 0.0)
trend_multiplier = (1.0 + annual_inflation) ** years_diff

@st.cache_data(ttl=300)
def fetch_live_exchange_rates():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=EUR,ILS", timeout=5)
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            return rates.get("EUR", 0.92), rates.get("ILS", 3.70)
    except Exception:
        pass
    return None, None

live_eur, live_ils = fetch_live_exchange_rates()
if live_eur is None or live_ils is None:
    live_eur, live_ils = 0.92, 3.70

usd_to_eur = st.sidebar.number_input(txt["rate_usd_eur"], value=float(live_eur), step=0.01, min_value=0.0001, key="sidebar_usd_eur")
usd_to_ils = st.sidebar.number_input(txt["rate_usd_ils"], value=float(live_ils), step=0.01, min_value=0.0001, key="sidebar_usd_ils")

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

curr_symbol = "$" if "USD" in display_currency else ("€" if "EUR" in display_currency else "₪")

dest_country = st.sidebar.selectbox(txt["dest_country"], list(VAT_RATES.keys()), index=0, key="sidebar_dest_country")
default_site_placeholder = txt["site_placeholder"]
is_european_dest = (dest_country != "ישראל" and dest_country != "Israel")

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
    st.subheader(txt["equipment_header"])
    st.info(txt["equipment_info"])

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        origin_port = st.selectbox(txt["origin_port"], ORIGIN_PORTS, key="tab1_origin_port")
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["אחר / מותאם"])
        dest_port = st.selectbox(txt["dest_port"], available_dest_ports, key=f"tab1_dest_port_{dest_country}")
        site_address = st.text_input(txt["site_name"], key="site_name_input", placeholder=default_site_placeholder)

    with col_meta2:
        vat_label_text = f"שיעור מע\"מ ({dest_country}) %:" if is_hebrew else f"VAT Rate ({dest_country}) %:"
        applied_vat = st.number_input(vat_label_text, value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country}")
        
        vat_rec_text = "אחוז החזר מע\"מ (%)" if is_hebrew else "VAT Recovery Rate (%)"
        vat_recovery_pct = st.number_input(vat_rec_text, value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        
        vat_sup_text = "המע\"מ משולם על ידי הספק במסגרת תנאי המסחר" if is_hebrew else "VAT paid by supplier under commercial terms"
        vat_paid_by_supplier = st.checkbox(vat_sup_text, value=False, key="tab1_vat_supplier")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("#### BESS Containers" if not is_hebrew else "#### מכולות סוללה (BESS)")
        bess_count = st.number_input("BESS Containers (40' HC DG):" if not is_hebrew else "כמות מכולות BESS (40' HC DG):", min_value=0, value=20, step=1, key="proj_bess_count")
        bess_exw = st.number_input("EXW Unit Cost per BESS ($):" if not is_hebrew else "עלות EXW ליחידת BESS ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_bess_exw")

        oog_count = st.number_input("OOG Containers:" if not is_hebrew else "כמות מכולות חריגות (OOG):", min_value=0, value=0, step=1, key="proj_oog_count")
        oog_exw = st.number_input("EXW Unit Cost per OOG ($):" if not is_hebrew else "עלות EXW ליחידת OOG ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_oog_exw")

    with col_q2:
        st.markdown("#### MVS & Transformers" if not is_hebrew else "#### תחנות המרה ושנאים")
        mvs_count = st.number_input("MVS Stations:" if not is_hebrew else "כמות תחנות מתח גבוה (MVS):", min_value=0, value=4, step=1, key="proj_mvs_count")
        mvs_exw = st.number_input("EXW Unit Cost per MVS ($):" if not is_hebrew else "עלות EXW ליחידת MVS ($):", min_value=0.0, value=250000.0, step=10000.0, key="proj_mvs_exw")

        transformer_count = st.number_input("Main Transformers:" if not is_hebrew else "כמות שנאים ראשיים:", min_value=0, value=2, step=1, key="proj_trans_count")
        transformer_exw = st.number_input("EXW Unit Cost per Transformer ($):" if not is_hebrew else "עלות EXW ליחידת שנאי ($):", min_value=0.0, value=120000.0, step=10000.0, key="proj_trans_exw")

    with col_q3:
        st.markdown("#### Accessories & PV" if not is_hebrew else "#### ציוד נלווה וסולארי")
        access_count = st.number_input("Accessory Containers:" if not is_hebrew else "מכולות ציוד נלווה / יבש:", min_value=0, value=2, step=1, key="proj_access_count")
        access_exw = st.number_input("EXW Unit Cost per Accessory Container ($):" if not is_hebrew else "עלות EXW ליחידת ציוד נלווה ($):", min_value=0.0, value=50000.0, step=5000.0, key="proj_access_exw")

        solar_count = st.number_input("Solar PV Units:" if not is_hebrew else "יחידות פאנלים סולאריים (PV):", min_value=0, value=0, step=1, key="proj_solar_count")
        solar_exw = st.number_input("EXW Unit Cost per Solar Unit ($):" if not is_hebrew else "עלות EXW ליחידה סולארית ($):", min_value=0.0, value=300000.0, step=10000.0, key="proj_solar_exw")

    total_containers_project = max(1, bess_count + oog_count + mvs_count + transformer_count + access_count + solar_count)
    total_exw_project = (
        (bess_count * bess_exw) + (oog_count * oog_exw) + 
        (mvs_count * mvs_exw) + (transformer_count * transformer_exw) + 
        (access_count * access_exw) + (solar_count * solar_exw)
    )
    is_bess = (bess_count > 0 or oog_count > 0)
    is_dg = is_bess

    if is_hebrew:
        st.success(f"📊 סה\"כ יחידות לפרויקט: {total_containers_project} | סה\"כ ערך ציוד במפעל (EXW): **${total_exw_project:,.2f}**")
    else:
        st.success(f"📊 Total Project Units: {total_containers_project} | Total Factory EXW Value: **${total_exw_project:,.2f}**")

with tab2:
    st.subheader("🚢 Ocean Freight, BAF & Destination THC" if not is_hebrew else "🚢 תעריפי הובלה ימית, היטל דלק (BAF) ודמי טיפול בנמל יעד (DTHC)")
    
    carrier_label = "Shipping Line / Carrier:" if not is_hebrew else "בחירת חברת ספנות:"
    selected_carrier = st.selectbox(carrier_label, list(CARRIER_FUEL_SURCHARGES.keys()), key="tab2_carrier")
    carrier_data = CARRIER_FUEL_SURCHARGES[selected_carrier]

    baf_incl_label = "Bunker Adjustment Factor (BAF) already included in ocean freight" if not is_hebrew else "תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית"
    baf_included = st.checkbox(baf_incl_label, value=False, key="tab2_baf_incl")

    st.markdown("##### 1. Ocean Freight per Unit:" if not is_hebrew else "##### 1. עלות הובלה ימית ליחידה:")
    oc_col1, oc_col2, oc_col3 = st.columns(3)
    with oc_col1:
        unit_freight_bess = st.number_input("BESS Freight ($):" if not is_hebrew else "הובלת BESS ($):", value=31850.0 * carrier_data["bess_multiplier"], step=500.0, key="freight_bess")
        unit_freight_oog = st.number_input("OOG Freight ($):" if not is_hebrew else "הובלת OOG ($):", value=29900.0, step=500.0, key="freight_oog")
    with oc_col2:
        unit_freight_mvs = st.number_input("MVS Freight ($):" if not is_hebrew else "הובלת MVS ($):", value=4200.0, step=200.0, key="freight_mvs")
        unit_freight_trans = st.number_input("Transformer Freight ($):" if not is_hebrew else "הובלת שנאי ($):", value=5500.0, step=200.0, key="freight_trans")
    with oc_col3:
        unit_freight_access = st.number_input("Accessory Freight ($):" if not is_hebrew else "הובלת ציוד נלווה ($):", value=3200.0, step=200.0, key="freight_access")
        unit_freight_solar = st.number_input("Solar PV Freight ($):" if not is_hebrew else "הובלת סולארי ($):", value=3360.0, step=200.0, key="freight_solar")

    st.markdown("---")
    st.markdown("##### 2. Bunker Adjustment Factor (BAF) per TEU:" if not is_hebrew else "##### 2. היטל דלק ימי (BAF) מחושב לפי נפח TEU:")
    baf_mult = carrier_data["dthc_mult"]
    base_baf_per_teu = st.number_input("Base BAF Rate per TEU ($):" if not is_hebrew else "תעריף BAF בסיסי ל־TEU יחיד ($):", value=420.0 * baf_mult, step=20.0, key="baf_per_teu")

    teu_bess, teu_oog, teu_mvs, teu_trans, teu_access, teu_solar = 2.0, 2.0, 1.0, 1.0, 1.0, 1.0

    baf_bess = 0.0 if baf_included else (base_baf_per_teu * teu_bess)
    baf_oog = 0.0 if baf_included else (base_baf_per_teu * teu_oog)
    baf_mvs = 0.0 if baf_included else (base_baf_per_teu * teu_mvs)
    baf_trans = 0.0 if baf_included else (base_baf_per_teu * teu_trans)
    baf_access = 0.0 if baf_included else (base_baf_per_teu * teu_access)
    baf_solar = 0.0 if baf_included else (base_baf_per_teu * teu_solar)

    st.markdown("---")
    st.markdown("##### 3. Destination Terminal Handling Charges (Destination THC):" if not is_hebrew else "##### 3. דמי טיפול בנמל יעד (Destination THC):")
    dthc_mult = carrier_data["dthc_mult"]
    
    dh_col1, dh_col2, dh_col3 = st.columns(3)
    with dh_col1:
        dthc_bess = st.number_input("BESS Destination THC ($):" if not is_hebrew else "DTHC מכולת BESS ($):", value=650.0 * dthc_mult, step=50.0, key="dthc_bess")
        dthc_oog = st.number_input("OOG Destination THC ($):" if not is_hebrew else "DTHC מכולת OOG ($):", value=850.0 * dthc_mult, step=50.0, key="dthc_oog")
    with dh_col2:
        dthc_mvs = st.number_input("MVS Destination THC ($):" if not is_hebrew else "DTHC תחנת MVS ($):", value=420.0 * dthc_mult, step=30.0, key="dthc_mvs")
        dthc_trans = st.number_input("Transformer Destination THC ($):" if not is_hebrew else "DTHC שנאי ($):", value=480.0 * dthc_mult, step=30.0, key="dthc_trans")
    with dh_col3:
        dthc_access = st.number_input("Accessory Destination THC ($):" if not is_hebrew else "DTHC ציוד נלווה ($):", value=280.0 * dthc_mult, step=20.0, key="dthc_access")
        dthc_solar = st.number_input("Solar PV Destination THC ($):" if not is_hebrew else "DTHC פאנלים ($):", value=300.0 * dthc_mult, step=20.0, key="dthc_solar")

    total_base_ocean_freight = (
        (bess_count * unit_freight_bess) + (oog_count * unit_freight_oog) +
        (mvs_count * unit_freight_mvs) + (transformer_count * unit_freight_trans) +
        (access_count * unit_freight_access) + (solar_count * unit_freight_solar)
    )
    total_baf_ocean = (
        (bess_count * baf_bess) + (oog_count * baf_oog) +
        (mvs_count * baf_mvs) + (transformer_count * baf_trans) +
        (access_count * baf_access) + (solar_count * baf_solar)
    )
    total_destination_thc = (
        (bess_count * dthc_bess) + (oog_count * dthc_oog) +
        (mvs_count * dthc_mvs) + (transformer_count * dthc_trans) +
        (access_count * dthc_access) + (solar_count * dthc_solar)
    )

    china_inland_drayage = 2200.0 * (total_containers_project / 10)
    china_origin_thc = 1300.0 * (total_containers_project / 10)
    heavy_lift_survey = 2500.0
    
    customs_duty_pct = 0.0 if (dest_country == "ישראל" or dest_country == "Israel") else 2.7
    insurance_pct = DEFAULT_INSURANCE_RATES.get(dest_country, 0.15)

with tab3:
    st.subheader("🚚 Port-to-Site Inland Drayage & Logistics" if not is_hebrew else "🚚 הובלה יבשתית מנמל הפריקה לאתר הפרויקט (Port to Site)")
    
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        drayage_bess = st.number_input("BESS Trucking per unit ($):" if not is_hebrew else "הובלת משאיות BESS ליחידה ($):", value=3200.0, step=200.0, key="dray_bess")
        drayage_oog = st.number_input("OOG Trucking per unit ($):" if not is_hebrew else "הובלת משאיות OOG ליחידה ($):", value=3800.0, step=200.0, key="dray_oog")
    with dr_col2:
        drayage_mvs = st.number_input("MVS Trucking per unit ($):" if not is_hebrew else "הובלת משאיות MVS ליחידה ($):", value=1400.0, step=100.0, key="dray_mvs")
        drayage_trans = st.number_input("Transformer Trucking per unit ($):" if not is_hebrew else "הובלת משאיות שנאי ליחידה ($):", value=1800.0, step=100.0, key="dray_trans")
    with dr_col3:
        drayage_access = st.number_input("Accessory Trucking per unit ($):" if not is_hebrew else "הובלת ציוד נלווה ליחידה ($):", value=850.0, step=100.0, key="dray_access")
        drayage_solar = st.number_input("Solar PV Trucking per unit ($):" if not is_hebrew else "הובלת ציוד סולארי ליחידה ($):", value=950.0, step=100.0, key="dray_solar")

    inland_drayage_total_base = (
        (bess_count * drayage_bess) + (oog_count * drayage_oog) +
        (mvs_count * drayage_mvs) + (transformer_count * drayage_trans) +
        (access_count * drayage_access) + (solar_count * drayage_solar)
    )

    free_days = DEFAULT_FREE_DAYS.get(dest_country, 7)
    actual_port_days = 12
    demurrage_daily_rate = 250.0 if is_dg else 150.0
    use_external_storage = True
    ext_storage_days = 15
    ext_storage_daily_rate = 65.0 if is_dg else 45.0
    include_site_crane = True
    site_crane_unloading = 8500.0
    ddp_contingency_pct = 5.0
    include_delay_scenario = False

with tab4:
    st.subheader("⚖️ Regulation & Mandatory Approvals" if not is_hebrew else "⚖️ רגולציה ואישורים מנדטוריים")

    if dest_country == "ישראל" or dest_country == "Israel":
        st.markdown("### 🇮🇱 Dangerous Goods Regulations & Transport Permits (Israel)")
        st.error("🚨 **Legal Requirement in Israel:** Individual transport approval from the Ministry of Transport Inspection Division for each BESS container.")
        mot_fee_per_bess = st.number_input("Ministry of Transport Approval Fee per BESS ($):" if not is_hebrew else "עלות אגרת אישור הובלה ממשרד התחבורה ליחידת BESS ($):", value=350.0, step=50.0, key="mot_fee_input")
        mot_total_approval_cost = mot_fee_per_bess * float(bess_count + oog_count)

        st.warning("⚠️ **Port Requirement:** Hazardous materials port inspection, supervision, and fire department approvals.")
        local_regulatory_permits = st.number_input("Port Hazmat Permits Total Cost ($):" if not is_hebrew else "עלות כוללת להיתרי חומ\"ס נמלים ($):", value=1500.0, step=100.0, key="reg_cost_input")
        
        epr_recycling_total_usd = 0.0
        battery_passport_total_usd = 0.0
        decommissioning_total_usd = 0.0
        include_mot_approval = True
        include_regulatory = True

    else:
        st.markdown(f"### 🇪🇺 European Regulatory Compliance & Extended Producer Responsibility ({dest_country})")
        st.error("🚨 **Mandatory in EU:** Digital EU Battery Passport & Supply Chain Documentation.")
        battery_passport_flat = st.number_input("Total Battery Passport & Documentation Cost ($):" if not is_hebrew else "עלות כוללת לדרכון סוללות ותיעוד ($):", value=1200.0, step=100.0, key="bp_cost_input")
        battery_passport_total_usd = battery_passport_flat

        st.warning("⚠️ **Mandatory in EU:** Extended Producer Responsibility (EPR / Ongoing Recycling Fees).")
        epr_fee_per_unit = st.number_input("Ongoing EPR Fee per BESS unit ($):" if not is_hebrew else "עלות EPR שוטף ליחידת BESS ($):", value=450.0, step=50.0, key="epr_unit_input")
        epr_recycling_total_usd = epr_fee_per_unit * float(bess_count + oog_count)

        reg_checkbox_label = "Include local European site entry permits & municipal clearance fees" if not is_hebrew else "הכלל אגרות היתרי כניסה והיערכות אתר מקומיים באירופה"
        include_regulatory = st.checkbox(reg_checkbox_label, value=True, key="reg_permits_toggle")
        local_regulatory_permits = st.number_input("Local Permits Cost ($):" if not is_hebrew else "עלות היתרים מקומיים ($):", value=600.0, step=100.0, key="reg_cost_input") if include_regulatory else 0.0

        mot_total_approval_cost = 0.0
        include_mot_approval = False

        st.markdown("---")
        st.markdown("### 🔄 Decommissioning & End-of-Life Financial Provision")
        with st.expander("📌 Management & Future Provision (Optional for European Project Manager)", expanded=False):
            st.markdown("""
            Management tool allowing future budgetary provisions for:
            * Physical dismantling of battery modules and containers.
            * Voltage neutralization and preliminary safety tests.
            * Separation of energy cells and hazardous materials prior to final recycling.
            """ if not is_hebrew else """
            כלי ניהול המאפשר להוסיף הפרשה תקציבית צופה פני עתיד עבור:
            * פירוק פיזי של מודולי הסוללות והמכולה.
            * נטרול מתח ובדיקות בטיחות מקדימות.
            * הפרדת תאי אנרגיה וחומרים מסוכנים לפני מחזור סופי.
            """)
            decom_toggle_label = "Add Decommissioning & End-of-Life Financial Provision" if not is_hebrew else "הוסף תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)"
            include_decommissioning_provision = st.checkbox(decom_toggle_label, value=False, key="decom_toggle")
            
            if include_decommissioning_provision:
                decom_unit_label = "Estimated Decommissioning & Recycling Cost per BESS ($):" if not is_hebrew else "עלות מוערכת לפירוק ומחזור ליחידת BESS ($):"
                decom_cost_per_bess = st.number_input(decom_unit_label, value=2200.0, step=200.0, key="decom_unit_input")
                decommissioning_total_usd = decom_cost_per_bess * float(bess_count + oog_count)
                st.info(f"💡 Total planned decommissioning provision for {int(bess_count + oog_count)} BESS/OOG units: **${decommissioning_total_usd:,.2f}**")
            else:
                decommissioning_total_usd = 0.0

    st.markdown("---")
    hl_toggle_label = "Heavy-Lift Survey / Anchor Crane Required" if not is_hebrew else "נדרש סקר מטענים כבדים / מנוף עוגן (Heavy-Lift Survey)"
    requires_heavy_lift = st.checkbox(hl_toggle_label, value=is_bess, key="hl_survey_toggle")
    heavy_lift_survey_cost = st.number_input("Heavy-Lift Survey Cost ($):" if not is_hebrew else "עלות סקר מטענים כבדים ($):", value=2500.0, step=250.0, key="hl_cost_input") if requires_heavy_lift else 0.0

if is_european_dest and tab5_eu is not None:
    with tab5_eu:
        st.subheader("🗺️ Indicative European Route Options" if not is_hebrew else "🗺️ הנחות מסלולים אינדיקטיביות באירופה")
        st.info("Analysis of discharge port alternatives and inland routing to project site." if not is_hebrew else "ניתוח חלופות נמלי פריקה והובלה יבשתית לאתר הפרויקט.")

if is_european_dest and tab_projects is not None:
    with tab_projects:
        st.subheader("📂 Enlight Projects 2027-2028 (Shira Control)" if not is_hebrew else "📂 פרויקטי Enlight 2027-2028 (ניהול ובקרה — שירה)")
        st.info("Enlight renewable energy and storage tracking table in Europe with full control columns." if not is_hebrew else "טבלת מעקב פרויקטי אגירה ואנרגיה מתחדשת של קבוצת אנלייט באירופה עם כל עמודות הבקרה המלאות.")

        shira_full_table_data = [
            {"Name": "no number", "CONT": 9, "Site": "Genzano", "Country site": "Italy, Europe", "zip code": "", "Supplier": "JINKO", "Product Category": "PV Modules", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 32, "Site": "Mosciska", "Country site": "Poland, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 480, "Site": "Jupiter", "Country site": "GERMANY, Europe", "zip code": "", "Supplier": "-", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 44, "Site": "Picasso", "Country site": "Sweden, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 15, "Site": "Nardo", "Country site": "Italy, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""}
        ]

        df_shira_full = pd.DataFrame(shira_full_table_data)
        st.dataframe(df_shira_full, use_container_width=True)
        st.success("✅ All original Shira control columns successfully loaded!" if not is_hebrew else "✅ כל עמודות הבקרה המקוריות של שירה נטענו בהצלחה!")

trended_exw = total_exw_project * trend_multiplier
trended_ocean_freight = (total_base_ocean_freight + total_baf_ocean) * trend_multiplier
trended_drayage = inland_drayage_total_base * trend_multiplier

total_ocean_freight = trended_ocean_freight
inland_drayage_total_usd = trended_drayage

cif_valuation_base = trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)
destination_thc_total = total_destination_thc  

indicative_vat_base_import_usd = customs_valuation_base_usd + customs_duty_usd + destination_thc_total
vat_total_usd = indicative_vat_base_import_usd * (applied_vat / 100.0)
is_delivery_inclusive = incoterm.startswith("DDP") or incoterm.startswith("DAP")
supplier_vat_component = vat_total_usd if (vat_paid_by_supplier and is_delivery_inclusive) else 0.0

ddp_supplier_scope_ex_vat = (
    trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + 
    insurance_total_usd + customs_duty_usd + destination_thc_total + inland_drayage_total_usd
)
ddp_supplier_scope_incl_vat = ddp_supplier_scope_ex_vat + supplier_vat_component

overdue_days = max(0, actual_port_days - free_days)
demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(total_containers_project)
external_storage_total_usd = (float(ext_storage_days) * ext_storage_daily_rate * float(total_containers_project)) if use_external_storage else 0.0

active_regulatory_permits = (local_regulatory_permits if include_regulatory else 0.0) + (mot_total_approval_cost if include_mot_approval else 0.0)
active_site_crane = site_crane_unloading if include_site_crane else 0.0
active_heavy_lift = heavy_lift_survey_cost if requires_heavy_lift else 0.0
effective_delay_cost = (demurrage_total_usd + external_storage_total_usd) if include_delay_scenario else 0.0

project_delivery_cost = (
    ddp_supplier_scope_ex_vat + 
    active_site_crane + 
    active_regulatory_permits + 
    epr_recycling_total_usd + 
    battery_passport_total_usd + 
    active_heavy_lift + 
    effective_delay_cost +
    decommissioning_total_usd
)

supplier_commercial_price_options = {
    incoterm_options[0]: ddp_supplier_scope_incl_vat,
    incoterm_options[1]: ddp_supplier_scope_ex_vat,
    incoterm_options[2]: trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd,
    incoterm_options[3]: trended_exw + china_inland_drayage + china_origin_thc,
    incoterm_options[4]: trended_exw
}

supplier_scope_total = supplier_commercial_price_options.get(incoterm, trended_exw)
buyer_direct_payment_usd = max(0.0, project_delivery_cost - supplier_scope_total)

effective_vat_cash = 0.0 if (vat_paid_by_supplier and is_delivery_inclusive) else vat_total_usd
recoverable_vat = vat_total_usd * (vat_recovery_pct / 100.0)
effective_non_recoverable_vat = 0.0 if (vat_paid_by_supplier and is_delivery_inclusive) else (vat_total_usd - recoverable_vat)

buyer_supply_chain_total = project_delivery_cost
contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
economic_cost_ex_vat = total_landed_cost_ex_vat + effective_non_recoverable_vat
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + effective_vat_cash

display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_scope_total, display_currency)
buyer_direct_val, _ = convert_from_usd(buyer_direct_payment_usd, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
econ_val, _ = convert_from_usd(economic_cost_ex_vat, display_currency)

with tab_summary:
    summary_title = f"📊 Financial & Regulatory Control Report — {incoterm} ({display_currency})" if not is_hebrew else f"📊 דוח בקרה פיננסית ורגולטורית — {incoterm} ({display_currency})"
    st.subheader(summary_title)
    
    m1_title = "Total Landed Cost (Excl. VAT)" if not is_hebrew else "עלות נחיתה (לפני מע\"מ)"
    m2_title = "Total Economic Cost" if not is_hebrew else "עלות כלכלית כוללת"
    m3_title = "Total Cash Requirement" if not is_hebrew else "דרישת מזומנים כוללת"
    m4_title = "Direct Supplier Payment" if not is_hebrew else "תשלום ישיר לספק"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{m1_title}</div>
            <div class="metric-value">{curr_symbol} {display_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{m2_title}</div>
            <div class="metric-value">{curr_symbol} {econ_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{m3_title}</div>
            <div class="metric-value">{curr_symbol} {cash_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{m4_title}</div>
            <div class="metric-value">{curr_symbol} {supplier_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    breakdown_header = "📋 Project Budget Cost Breakdown" if not is_hebrew else "📋 פירוט רכיבי תקציב הפרויקט (Cost Breakdown)"
    st.subheader(breakdown_header)

    ex_exw, _ = convert_from_usd(trended_exw, display_currency)
    ex_ch_inland, _ = convert_from_usd(china_inland_drayage + china_origin_thc, display_currency)
    ex_ocean, _ = convert_from_usd(total_base_ocean_freight * trend_multiplier, display_currency)
    ex_baf, _ = convert_from_usd(total_baf_ocean * trend_multiplier, display_currency)
    ex_dthc, _ = convert_from_usd(destination_thc_total, display_currency)
    ex_insur, _ = convert_from_usd(insurance_total_usd, display_currency)
    ex_customs, _ = convert_from_usd(customs_duty_usd, display_currency)
    ex_drayage, _ = convert_from_usd(inland_drayage_total_usd, display_currency)
    ex_reg, _ = convert_from_usd(active_regulatory_permits, display_currency)
    ex_crane, _ = convert_from_usd(active_site_crane, display_currency)
    ex_decom, _ = convert_from_usd(decommissioning_total_usd, display_currency)
    ex_cont, _ = convert_from_usd(contingency_usd, display_currency)
    ex_total, _ = convert_from_usd(total_landed_cost_ex_vat, display_currency)

    unit_exw, _ = convert_from_usd(trended_exw / max(1, total_containers_project), display_currency)
    unit_ch_inland, _ = convert_from_usd((china_inland_drayage + china_origin_thc) / max(1, total_containers_project), display_currency)
    unit_ocean, _ = convert_from_usd((total_base_ocean_freight) / max(1, total_containers_project), display_currency)
    unit_baf, _ = convert_from_usd((total_baf_ocean) / max(1, total_containers_project), display_currency)
    unit_dthc, _ = convert_from_usd((total_destination_thc) / max(1, total_containers_project), display_currency)
    unit_drayage, _ = convert_from_usd(inland_drayage_total_base / max(1, total_containers_project), display_currency)

    th_item = "Project Cost Item" if not is_hebrew else "רכיב עלות בפרויקט"
    th_qty = "Basis / Qty" if not is_hebrew else "כמות / בסיס חישוב"
    th_unit = "Unit Cost" if not is_hebrew else "עלות ליחידה"
    th_total = "Total Amount" if not is_hebrew else "סה\"כ סעיף"

    html_table = f"""
    <table class="custom-finance-table">
        <thead>
            <tr>
                <th style="width: 40%;">{th_item}</th>
                <th class="center" style="width: 20%;">{th_qty}</th>
                <th class="left" style="width: 20%;">{th_unit}</th>
                <th class="left" style="width: 20%;">{th_total}</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{'Equipment EXW Value' if not is_hebrew else 'ערך ציוד במפעל (Equipment EXW)'}</td>
                <td class="center">{int(total_containers_project)} units</td>
                <td class="left">{curr_symbol} {unit_exw:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_exw:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'China Inland & Origin THC' if not is_hebrew else 'הובלה יבשתית ונמלית במוצא'}</td>
                <td class="center">{int(total_containers_project)} units</td>
                <td class="left">{curr_symbol} {unit_ch_inland:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ch_inland:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Ocean Freight (Base)' if not is_hebrew else 'הובלה ימית בסיסית'}</td>
                <td class="center">{int(total_containers_project)} containers</td>
                <td class="left">{curr_symbol} {unit_ocean:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ocean:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Bunker Adjustment Factor (BAF)' if not is_hebrew else 'היטל דלק ימי לפי TEU (BAF)'}</td>
                <td class="center">{int(total_containers_project)} units</td>
                <td class="left">{curr_symbol} {unit_baf:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_baf:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Destination THC' if not is_hebrew else 'דמי טיפול בנמל יעד (Destination THC)'}</td>
                <td class="center">{int(total_containers_project)} units</td>
                <td class="left">{curr_symbol} {unit_dthc:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_dthc:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Marine Insurance' if not is_hebrew else 'ביטוח ימי'}</td>
                <td class="center">% of CIF</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_insur:,.2f}</b></td>
            </tr>
            <tr>
                <td>{f'Import Customs Duty ({customs_duty_pct}%)' if not is_hebrew else f'מכס יבוא ({customs_duty_pct}%)'}</td>
                <td class="center">Classification</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_customs:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Inland Drayage (Port to Site)' if not is_hebrew else 'הובלה יבשתית מנמל לאתר'}</td>
                <td class="center">{int(total_containers_project)} trucks</td>
                <td class="left">{curr_symbol} {unit_drayage:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_drayage:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Regulatory & Local Permits' if not is_hebrew else 'רגולציה מקומית ואישורי חומ\"ס / משרד התחבורה'}</td>
                <td class="center">Total Expense</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_reg:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Site Crane & Unloading' if not is_hebrew else 'עגורן מנוף ופריקה באתר'}</td>
                <td class="center">Total Expense</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_crane:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Decommissioning Provision' if not is_hebrew else 'הפרשת מחזור סוף חיים (Decommissioning)'}</td>
                <td class="center">{int(bess_count + oog_count)} BESS</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_decom:,.2f}</b></td>
            </tr>
            <tr>
                <td>{'Contingency (5%)' if not is_hebrew else 'בלת״ם פרויקטי (5%)'}</td>
                <td class="center">5% Supply Chain</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_cont:,.2f}</b></td>
            </tr>
            <tr class="total-row">
                <td>{'Total Landed Cost (Excl. VAT)' if not is_hebrew else 'סה\"כ עלות נחיתה לפני מע\"מ (Total Landed Cost)'}</td>
                <td class="center">-</td>
                <td class="left">-</td>
                <td class="left" style="font-size: 1.05rem; color: #1e3d59;"><b>{curr_symbol} {ex_total:,.2f}</b></td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    export_header = "📥 Excel Export" if not is_hebrew else "📥 ייצוא נתונים לדוח אקסל (Excel Export)"
    st.subheader(export_header)
    
    excel_summary_data = [
        ["Project Cost Item", "Basis / Qty", f"Unit Cost ({curr_symbol})", f"Total ({curr_symbol})"],
        ["Equipment EXW", f"{int(total_containers_project)} units", trended_exw / max(1, total_containers_project), trended_exw],
        ["China Inland & Origin THC", f"{int(total_containers_project)} units", (china_inland_drayage + china_origin_thc) / max(1, total_containers_project), china_inland_drayage + china_origin_thc],
        ["Ocean Freight", f"{int(total_containers_project)} containers", total_base_ocean_freight / max(1, total_containers_project), total_base_ocean_freight * trend_multiplier],
        ["BAF", f"{int(total_containers_project)} units", total_baf_ocean / max(1, total_containers_project), total_baf_ocean * trend_multiplier],
        ["Destination THC", f"{int(total_containers_project)} units", total_destination_thc / max(1, total_containers_project), destination_thc_total],
        ["Marine Insurance", "% of CIF", 0, insurance_total_usd],
        ["Import Customs Duty", f"({customs_duty_pct}%)", 0, customs_duty_usd],
        ["Inland Drayage Port-to-Site", f"{int(total_containers_project)} trucks", inland_drayage_total_base / max(1, total_containers_project), inland_drayage_total_usd],
        ["Regulatory & Permits", "Total", 0, active_regulatory_permits],
        ["Site Crane Unloading", "Total", 0, active_site_crane],
        ["Decommissioning Provision", f"{int(bess_count + oog_count)} BESS", 0, decommissioning_total_usd],
        ["Contingency", "5%", 0, contingency_usd],
        ["Total Landed Cost (Excl. VAT)", "-", 0, total_landed_cost_ex_vat]
    ]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = pd.DataFrame(excel_summary_data[1:], columns=excel_summary_data[0])
        df_export.to_excel(writer, sheet_name='Cost Summary', index=False)
        
        ws = writer.sheets['Cost Summary']
        ws.views.sheetView[0].rightToLeft = is_hebrew

    excel_data = output.getvalue()

    download_btn_label = "📥 Download Full Excel Report" if not is_hebrew else "📥 הורד דוח פיננסי מלא לאקסל (Download Excel Report)"
    st.download_button(
        label=download_btn_label,
        data=excel_data,
        file_name=f"TerraVol_Project_Report_{dest_country}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
