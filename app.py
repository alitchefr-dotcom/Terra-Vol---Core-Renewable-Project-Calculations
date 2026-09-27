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

# עיצוב גלובלי וכרטיסי מדדים מותאמים אישית (סימן מטבע משמאל למספר)
st.markdown(
    """
    <style>
    .stApp { direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, h4, h5, h6, p, label, div, span { direction: rtl; text-align: right; }
    .stTextInput label, .stSelectbox label, .stNumberInput label { direction: rtl; text-align: right; width: 100%; font-weight: 600; }
    
    /* עיצוב כרטיסי מדדים פיננסיים מקצועיים */
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.5rem;
        color: #1e3d59;
        font-weight: 700;
        direction: ltr;
        text-align: right;
    }
    
    /* עיצוב טבלה פיננסית מותאמת אישית */
    .custom-finance-table {
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
    }
    .custom-finance-table th {
        background-color: #f1f5f9;
        color: #1e3d59;
        font-weight: 700;
        padding: 12px 16px;
        text-align: right;
        border-bottom: 2px solid #e2e8f0;
    }
    .custom-finance-table th.center, .custom-finance-table td.center {
        text-align: center;
    }
    .custom-finance-table th.left, .custom-finance-table td.left {
        text-align: left;
        direction: ltr;
    }
    .custom-finance-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #e2e8f0;
        text-align: right;
    }
    .custom-finance-table tr.total-row {
        background-color: #f8fafc;
        font-weight: 700;
        border-top: 2px solid #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

T = {
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
}

logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" style="width: 140px; height: auto;" />' if logo_base64 else '⚡'

header_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; width: 100%; direction: rtl; margin-bottom: 0rem;">
    <h1 style="margin: 0; font-size: 3rem; font-weight: 700; color: #1e3d59;">Terra Vol</h1>
    <div>{logo_img_tag}</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.caption(T["caption"])

ORIGIN_PORTS = ["שאנגחאי (Shanghai)", "נינגבו (Ningbo)", "שנג'ן (Shenzhen)", "צ'ינגדאו (Qingdao)"]
DESTINATION_PORTS = {
    "ישראל": ["נמל חיפה", "נמל אשדוד"],
    "רומניה": ["קונסטנצה, רומניה (Constanța)", "בורגס, בולגריה (Burgas)"],
    "פולין": ["גדנסק, פולין (Gdansk)", "גדיניה, פולין (Gdynia)"],
    "גרמניה": ["המבורג, גרמניה (Hamburg)", "ברמרהאפן, גרמניה (Bremerhaven)"],
    "אחר / מותאם": ["רוטרדם, הולנד (Rotterdam)"]
}
VAT_RATES = {"ישראל": 18.0, "רומניה": 19.0, "פולין": 23.0, "גרמניה": 19.0, "אחר / מותאם": 0.0}
DEFAULT_INSURANCE_RATES = {"ישראל": 0.08, "רומניה": 0.15, "פולין": 0.15, "גרמניה": 0.15, "אחר / מותאם": 0.15}
DEFAULT_FREE_DAYS = {"ישראל": 4, "רומניה": 7, "פולין": 7, "גרמניה": 7, "אחר / מותאם": 7}

CARRIER_FUEL_SURCHARGES = {
    "ZIM (שירות מועדף למטעני חומ\"ס וגמישות)": {"bess_multiplier": 1.0, "dthc_mult": 1.0},
    "MSC (תעריפים מועדפים)": {"bess_multiplier": 0.82, "dthc_mult": 0.90},
    "Hapag-Lloyd (סטנדרטי)": {"bess_multiplier": 0.95, "dthc_mult": 0.95},
    "שוק חופשי / ספוט": {"bess_multiplier": 0.90, "dthc_mult": 0.90}
}

incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (אחריות מלאה כולל מיסים)", "DAP (מסירה באתר ללא פריקה ומכס)", "CIF (עלות, ביטוח והובלה ימית)", "FOB (מסירה על הסיפון בנמל מוצא)", "EXW (איסוף עצמי ממפעל הספק)"], key="sidebar_incoterm")
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"], key="sidebar_currency")

forecast_date = st.sidebar.date_input("תאריך יעד לאספקה באתר:", value=date(2027, 6, 30), key="sidebar_forecast_date")
market_scenario = st.sidebar.selectbox("תחזית אינפלציה ומגמת שוק:", ["שמרני (+8.0% לשנה)", "בסיסי (+4.5% לשנה)", "יציב / ללא שינוי (0.0%)"], key="sidebar_market_scenario")

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

usd_to_eur = st.sidebar.number_input("שער המרה USD ל־EUR:", value=float(live_eur), step=0.01, min_value=0.0001, key="sidebar_usd_eur")
usd_to_ils = st.sidebar.number_input("שער המרה USD ל־ILS:", value=float(live_ils), step=0.01, min_value=0.0001, key="sidebar_usd_ils")

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

curr_symbol = "$" if "USD" in display_currency else ("€" if "EUR" in display_currency else "₪")

dest_country = st.sidebar.selectbox(T["dest_country"], list(VAT_RATES.keys()), index=0, key="sidebar_dest_country")
default_site_placeholder = "אשלים / עמק הירדן (אנלייט)" if dest_country == "ישראל" else "Iepurești / Project Site"
is_european_dest = (dest_country != "ישראל")

# הגדרת הטאבים באופן דינמי: טאב פרויקטי אירופה יוצג אך ורק כאשר נבחרת מדינה אירופאית
if is_european_dest:
    tab1, tab2, tab3, tab4, tab5_eu, tab_projects, tab_summary = st.tabs([
        T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_projects"], T["tab_summary"]
    ])
else:
    tab1, tab2, tab3, tab4, tab_summary = st.tabs([
        T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_summary"]
    ])
    tab5_eu = None
    tab_projects = None

with tab1:
    st.subheader("הגדרת רכיבי הציוד וכמויות לפרויקט")
    st.info("הזן את כמויות מכולות הסוללה, הממירים, השנאים ועלויות הייצור במפעל (EXW).")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        origin_port = st.selectbox(T["origin_port"], ORIGIN_PORTS, key="tab1_origin_port")
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["אחר / מותאם"])
        dest_port = st.selectbox(T["dest_port"], available_dest_ports, key=f"tab1_dest_port_{dest_country}")
        site_address = st.text_input("שם אתר הפרויקט:", key="site_name_input", placeholder=default_site_placeholder)

    with col_meta2:
        applied_vat = st.number_input(f"שיעור מע\"מ ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country}")
        vat_recovery_pct = st.number_input("אחוז החזר מע\"מ (%)", value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        vat_paid_by_supplier = st.checkbox("המע\"מ משולם על ידי הספק במסגרת תנאי המסחר", value=False, key="tab1_vat_supplier")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("#### מכולות סוללה (BESS)")
        bess_count = st.number_input("כמות מכולות BESS (40' HC DG):", min_value=0, value=20, step=1, key="proj_bess_count")
        bess_exw = st.number_input("עלות EXW ליחידת BESS ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_bess_exw")

        oog_count = st.number_input("כמות מכולות חריגות (OOG):", min_value=0, value=0, step=1, key="proj_oog_count")
        oog_exw = st.number_input("עלות EXW ליחידת OOG ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_oog_exw")

    with col_q2:
        st.markdown("#### תחנות המרה ושנאים")
        mvs_count = st.number_input("כמות תחנות מתח גבוה (MVS):", min_value=0, value=4, step=1, key="proj_mvs_count")
        mvs_exw = st.number_input("עלות EXW ליחידת MVS ($):", min_value=0.0, value=250000.0, step=10000.0, key="proj_mvs_exw")

        transformer_count = st.number_input("כמות שנאים ראשיים:", min_value=0, value=2, step=1, key="proj_trans_count")
        transformer_exw = st.number_input("עלות EXW ליחידת שנאי ($):", min_value=0.0, value=120000.0, step=10000.0, key="proj_trans_exw")

    with col_q3:
        st.markdown("#### ציוד נלווה וסולארי")
        access_count = st.number_input("מכולות ציוד נלווה / יבש:", min_value=0, value=2, step=1, key="proj_access_count")
        access_exw = st.number_input("עלות EXW ליחידת ציוד נלווה ($):", min_value=0.0, value=50000.0, step=5000.0, key="proj_access_exw")

        solar_count = st.number_input("יחידות פאנלים סולאריים (PV):", min_value=0, value=0, step=1, key="proj_solar_count")
        solar_exw = st.number_input("עלות EXW ליחידה סולארית ($):", min_value=0.0, value=300000.0, step=10000.0, key="proj_solar_exw")

    total_containers_project = max(1, bess_count + oog_count + mvs_count + transformer_count + access_count + solar_count)
    total_exw_project = (
        (bess_count * bess_exw) + (oog_count * oog_exw) + 
        (mvs_count * mvs_exw) + (transformer_count * transformer_exw) + 
        (access_count * access_exw) + (solar_count * solar_exw)
    )
    is_bess = (bess_count > 0 or oog_count > 0)
    is_dg = is_bess

    st.success(f"📊 סה\"כ יחידות לפרויקט: {total_containers_project} | סה\"כ ערך ציוד במפעל (EXW): **${total_exw_project:,.2f}**")

with tab2:
    st.subheader("🚢 תעריפי הובלה ימית, היטל דלק (BAF) ודמי טיפול בנמל יעד (DTHC)")
    
    selected_carrier = st.selectbox("בחירת חברת ספנות:", list(CARRIER_FUEL_SURCHARGES.keys()), key="tab2_carrier")
    carrier_data = CARRIER_FUEL_SURCHARGES[selected_carrier]

    baf_included = st.checkbox("תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית", value=False, key="tab2_baf_incl")

    st.markdown("##### 1. עלות הובלה ימית ליחידה:")
    oc_col1, oc_col2, oc_col3 = st.columns(3)
    with oc_col1:
        unit_freight_bess = st.number_input("הובלת BESS ($):", value=31850.0 * carrier_data["bess_multiplier"], step=500.0, key="freight_bess")
        unit_freight_oog = st.number_input("הובלת OOG ($):", value=29900.0, step=500.0, key="freight_oog")
    with oc_col2:
        unit_freight_mvs = st.number_input("הובלת MVS ($):", value=4200.0, step=200.0, key="freight_mvs")
        unit_freight_trans = st.number_input("הובלת שנאי ($):", value=5500.0, step=200.0, key="freight_trans")
    with oc_col3:
        unit_freight_access = st.number_input("הובלת ציוד נלווה ($):", value=3200.0, step=200.0, key="freight_access")
        unit_freight_solar = st.number_input("הובלת סולארי ($):", value=3360.0, step=200.0, key="freight_solar")

    st.markdown("---")
    st.markdown("##### 2. היטל דלק ימי (BAF) מחושב לפי נפח TEU:")
    baf_mult = carrier_data["dthc_mult"]
    base_baf_per_teu = st.number_input("תעריף BAF בסיסי ל־TEU יחיד ($):", value=420.0 * baf_mult, step=20.0, key="baf_per_teu")

    teu_bess, teu_oog, teu_mvs, teu_trans, teu_access, teu_solar = 2.0, 2.0, 1.0, 1.0, 1.0, 1.0

    baf_bess = 0.0 if baf_included else (base_baf_per_teu * teu_bess)
    baf_oog = 0.0 if baf_included else (base_baf_per_teu * teu_oog)
    baf_mvs = 0.0 if baf_included else (base_baf_per_teu * teu_mvs)
    baf_trans = 0.0 if baf_included else (base_baf_per_teu * teu_trans)
    baf_access = 0.0 if baf_included else (base_baf_per_teu * teu_access)
    baf_solar = 0.0 if baf_included else (base_baf_per_teu * teu_solar)

    st.markdown("---")
    st.markdown("##### 3. דמי טיפול בנמל יעד (Destination THC):")
    dthc_mult = carrier_data["dthc_mult"]
    
    dh_col1, dh_col2, dh_col3 = st.columns(3)
    with dh_col1:
        dthc_bess = st.number_input("DTHC מכולת BESS ($):", value=650.0 * dthc_mult, step=50.0, key="dthc_bess")
        dthc_oog = st.number_input("DTHC מכולת OOG ($):", value=850.0 * dthc_mult, step=50.0, key="dthc_oog")
    with dh_col2:
        dthc_mvs = st.number_input("DTHC תחנת MVS ($):", value=420.0 * dthc_mult, step=30.0, key="dthc_mvs")
        dthc_trans = st.number_input("DTHC שנאי ($):", value=480.0 * dthc_mult, step=30.0, key="dthc_trans")
    with dh_col3:
        dthc_access = st.number_input("DTHC ציוד נלווה ($):", value=280.0 * dthc_mult, step=20.0, key="dthc_access")
        dthc_solar = st.number_input("DTHC פאנלים ($):", value=300.0 * dthc_mult, step=20.0, key="dthc_solar")

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
    customs_duty_pct = 2.7 if is_bess else 0.0
    insurance_pct = DEFAULT_INSURANCE_RATES.get(dest_country, 0.15)

with tab3:
    st.subheader("🚚 הובלה יבשתית מנמל הפריקה לאתר הפרויקט (Port to Site)")
    
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        drayage_bess = st.number_input("הובלת משאיות BESS ליחידה ($):", value=3200.0, step=200.0, key="dray_bess")
        drayage_oog = st.number_input("הובלת משאיות OOG ליחידה ($):", value=3800.0, step=200.0, key="dray_oog")
    with dr_col2:
        drayage_mvs = st.number_input("הובלת משאיות MVS ליחידה ($):", value=1400.0, step=100.0, key="dray_mvs")
        drayage_trans = st.number_input("הובלת משאיות שנאי ליחידה ($):", value=1800.0, step=100.0, key="dray_trans")
    with dr_col3:
        drayage_access = st.number_input("הובלת ציוד נלווה ליחידה ($):", value=850.0, step=100.0, key="dray_access")
        drayage_solar = st.number_input("הובלת ציוד סולארי ליחידה ($):", value=950.0, step=100.0, key="dray_solar")

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
    st.subheader("⚖️ רגולציה ואישורים מנדטוריים")

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
        st.markdown(f"### 🇪🇺 רגולציה שוטפת ואחריות יצרן (איחוד אירופי — {dest_country})")
        st.error("🚨 **חובה באירופה:** דרכון סוללות דיגיטלי (EU Battery Passport) ותיעוד שרשרת אספקה.")
        battery_passport_flat = st.number_input("עלות כוללת לדרכון סוללות ותיעוד ($):", value=1200.0, step=100.0, key="bp_cost_input")
        battery_passport_total_usd = battery_passport_flat

        st.warning("⚠️ **חובה באירופה:** דמי טיפול באחריות יצרן מורחבת (EPR / Recycling שוטף).")
        epr_fee_per_unit = st.number_input("עלות EPR שוטף ליחידת BESS ($):", value=450.0, step=50.0, key="epr_unit_input")
        epr_recycling_total_usd = epr_fee_per_unit * float(bess_count + oog_count)

        include_regulatory = st.checkbox("הכלל אגרות היתרי כניסה והיערכות אתר מקומיים באירופה", value=True, key="reg_permits_toggle")
        local_regulatory_permits = st.number_input("עלות היתרים מקומיים ($):", value=600.0, step=100.0, key="reg_cost_input") if include_regulatory else 0.0

        mot_total_approval_cost = 0.0
        include_mot_approval = False

        st.markdown("---")
        st.markdown("### 🔄 תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)")
        with st.expander("📌 ניהול והפרשה לעתיד (אופציונלי למנהל הפרויקט באירופה)", expanded=False):
            st.markdown("""
            כלי ניהול המאפשר להוסיף הפרשה תקציבית צופה פני עתיד עבור:
            * פירוק פיזי של מודולי הסוללות והמכולה.
            * נטרול מתח ובדיקות בטיחות מקדימות.
            * הפרדת תאי אנרגיה וחומרים מסוכנים לפני מחזור סופי.
            """)
            include_decommissioning_provision = st.checkbox("הוסף תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)", value=False, key="decom_toggle")
            
            if include_decommissioning_provision:
                decom_cost_per_bess = st.number_input("עלות מוערכת לפירוק ומחזור ליחידת BESS ($):", value=2200.0, step=200.0, key="decom_unit_input")
                decommissioning_total_usd = decom_cost_per_bess * float(bess_count + oog_count)
                st.info(f"💡 סה\"כ הפרשה מתוכננת למחזור סוף חיים עבור {int(bess_count + oog_count)} יחידות BESS/OOG: **${decommissioning_total_usd:,.2f}**")
            else:
                decommissioning_total_usd = 0.0

    st.markdown("---")
    requires_heavy_lift = st.checkbox("נדרש סקר מטענים כבדים / מנוף עוגן (Heavy-Lift Survey)", value=is_bess, key="hl_survey_toggle")
    heavy_lift_survey_cost = st.number_input("עלות סקר מטענים כבדים ($):", value=2500.0, step=250.0, key="hl_cost_input") if requires_heavy_lift else 0.0

# טאב 5 האירופאי מוצג אך ורק אם נבחרה מדינה אירופאית
if is_european_dest and tab5_eu is not None:
    with tab5_eu:
        st.subheader("🗺️ הנחות מסלולים אינדיקטיביות באירופה")
        st.info("ניתוח חלופות נמלי פריקה והובלה יבשתית לאתר הפרויקט.")

# טאב פרויקטי אנלייט מוצג אך ורק אם נבחרה מדינה אירופאית
if is_european_dest and tab_projects is not None:
    with tab_projects:
        st.subheader("📂 פרויקטי Enlight 2027-2028 (ניהול ובקרה — שירה)")
        st.info("בחינת תרחישים לפרויקטי אגירה ואנרגיה מתחדשת של קבוצת אנלייט באירופה בשנים 2027–2028 (על בסיס נתוני האקסל של שירה).")
        
        enlight_project_type = st.selectbox("בחר פרויקט אירופאי של שירה לטעינת נתונים אוטומטית:", [
            "פרויקט Iepurești (רומניה)", 
            "פרויקט Ghimpați (רומניה)", 
            "פרויקט Mosciska / Czerwona Woda (פולין)",
            "פרויקט Genzano (איטליה)"
        ], key="enlight_proj_sel")
        
        if "Iepurești" in enlight_project_type or "Ghimpați" in enlight_project_type:
            st.markdown("📌 **מאפייני פרויקט רומניה (שירה):** פריקה דרך נמל קונסטנצה, הובלה יבשתית לאתר, עמידה בתקן UN3536 ודרכון סוללות אירופאי.")
        elif "Mosciska" in enlight_project_type:
            st.markdown("📌 **מאפייני פרויקט פולין (שירה):** פרויקט BESS GEN2 ו־MVS, דרישות EPR ודרכון סוללות מנדטורי.")
        else:
            st.markdown("📌 **מאפייני פרויקט אירופאי (שירה):** ניהול שרשרת אספקה אזורית, עמידה בדרישות EPR ודרכון סוללות דיגיטלי.")

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
    st.subheader(f"📊 דוח בקרה פיננסית ורגולטורית — {incoterm} ({display_currency})")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">עלות נחיתה (לפני מע"מ)</div>
            <div class="metric-value">{curr_symbol} {display_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">עלות כלכלית כוללת</div>
            <div class="metric-value">{curr_symbol} {econ_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">דרישת מזומנים כוללת</div>
            <div class="metric-value">{curr_symbol} {cash_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">תשלום ישיר לספק</div>
            <div class="metric-value">{curr_symbol} {supplier_val:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 פירוט רכיבי תקציב הפרויקט (Cost Breakdown)")

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

    html_table = f"""
    <table class="custom-finance-table">
        <thead>
            <tr>
                <th style="width: 40%;">רכיב עלות בפרויקט</th>
                <th class="center" style="width: 20%;">כמות / בסיס חישוב</th>
                <th class="left" style="width: 20%;">עלות ליחידה</th>
                <th class="left" style="width: 20%;">סה\"כ סעיף</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>ערך ציוד במפעל (Equipment EXW)</td>
                <td class="center">{int(total_containers_project)} יחידות</td>
                <td class="left">{curr_symbol} {unit_exw:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_exw:,.2f}</b></td>
            </tr>
            <tr>
                <td>הובלה יבשתית ונמלית במוצא</td>
                <td class="center">{int(total_containers_project)} יחידות</td>
                <td class="left">{curr_symbol} {unit_ch_inland:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ch_inland:,.2f}</b></td>
            </tr>
            <tr>
                <td>הובלה ימית בסיסית</td>
                <td class="center">{int(total_containers_project)} מכולות</td>
                <td class="left">{curr_symbol} {unit_ocean:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_ocean:,.2f}</b></td>
            </tr>
            <tr>
                <td>היטל דלק ימי לפי TEU (BAF)</td>
                <td class="center">{int(total_containers_project)} יחידות</td>
                <td class="left">{curr_symbol} {unit_baf:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_baf:,.2f}</b></td>
            </tr>
            <tr>
                <td>דמי טיפול בנמל יעד (Destination THC)</td>
                <td class="center">{int(total_containers_project)} יחידות</td>
                <td class="left">{curr_symbol} {unit_dthc:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_dthc:,.2f}</b></td>
            </tr>
            <tr>
                <td>ביטוח ימי</td>
                <td class="center">אחוז מערך CIF</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_insur:,.2f}</b></td>
            </tr>
            <tr>
                <td>מכס יבוא</td>
                <td class="center">על פי סיווג ({customs_duty_pct}%)</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_customs:,.2f}</b></td>
            </tr>
            <tr>
                <td>הובלה יבשתית מנמל לאתר</td>
                <td class="center">{int(total_containers_project)} משאיות</td>
                <td class="left">{curr_symbol} {unit_drayage:,.2f}</td>
                <td class="left"><b>{curr_symbol} {ex_drayage:,.2f}</b></td>
            </tr>
            <tr>
                <td>רגולציה מקומית ואישורי חומ\"ס / משרד התחבורה</td>
                <td class="center">הוצאה כוללת</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_reg:,.2f}</b></td>
            </tr>
            <tr>
                <td>עגורן מנוף ופריקה באתר</td>
                <td class="center">הוצאה כוללת</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_crane:,.2f}</b></td>
            </tr>
            <tr>
                <td>הפרשת מחזור סוף חיים (Decommissioning)</td>
                <td class="center">{int(bess_count + oog_count)} יחידות BESS</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_decom:,.2f}</b></td>
            </tr>
            <tr>
                <td>בלת״ם פרויקטי</td>
                <td class="center">5% מסך שרשרת האספקה</td>
                <td class="left">-</td>
                <td class="left"><b>{curr_symbol} {ex_cont:,.2f}</b></td>
            </tr>
            <tr class="total-row">
                <td>סה\"כ עלות נחיתה לפני מע\"מ (Total Landed Cost)</td>
                <td class="center">-</td>
                <td class="left">-</td>
                <td class="left" style="font-size: 1.05rem; color: #1e3d59;"><b>{curr_symbol} {ex_total:,.2f}</b></td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 ייצוא נתונים לדוח אקסל (Excel Export)")
    
    excel_summary_data = [
        [
            "רכיב עלות בפרויקט",
            "כמות / בסיס חישוב",
            f"עלות ליחידה ({curr_symbol})",
            f"סה\"כ סעיף ({curr_symbol})"
        ],
        ["ערך ציוד במפעל (Equipment EXW)", f"{int(total_containers_project)} יחידות", trended_exw / max(1, total_containers_project), trended_exw],
        ["הובלה יבשתית ונמלית במוצא", f"{int(total_containers_project)} יחידות", (china_inland_drayage + china_origin_thc) / max(1, total_containers_project), china_inland_drayage + china_origin_thc],
        ["הובלה ימית בסיסית", f"{int(total_containers_project)} מכולות", total_base_ocean_freight / max(1, total_containers_project), total_base_ocean_freight * trend_multiplier],
        ["היטל דלק ימי לפי TEU (BAF)", f"{int(total_containers_project)} יחידות", total_baf_ocean / max(1, total_containers_project), total_baf_ocean * trend_multiplier],
        ["דמי טיפול בנמל יעד (Destination THC)", f"{int(total_containers_project)} יחידות", total_destination_thc / max(1, total_containers_project), destination_thc_total],
        ["ביטוח ימי", "אחוז מערך CIF", 0, insurance_total_usd],
        ["מכס יבוא", f"על פי סיווג ({customs_duty_pct}%)", 0, customs_duty_usd],
        ["הובלה יבשתית מנמל לאתר", f"{int(total_containers_project)} משאיות", inland_drayage_total_base / max(1, total_containers_project), inland_drayage_total_usd],
        ["רגולציה מקומית ואישורי חומ\"ס / משרד התחבורה", "הוצאה כוללת", 0, active_regulatory_permits],
        ["עגורן מנוף ופריקה באתר", "הוצאה כוללת", 0, active_site_crane],
        ["הפרשת מחזור סוף חיים (Decommissioning)", f"{int(bess_count + oog_count)} יחידות BESS", 0, decommissioning_total_usd],
        ["בלת״ם פרויקטי", "5% מסך שרשרת האספקה", 0, contingency_usd],
        ["סה\"כ עלות נחיתה לפני מע\"מ (Total Landed Cost)", "-", 0, total_landed_cost_ex_vat]
    ]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = pd.DataFrame(excel_summary_data[1:], columns=excel_summary_data[0])
        df_export.to_excel(writer, sheet_name='Cost Summary', index=False)
        
        ws = writer.sheets['Cost Summary']
        ws.views.sheetView[0].rightToLeft = True

    excel_data = output.getvalue()

    st.download_button(
        label="📥 הורד דוח פיננסי מלא לאקסל (Download Excel Report)",
        data=excel_data,
        file_name=f"TerraVol_Project_Report_{dest_country}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
