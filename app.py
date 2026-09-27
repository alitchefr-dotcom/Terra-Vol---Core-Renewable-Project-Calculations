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

st.sidebar.header("🌐 שפה / Language")
lang = st.sidebar.radio("בחר שפה / Select Language:", ["עברית", "English"], index=0, key="lang_select")
is_hebrew = (lang == "עברית")
current_lang = "he" if is_hebrew else "en"

# מילון תרגום מדויק ונקי לממשק המשתמש בלבד
T = {
    "he": {
        "caption": "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, תנאי סחר, רגולציה ותחזית שוק",
        "incoterm_label": "תנאי סחר מסחרי (אחריות ספק):",
        "currency_label": "מטבע תצוגה ראשי:",
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
        "site_label": "שם אתר הפרויקט:",
        "site_ph": "אשלים / עמק הירדן (אנלייט)",
        "eq_header": "הגדרת רכיבי הציוד וכמויות לפרויקט",
        "eq_info": "הזן את כמויות מכולות הסוללה, הממירים, השנאים ועלויות הייצור במפעל (EXW).",
        "summary_title": "📊 דוח בקרה פיננסית ורגולטורית",
        "breakdown_title": "📋 פירוט רכיבי תקציב הפרויקט (Cost Breakdown)",
        "excel_btn": "📥 הורד דוח פיננסי מלא לאקסל (Download Excel Report)",
        "col_item": "רכיב עלות בפרויקט",
        "col_qty": "כמות / בסיס חישוב",
        "col_unit": "עלות ליחידה",
        "col_total": "סה\"כ סעיף",
    },
    "en": {
        "caption": "Professional Project Calculator for Target Costs, Incoterms, Regulation & Market Forecast",
        "incoterm_label": "Commercial Incoterm (Supplier Scope):",
        "currency_label": "Main Display Currency:",
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
        "site_label": "Project Site Name:",
        "site_ph": "Project Site / Site Address",
        "eq_header": "Equipment Mix & Quantities Configuration",
        "eq_info": "Enter BESS container quantities, inverters, transformers, and factory EXW production costs.",
        "summary_title": "📊 Financial & Regulatory Control Report",
        "breakdown_title": "📋 Project Budget Cost Breakdown",
        "excel_btn": "📥 Download Full Excel Report",
        "col_item": "Project Cost Item",
        "col_qty": "Basis / Qty",
        "col_unit": "Unit Cost",
        "col_total": "Total Amount",
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

ORIGIN_PORTS = ["שאנגחאי (Shanghai)", "נינגבו (Ningbo)", "שנג'ן (Shenzhen)", "צ'ינגדאו (Qingdao)"]

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
    "ישראל": 4, "רומניה": 7, "פולין": 7, "גרמניה": 7, 
    "שוודיה": 7, "יוון": 7, "ספרד": 7, "איטליה": 7, "בולגריה": 7, "הונגריה": 7, "אחר / מותאם": 7
}

CARRIER_FUEL_SURCHARGES = {
    "ZIM (שירות מועדף למטעני חומ\"ס וגמישות)": {"bess_multiplier": 1.0, "dthc_mult": 1.0},
    "MSC (תעריפים מועדפים)": {"bess_multiplier": 0.82, "dthc_mult": 0.90},
    "Hapag-Lloyd (סטנדרטי)": {"bess_multiplier": 0.95, "dthc_mult": 0.95},
    "שוק חופשי / ספוט": {"bess_multiplier": 0.90, "dthc_mult": 0.90}
}

incoterm = st.sidebar.selectbox(txt["incoterm_label"], ["DDP (אחריות מלאה כולל מיסים)", "DAP (מסירה באתר ללא פריקה ומכס)", "CIF (עלות, ביטוח והובלה ימית)", "FOB (מסירה על הסיפון בנמל מוצא)", "EXW (איסוף עצמי ממפעל הספק)"], key="sidebar_incoterm")
display_currency = st.sidebar.selectbox(txt["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"], key="sidebar_currency")

forecast_date = st.sidebar.date_input("תאריך יעד לאספקה באתר / Delivery Target Date:", value=date(2027, 6, 30), key="sidebar_forecast_date")
market_scenario = st.sidebar.selectbox("תחזית אינפלציה ומגמת שוק / Market Trend:", ["שמרני (+8.0% לשנה)", "בסיסי (+4.5% לשנה)", "יציב / ללא שינוי (0.0%)"], key="sidebar_market_scenario")

today_date = date.today()
delta_days = (forecast_date - today_date).days
years_diff = max(0.0, delta_days / 365.25)
annual_inflation = 0.08 if "שמרני" in market_scenario else (0.045 if "בסיסי" in market_scenario else 0.0)
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

usd_to_eur = st.sidebar.number_input("שער המרה USD ל־EUR / USD-EUR Rate:", value=float(live_eur), step=0.01, min_value=0.0001, key="sidebar_usd_eur")
usd_to_ils = st.sidebar.number_input("שער המרה USD ל־ILS / USD-ILS Rate:", value=float(live_ils), step=0.01, min_value=0.0001, key="sidebar_usd_ils")

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

curr_symbol = "$" if "USD" in display_currency else ("€" if "EUR" in display_currency else "₪")

dest_country = st.sidebar.selectbox(txt["dest_country"], list(VAT_RATES.keys()), index=0, key="sidebar_dest_country")
default_site_placeholder = txt["site_ph"]
is_european_dest = (dest_country != "ישראל")

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
        origin_port = st.selectbox(txt["origin_port"], ORIGIN_PORTS, key="tab1_origin_port")
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["אחר / מותאם"])
        dest_port = st.selectbox(txt["dest_port"], available_dest_ports, key=f"tab1_dest_port_{dest_country}")
        site_address = st.text_input(txt["site_label"], key="site_name_input", placeholder=default_site_placeholder)

    with col_meta2:
        applied_vat = st.number_input(f"שיעור מע\"מ ({dest_country}) % / VAT %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country}")
        vat_recovery_pct = st.number_input("אחוז החזר מע\"מ (%) / VAT Recovery %", value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        vat_paid_by_supplier = st.checkbox("המע\"מ משולם על ידי הספק / VAT paid by supplier", value=False, key="tab1_vat_supplier")

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

    if is_hebrew:
        st.success(f"📊 סה\"כ יחידות לפרויקט: {total_containers_project} | סה\"כ ערך ציוד במפעל (EXW): **${total_exw_project:,.2f}**")
    else:
        st.success(f"📊 Total Project Units: {total_containers_project} | Total Factory EXW Value: **${total_exw_project:,.2f}**")

with tab2:
    st.subheader("🚢 תעריפי הובלה ימית, היטל דלק (BAF) ודמי טיפול בנמל יעד (DTHC)" if is_hebrew else "🚢 Ocean Freight, BAF & Destination THC")
    
    selected_carrier = st.selectbox("בחירת חברת ספנות:" if is_hebrew else "Shipping Line / Carrier:", list(CARRIER_FUEL_SURCHARGES.keys()), key="tab2_carrier")
    carrier_data = CARRIER_FUEL_SURCHARGES[selected_carrier]

    baf_included = st.checkbox("תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית" if is_hebrew else "Bunker Adjustment Factor (BAF) included in ocean freight", value=False, key="tab2_baf_incl")

    st.markdown("##### 1. עלות הובלה ימית ליחידה:" if is_hebrew else "##### 1. Ocean Freight per Unit:")
    oc_col1, oc_col2, oc_col3 = st.columns(3)
    with oc_col1:
        unit_freight_bess = st.number_input("הובלת BESS ($):" if is_hebrew else "BESS Freight ($):", value=31850.0 * carrier_data["bess_multiplier"], step=500.0, key="freight_bess")
        unit_freight_oog = st.number_input("הובלת OOG ($):" if is_hebrew else "OOG Freight ($):", value=29900.0, step=500.0, key="freight_oog")
    with oc_col2:
        unit_freight_mvs = st.number_input("הובלת MVS ($):" if is_hebrew else "MVS Freight ($):", value=4200.0, step=200.0, key="freight_mvs")
        unit_freight_trans = st.number_input("הובלת שנאי ($):" if is_hebrew else "Transformer Freight ($):", value=5500.0, step=200.0, key="freight_trans")
    with oc_col3:
        unit_freight_access = st.number_input("הובלת ציוד נלווה ($):" if is_hebrew else "Accessory Freight ($):", value=3200.0, step=200.0, key="freight_access")
        unit_freight_solar = st.number_input("הובלת סולארי ($):" if is_hebrew else "Solar PV Freight ($):", value=3360.0, step=200.0, key="freight_solar")

    st.markdown("---")
    st.markdown("##### 2. היטל דלק ימי (BAF) מחושב לפי נפח TEU:" if is_hebrew else "##### 2. Bunker Adjustment Factor (BAF) per TEU:")
    baf_mult = carrier_data["dthc_mult"]
    base_baf_per_teu = st.number_input("תעריף BAF בסיסי ל־TEU יחיד ($):" if is_hebrew else "Base BAF Rate per TEU ($):", value=420.0 * baf_mult, step=20.0, key="baf_per_teu")

    teu_bess, teu_oog, teu_mvs, teu_trans, teu_access, teu_solar = 2.0, 2.0, 1.0, 1.0, 1.0, 1.0

    baf_bess = 0.0 if baf_included else (base_baf_per_teu * teu_bess)
    baf_oog = 0.0 if baf_included else (base_baf_per_teu * teu_oog)
    baf_mvs = 0.0 if baf_included else (base_baf_per_teu * teu_mvs)
    baf_trans = 0.0 if baf_included else (base_baf_per_teu * teu_trans)
    baf_access = 0.0 if baf_included else (base_baf_per_teu * teu_access)
    baf_solar = 0.0 if baf_included else (base_baf_per_teu * teu_solar)

    st.markdown("---")
    st.markdown("##### 3. דמי טיפול בנמל יעד (Destination THC):" if is_hebrew else "##### 3. Destination Terminal Handling Charges (Destination THC):")
    dthc_mult = carrier_data["dthc_mult"]
    
    dh_col1, dh_col2, dh_col3 = st.columns(3)
    with dh_col1:
        dthc_bess = st.number_input("DTHC מכולת BESS ($):" if is_hebrew else "BESS Destination THC ($):", value=650.0 * dthc_mult, step=50.0, key="dthc_bess")
        dthc_oog = st.number_input("DTHC מכולת OOG ($):" if is_hebrew else "OOG Destination THC ($):", value=850.0 * dthc_mult, step=50.0, key="dthc_oog")
    with dh_col2:
        dthc_mvs = st.number_input("DTHC תחנת MVS ($):" if is_hebrew else "MVS Destination THC ($):", value=420.0 * dthc_mult, step=30.0, key="dthc_mvs")
        dthc_trans = st.number_input("DTHC שנאי ($):" if is_hebrew else "Transformer Destination THC ($):", value=480.0 * dthc_mult, step=30.0, key="dthc_trans")
    with dh_col3:
        dthc_access = st.number_input("DTHC ציוד נלווה ($):" if is_hebrew else "Accessory Destination THC ($):", value=280.0 * dthc_mult, step=20.0, key="dthc_access")
        dthc_solar = st.number_input("DTHC פאנלים ($):" if is_hebrew else "Solar PV Destination THC ($):", value=300.0 * dthc_mult, step=20.0, key="dthc_solar")

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
    
    customs_duty_pct = 0.0 if dest_country == "ישראל" else 2.7
    insurance_pct = DEFAULT_INSURANCE_RATES.get(dest_country, 0.15)

with tab3:
    st.subheader("🚚 הובלה יבשתית מנמל הפריקה לאתר הפרויקט (Port to Site)" if is_hebrew else "🚚 Port-to-Site Inland Drayage & Logistics")
    
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        drayage_bess = st.number_input("הובלת משאיות BESS ליחידה ($):" if is_hebrew else "BESS Trucking per unit ($):", value=3200.0, step=200.0, key="dray_bess")
        drayage_oog = st.number_input("הובלת משאיות OOG ליחידה ($):" if is_hebrew else "OOG Trucking per unit ($):", value=3800.0, step=200.0, key="dray_oog")
    with dr_col2:
        drayage_mvs = st.number_input("הובלת משאיות MVS ליחידה ($):" if is_hebrew else "MVS Trucking per unit ($):", value=1400.0, step=100.0, key="dray_mvs")
        drayage_trans = st.number_input("הובלת משאיות שנאי ליחידה ($):" if is_hebrew else "Transformer Trucking per unit ($):", value=1800.0, step=100.0, key="dray_trans")
    with dr_col3:
        drayage_access = st.number_input("הובלת ציוד נלווה ליחידה ($):" if is_hebrew else "Accessory Trucking per unit ($):", value=850.0, step=100.0, key="dray_access")
        drayage_solar = st.number_input("הובלת ציוד סולארי ליחידה ($):" if is_hebrew else "Solar PV Trucking per unit ($):", value=950.0, step=100.0, key="dray_solar")

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
    st.subheader("⚖️ רגולציה ואישורים מנדטוריים" if is_hebrew else "⚖️ Regulation & Mandatory Approvals")

    if dest_country == "ישראל":
        st.markdown("### 🇮🇱 רגולציית חומ\"ס ואישורי הובלה שוטפים (ישראל)")
        st.error("🚨 **חובה חוקית בישראל:** אישור הובלה פרטני מאגף הפיקוח והרכב במשרד התחבורה לכל מכולת BESS.")
        mot_fee_per_bess = st.number_input("עלות אגרת אישור הובלה ממשרד התחבורה ליחידת BESS ($):", value=350.0, step=50.0, key="mot_fee_input")
        mot_total_approval_cost = mot_fee_per_bess * float(bess_count + oog_count)

        st.warning("⚠️ **דרישה נמלית:** אגרות בדיקה, פיקוח חומ\"ס ואישורי כבאות בנמלי הים.")
        local_regulatory_permits = st.number_input("עלות כוללת להיתרי חומ\"ס נמלים ($):", value=1500.0, step=100.0, key="reg_cost_input")
        
        epr_recycling_total_usd = 0.0
        battery_passport_total_usd = 0.0
        decommissioning_total_usd = 0.0
        include_mot_approval = True
        include_regulatory = True

    else:
        st.markdown(f"### 🇪🇺 רגולציה שוטפת ואחריות יצרן (איחוד אירופי — {dest_country})" if is_hebrew else f"### 🇪🇺 European Regulatory Compliance & EPR ({dest_country})")
        st.error("🚨 **חובה באירופה:** דרכון סוללות דיגיטלי (EU Battery Passport) ותיעוד שרשרת אספקה." if is_hebrew else "🚨 **Mandatory in EU:** Digital EU Battery Passport & Supply Chain Documentation.")
        battery_passport_flat = st.number_input("עלות כוללת לדרכון סוללות ותיעוד ($):" if is_hebrew else "Total Battery Passport & Documentation Cost ($):", value=1200.0, step=100.0, key="bp_cost_input")
        battery_passport_total_usd = battery_passport_flat

        st.warning("⚠️ **חובה באירופה:** דמי טיפול באחריות יצרן מורחבת (EPR / Recycling שוטף)." if is_hebrew else "⚠️ **Mandatory in EU:** Extended Producer Responsibility (EPR / Recycling).")
        epr_fee_per_unit = st.number_input("עלות EPR שוטף ליחידת BESS ($):" if is_hebrew else "Ongoing EPR Fee per BESS unit ($):", value=450.0, step=50.0, key="epr_unit_input")
        epr_recycling_total_usd = epr_fee_per_unit * float(bess_count + oog_count)

        include_regulatory = st.checkbox("הכלל אגרות היתרי כניסה והיערכות אתר מקומיים באירופה" if is_hebrew else "Include local European site entry permits & clearance fees", value=True, key="reg_permits_toggle")
        local_regulatory_permits = st.number_input("עלות היתרים מקומיים ($):" if is_hebrew else "Local Permits Cost ($):", value=600.0, step=100.0, key="reg_cost_input") if include_regulatory else 0.0

        mot_total_approval_cost = 0.0
        include_mot_approval = False

        st.markdown("---")
        st.markdown("### 🔄 תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)" if is_hebrew else "### 🔄 Decommissioning & End-of-Life Financial Provision")
        with st.expander("📌 ניהול והפרשה לעתיד (אופציונלי למנהל הפרויקט באירופה)" if is_hebrew else "📌 Management & Future Provision (Optional)", expanded=False):
            st.markdown("""
            כלי ניהול המאפשר להוסיף הפרשה תקציבית צופה פני עתיד עבור:
            * פירוק פיזי של מודולי הסוללות והמכולה.
            * נטרול מתח ובדיקות בטיחות מקדימות.
            * הפרדת תאי אנרגיה וחומרים מסוכנים לפני מחזור סופי.
            """ if is_hebrew else """
            Management tool allowing future budgetary provisions for:
            * Physical dismantling of battery modules and containers.
            * Voltage neutralization and preliminary safety tests.
            * Separation of energy cells and hazardous materials prior to final recycling.
            """)
            include_decommissioning_provision = st.checkbox("הוסף תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)" if is_hebrew else "Add Decommissioning & End-of-Life Financial Provision", value=False, key="decom_toggle")
            
            if include_decommissioning_provision:
                decom_cost_per_bess = st.number_input("עלות מוערכת לפירוק ומחזור ליחידת BESS ($):" if is_hebrew else "Estimated Decommissioning Cost per BESS ($):", value=2200.0, step=200.0, key="decom_unit_input")
                decommissioning_total_usd = decom_cost_per_bess * float(bess_count + oog_count)
                st.info(f"💡 סה\"כ הפרשה מתוכננת למחזור סוף חיים עבור {int(bess_count + oog_count)} יחידות BESS/OOG: **${decommissioning_total_usd:,.2f}**" if is_hebrew else f"💡 Total planned decommissioning provision for {int(bess_count + oog_count)} BESS/OOG units: **${decommissioning_total_usd:,.2f}**")
            else:
                decommissioning_total_usd = 0.0

    st.markdown("---")
    requires_heavy_lift = st.checkbox("נדרש סקר מטענים כבדים / מנוף עוגן (Heavy-Lift Survey)" if is_hebrew else "Heavy-Lift Survey / Anchor Crane Required", value=is_bess, key="hl_survey_toggle")
    heavy_lift_survey_cost = st.number_input("עלות סקר מטענים כבדים ($):" if is_hebrew else "Heavy-Lift Survey Cost ($):", value=2500.0, step=250.0, key="hl_cost_input") if requires_heavy_lift else 0.0

if is_european_dest and tab5_eu is not None:
    with tab5_eu:
        st.subheader("🗺️ הנחות מסלולים אינדיקטיביות באירופה" if is_hebrew else "🗺️ Indicative European Route Options")
        st.info("ניתוח חלופות נמלי פריקה והובלה יבשתית לאתר הפרויקט." if is_hebrew else "Analysis of discharge port alternatives and inland routing to project site.")

if is_european_dest and tab_projects is not None:
    with tab_projects:
        st.subheader("📂 פרויקטי Enlight 2027-2028 (ניהול ובקרה — שירה)" if is_hebrew else "📂 Enlight Projects 2027-2028 (Shira Control)")
        st.info("טבלת מעקב פרויקטי אגירה ואנרגיה מתחדשת של קבוצת אנלייט באירופה עם כל עמודות הבקרה המלאות." if is_hebrew else "Enlight renewable energy and storage tracking table in Europe with full control columns.")

        shira_full_table_data = [
            {"Name": "no number", "CONT": 9, "Site": "Genzano", "Country site": "Italy, Europe", "zip code": "", "Supplier": "JINKO", "Product Category": "PV Modules", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 32, "Site": "Mosciska", "Country site": "Poland, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 480, "Site": "Jupiter", "Country site": "GERMANY, Europe", "zip code": "", "Supplier": "-", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 44, "Site": "Picasso", "Country site": "Sweden, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""},
            {"Name": "no number", "CONT": 15, "Site": "Nardo", "Country site": "Italy, Europe", "zip code": "", "Supplier": "SUNGRO", "Product Category": "BESS GEN2", "TAX other destination": "", "Sea transport": "", "Recycling": "", "Land transport": "", "Custom agent": "", "Insurance": "", "VAT": "", "SPV": "", "over 50 container": "", "Direct or transshipment": ""}
        ]

        df_shira_full = pd.DataFrame(shira_full_table_data)
        st.dataframe(df_shira_full, use_container_width=True)
        st.success("✅ כל עמודות הבקרה המקוריות של שירה נטענו בהצלחה!" if is_hebrew else "✅ All original Shira control columns successfully loaded!")

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
    "EXW (איסוף עצמי ממפעל הספק)": trended_exw,
    "FOB (מסירה על הסיפון בנמל מוצא)": trended_exw + china_inland_drayage + china_origin_thc,
    "CIF (עלות, ביטוח והובלה ימית)": trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd,
    "DAP (מסירה באתר ללא פריקה ומכס)": ddp_supplier_scope_ex_vat,
    "DDP (אחריות מלאה כולל מיסים)": ddp_supplier_scope_incl_vat
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
    st.subheader(f"{txt['summary_title']} — {incoterm} ({display_currency})")
    
    m1_title = "עלות נחיתה (לפני מע\"מ)" if is_hebrew else "Total Landed Cost (Excl. VAT)"
    m2_title = "עלות כלכלית כוללת" if is_hebrew else "Total Economic Cost"
    m3_title = "דרישת מזומנים כוללת" if is_hebrew else "Total Cash Requirement"
    m4_title = "תשלום ישיר לספק" if is_hebrew else "Direct Supplier Payment"

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
    st.subheader(txt["breakdown_title"])

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

    item_exw = "ערך ציוד במפעל (Equipment EXW)" if is_hebrew else "Equipment EXW Value"
    item_china = "הובלה יבשתית ונמלית במוצא" if is_hebrew else "China Inland & Origin THC"
    item_ocean = "הובלה ימית בסיסית" if is_hebrew else "Ocean Freight (Base)"
    item_baf = "היטל דלק ימי לפי TEU (BAF)" if is_hebrew else "Bunker Adjustment Factor (BAF)"
    item_dthc = "דמי טיפול בנמל יעד (Destination THC)" if is_hebrew else "Destination THC"
    item_insur = "ביטוח ימי" if is_hebrew else "Marine Insurance"
    item_customs = f"מכס יבוא ({customs_duty_pct}%)" if is_hebrew else f"Import Customs Duty ({customs_duty_pct}%)"
    item_drayage = "הובלה יבשתית מנמל לאתר" if is_hebrew else "Inland Drayage (Port to Site)"
    item_reg = "רגולציה מקומית ואישורי חומ\"ס / משרד התחבורה" if is_hebrew else "Regulatory & Local Permits"
    item_crane = "עגורן מנוף ופריקה באתר" if is_hebrew else "Site Crane & Unloading"
    item_decom = "הפרשת מחזור סוף חיים (Decommissioning)" if is_hebrew else "Decommissioning Provision"
    item_cont = "בלת״ם פרויקטי (5%)" if is_hebrew else "Contingency (5%)"
    item_tot = "סה\"כ עלות נחיתה לפני מע\"מ (Total Landed Cost)" if is_hebrew else "Total Landed Cost (Excl. VAT)"

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
            <tr>
                <td>{item_exw}</td>
                <td class="center">{int(total_containers_project)} {'יחידות' if is_hebrew else 'units'}</td>
                <td class="left">{curr_symbol} {unit_exw:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_exw:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_china}</td>
                <td class="center">{int(total_containers_project)} {'יחידות' if is_hebrew else 'units'}</td>
                <td class="left">{curr_symbol} {unit_ch_inland:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ch_inland:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_ocean}</td>
                <td class="center">{int(total_containers_project)} {'מכולות' if is_hebrew else 'containers'}</td>
                <td class="left">{curr_symbol} {unit_ocean:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ocean:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_baf}</td>
                <td class="center">{int(total_containers_project)} {'יחידות' if is_hebrew else 'units'}</td>
                <td class="left">{curr_symbol} {unit_baf:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_baf:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_dthc}</td>
                <td class="center">{int(total_containers_project)} {'יחידות' if is_hebrew else 'units'}</td>
                <td class="left">{curr_symbol} {unit_dthc:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_dthc:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_insur}</td>
                <td class="center">{'אחוז מערך CIF' if is_hebrew else '% of CIF'}</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_insur:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_customs}</td>
                <td class="center">{'על פי סיווג' if is_hebrew else 'Classification'}</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_customs:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_drayage}</td>
                <td class="center">{int(total_containers_project)} {'משאיות' if is_hebrew else 'trucks'}</td>
                <td class="left">{curr_symbol} {unit_drayage:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_drayage:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_reg}</td>
                <td class="center">{'הוצאה כוללת' if is_hebrew else 'Total Expense'}</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_reg:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_crane}</td>
                <td class="center">{'הוצאה כוללת' if is_hebrew else 'Total Expense'}</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_crane:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_decom}</td>
                <td class="center">{int(bess_count + oog_count)} BESS</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_decom:,.2f}</b></td>
            </tr>
            <tr>
                <td>{item_cont}</td>
                <td class="center">5% Supply Chain</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_cont:,.2f}</b></td>
            </tr>
            <tr class="total-row">
                <td>{item_tot}</td>
                <td class="center">-</td>
                <td class="left">-</td>
                <td class="left" style="font-size: 1.05rem; color: #1e3d59;"><b>{curr_symbol} {ex_total:,.2f}</b></td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 ייצוא נתונים לדוח אקסל (Excel Export)" if is_hebrew else "📥 Excel Export")
    
    excel_summary_data = [
        [
            "רכיב עלות בפרויקט" if is_hebrew else "Project Cost Item",
            "כמות / בסיס חישוב" if is_hebrew else "Basis / Qty",
            f"עלות ליחידה ({curr_symbol})" if is_hebrew else f"Unit Cost ({curr_symbol})",
            f"סה\"כ סעיף ({curr_symbol})" if is_hebrew else f"Total Amount ({curr_symbol})"
        ],
        [item_exw, f"{int(total_containers_project)} units", trended_exw / max(1, total_containers_project), trended_exw],
        [item_china, f"{int(total_containers_project)} units", (china_inland_drayage + china_origin_thc) / max(1, total_containers_project), china_inland_drayage + china_origin_thc],
        [item_ocean, f"{int(total_containers_project)} containers", total_base_ocean_freight / max(1, total_containers_project), total_base_ocean_freight * trend_multiplier],
        [item_baf, f"{int(total_containers_project)} units", total_baf_ocean / max(1, total_containers_project), total_baf_ocean * trend_multiplier],
        [item_dthc, f"{int(total_containers_project)} units", total_destination_thc / max(1, total_containers_project), destination_thc_total],
        [item_insur, "% of CIF", 0, insurance_total_usd],
        [item_customs, f"({customs_duty_pct}%)", 0, customs_duty_usd],
        [item_drayage, f"{int(total_containers_project)} trucks", inland_drayage_total_base / max(1, total_containers_project), inland_drayage_total_usd],
        [item_reg, "Total", 0, active_regulatory_permits],
        [item_crane, "Total", 0, active_site_crane],
        [item_decom, f"{int(bess_count + oog_count)} BESS", 0, decommissioning_total_usd],
        [item_cont, "5%", 0, contingency_usd],
        [item_tot, "-", 0, total_landed_cost_ex_vat]
    ]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = pd.DataFrame(excel_summary_data[1:], columns=excel_summary_data[0])
        df_export.to_excel(writer, sheet_name='Cost Summary', index=False)
        
        ws = writer.sheets['Cost Summary']
        ws.views.sheetView[0].rightToLeft = is_hebrew

    excel_data = output.getvalue()

    st.download_button(
        label=txt["excel_btn"],
        data=excel_data,
        file_name=f"TerraVol_Project_Report_{dest_country}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
