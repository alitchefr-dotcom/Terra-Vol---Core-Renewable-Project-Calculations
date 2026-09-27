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
lang = st.sidebar.radio("Select Language / בחר שפה:", ["Hebrew (עברית)", "English"], index=0, key="lang_select")
is_hebrew = (lang == "Hebrew (עברית)")

if is_hebrew:
    st.markdown(
        """
        <style>
        .stApp { direction: rtl; text-align: right; }
        h1, h2, h3, h4, h5, h6, p, label, div { direction: rtl; text-align: right; }
        .stTextInput label, .stSelectbox label, .stNumberInput label { direction: rtl; text-align: right; width: 100%; }
        </style>
        """,
        unsafe_allow_html=True
    )

T = {
    "caption": "Professional MVP Project Cargo Calculator incorporating Supply Chain Costs, Incoterms, DG Compliance & Market Forecasting" if not is_hebrew else "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, Incoterms, רגולציה ותחזית שוק",
    "scenario_header": "🗂️ Scenario, Incoterm & Market Forecast" if not is_hebrew else "🗂️ הגדרות תרחיש, תנאי סחר ותחזית שוק",
    "incoterm_label": "Commercial Incoterm (Supplier Scope):" if not is_hebrew else "תנאי סחר מסחרי (אחריות ספק):",
    "currency_label": "Dashboard Main Currency:" if not is_hebrew else "מטבע הצגה ראשי בדשבורד:",
    "tab1": "📋 Multi-Item Project Scope" if not is_hebrew else "📋 תמהיל רכיבי הציוד לפרויקט (Multi-Item)",
    "tab2": "⚓ Supply Chain & Incoterms" if not is_hebrew else "⚓ שרשרת אספקה ותנאי סחר",
    "tab3": "📦 Storage & Site Drayage" if not is_hebrew else "📦 אחסנה, השהיות והובלת אתר",
    "tab4": "⚖️ DG Compliance & Regulation" if not is_hebrew else "⚖️ רגולציית חומ\"ס DG ורגולציית מוצר",
    "tab5_eu": "🗺️ Illustrative Route Assumptions" if not is_hebrew else "🗺️ הנחות מסלולים אינדיקטיביות",
    "tab_projects": "📂 Enlight 2027-2028 Projects" if not is_hebrew else "📂 פרויקטי Enlight 2027-2028 (שירה)",
    "tab_summary": "📊 Financial & Regulatory Summary" if not is_hebrew else "📊 דוח בקרה פיננסית ורגולטורית",
    "origin_port": "Port of Loading:" if not is_hebrew else "נמל מוצא:",
    "dest_port": "Port of Discharge:" if not is_hebrew else "נמל יעד ימי (Port of Discharge):",
    "dest_country": "Final Project Country:" if not is_hebrew else "מדינת יעד סופית (אתר הפרויקט):",
}

logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" style="width: 140px; height: auto;" />' if logo_base64 else '⚡'

header_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; width: 100%; direction: {'rtl' if is_hebrew else 'ltr'}; margin-bottom: 0rem;">
    <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">Terra Vol</h1>
    <div>{logo_img_tag}</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.caption(T["caption"])

ORIGIN_PORTS = ["Shanghai", "Ningbo-Zhoushan", "Shenzhen / Yantian", "Qingdao"]
DESTINATION_PORTS = {
    "Israel": ["Haifa Port", "Ashdod Port"],
    "Romania": ["Constanța, Romania", "Burgas, Bulgaria"],
    "Poland": ["Gdansk, Poland", "Gdynia, Poland"],
    "Germany": ["Hamburg, Germany", "Bremerhaven, Germany"],
    "Other / Custom": ["Rotterdam, Netherlands"]
}
VAT_RATES = {"Israel": 18.0, "Romania": 19.0, "Poland": 23.0, "Germany": 19.0, "Other / Custom": 0.0}
DEFAULT_INSURANCE_RATES = {"Israel": 0.08, "Romania": 0.15, "Poland": 0.15, "Germany": 0.15, "Other / Custom": 0.15}
DEFAULT_FREE_DAYS = {"Israel": 4, "Romania": 7, "Poland": 7, "Germany": 7, "Other / Custom": 7}

CARRIER_FUEL_SURCHARGES = {
    "ZIM (Premium DG & Flexibility)": {"bess_multiplier": 1.0, "dthc_mult": 1.0},
    "MSC (Discounted Rates)": {"bess_multiplier": 0.82, "dthc_mult": 0.90},
    "Hapag-Lloyd (Standard)": {"bess_multiplier": 0.95, "dthc_mult": 0.95},
    "Other / Spot Market": {"bess_multiplier": 0.90, "dthc_mult": 0.90}
}

incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "DAP (Delivered at Place)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)", "EXW (Ex Works)"], key="sidebar_incoterm")
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"], key="sidebar_currency")

forecast_date = st.sidebar.date_input("Target Delivery Date:", value=date(2027, 6, 30), key="sidebar_forecast_date")
market_scenario = st.sidebar.selectbox("Market Scenario:", ["Conservative (+8.0% p.a.)", "Base Market Trend (+4.5% p.a.)", "Optimistic / Stable (0.0%)"], key="sidebar_market_scenario")

today_date = date.today()
delta_days = (forecast_date - today_date).days
years_diff = max(0.0, delta_days / 365.25)
annual_inflation = 0.08 if "Conservative" in market_scenario else (0.045 if "Base" in market_scenario else 0.0)
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

usd_to_eur = st.sidebar.number_input("USD to EUR Rate:", value=float(live_eur), step=0.01, min_value=0.0001, key="sidebar_usd_eur")
usd_to_ils = st.sidebar.number_input("USD to ILS Rate:", value=float(live_ils), step=0.01, min_value=0.0001, key="sidebar_usd_ils")

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

dest_country = st.sidebar.selectbox(T["dest_country"], list(VAT_RATES.keys()), index=0, key="sidebar_dest_country")
default_site_placeholder = "אשלים / עמק הירדן (אנלייט)" if dest_country == "Israel" else "Iepurești / Project Site"
show_route_optimization = (dest_country != "Israel")

if show_route_optimization:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_projects"], T["tab_summary"]])
    tab_summary = tab7
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_projects"], T["tab_summary"]])
    tab_summary = tab6

with tab1:
    st.subheader("הגדרת רכיבי הציוד וכמויות (Project Bill of Materials)" if is_hebrew else "Project Equipment Quantities")
    st.info("כאן מזינים את כמויות ועלויות ה־EXW לכל רכיב בנפרד.")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        origin_port = st.selectbox(T["origin_port"], ORIGIN_PORTS, key="tab1_origin_port")
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["Other / Custom"])
        dest_port = st.selectbox(T["dest_port"], available_dest_ports, key=f"tab1_dest_port_{dest_country}")
        site_address = st.text_input("Project Site Name / שם אתר הפרויקט", key="site_name_input", placeholder=default_site_placeholder)

    with col_meta2:
        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country}")
        vat_recovery_pct = st.number_input("VAT Recoverability (%)", value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        vat_paid_by_supplier = st.checkbox("VAT paid by supplier under commercial arrangement", value=False, key="tab1_vat_supplier")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("#### BESS & OOG Containers")
        bess_count = st.number_input("BESS Count (40' HC DG):", min_value=0, value=20, step=1, key="proj_bess_count")
        bess_exw = st.number_input("BESS Unit EXW ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_bess_exw")

        oog_count = st.number_input("OOG Flat Rack Count:", min_value=0, value=0, step=1, key="proj_oog_count")
        oog_exw = st.number_input("OOG Unit EXW ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_oog_exw")

    with col_q2:
        st.markdown("#### MVS & Transformers")
        mvs_count = st.number_input("MVS Stations Count:", min_value=0, value=4, step=1, key="proj_mvs_count")
        mvs_exw = st.number_input("MVS Unit EXW ($):", min_value=0.0, value=250000.0, step=10000.0, key="proj_mvs_exw")

        transformer_count = st.number_input("Transformers Count:", min_value=0, value=2, step=1, key="proj_trans_count")
        transformer_exw = st.number_input("Transformer Unit EXW ($):", min_value=0.0, value=120000.0, step=10000.0, key="proj_trans_exw")

    with col_q3:
        st.markdown("#### Accessories & Solar")
        access_count = st.number_input("Accessories / Dry Containers Count:", min_value=0, value=2, step=1, key="proj_access_count")
        access_exw = st.number_input("Accessories Unit EXW ($):", min_value=0.0, value=50000.0, step=5000.0, key="proj_access_exw")

        solar_count = st.number_input("Solar PV Units Count:", min_value=0, value=0, step=1, key="proj_solar_count")
        solar_exw = st.number_input("Solar Unit EXW ($):", min_value=0.0, value=300000.0, step=10000.0, key="proj_solar_exw")

    total_containers_project = max(1, bess_count + oog_count + mvs_count + transformer_count + access_count + solar_count)
    total_exw_project = (
        (bess_count * bess_exw) + (oog_count * oog_exw) + 
        (mvs_count * mvs_exw) + (transformer_count * transformer_exw) + 
        (access_count * access_exw) + (solar_count * solar_exw)
    )
    is_bess = (bess_count > 0 or oog_count > 0)
    is_dg = is_bess

    st.success(f"📊 סה\"כ יחידות לפרויקט: {total_containers_project} | סה\"כ ערך EXW במפעל: **${total_exw_project:,.2f}**")

with tab2:
    st.subheader("🚢 תעריפי הובלה ימית, BAF לפי TEU ו־DTHC פרטניים" if is_hebrew else "Itemized Ocean Freight, BAF per TEU & DTHC")
    
    selected_carrier = st.selectbox("בחירת חברת ספנות:" if is_hebrew else "Select Carrier:", list(CARRIER_FUEL_SURCHARGES.keys()), key="tab2_carrier")
    carrier_data = CARRIER_FUEL_SURCHARGES[selected_carrier]

    baf_included = st.checkbox("תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית הבסיסי" if is_hebrew else "Bunker Surcharge (BAF) included in Base Ocean Freight", value=False, key="tab2_baf_incl")

    st.markdown("##### 1. עלות הובלה ימית ליחידה (Ocean Freight / Unit):")
    oc_col1, oc_col2, oc_col3 = st.columns(3)
    with oc_col1:
        unit_freight_bess = st.number_input("BESS Freight ($):", value=31850.0 * carrier_data["bess_multiplier"], step=500.0, key="freight_bess")
        unit_freight_oog = st.number_input("OOG Flat Rack Freight ($):", value=29900.0, step=500.0, key="freight_oog")
    with oc_col2:
        unit_freight_mvs = st.number_input("MVS Freight ($):", value=4200.0, step=200.0, key="freight_mvs")
        unit_freight_trans = st.number_input("Transformer Freight ($):", value=5500.0, step=200.0, key="freight_trans")
    with oc_col3:
        unit_freight_access = st.number_input("Accessories / Dry Freight ($):", value=3200.0, step=200.0, key="freight_access")
        unit_freight_solar = st.number_input("Solar PV Freight ($):", value=3360.0, step=200.0, key="freight_solar")

    st.markdown("---")
    st.markdown("##### 2. היטל דלק (BAF - Bunker Surcharge) מחושב לפי נפח TEU:")
    baf_mult = carrier_data["dthc_mult"]
    base_baf_per_teu = st.number_input("תעריף BAF בסיסי ל־TEU אחד ($):", value=420.0 * baf_mult, step=20.0, key="baf_per_teu")

    teu_bess, teu_oog, teu_mvs, teu_trans, teu_access, teu_solar = 2.0, 2.0, 1.0, 1.0, 1.0, 1.0

    baf_bess = 0.0 if baf_included else (base_baf_per_teu * teu_bess)
    baf_oog = 0.0 if baf_included else (base_baf_per_teu * teu_oog)
    baf_mvs = 0.0 if baf_included else (base_baf_per_teu * teu_mvs)
    baf_trans = 0.0 if baf_included else (base_baf_per_teu * teu_trans)
    baf_access = 0.0 if baf_included else (base_baf_per_teu * teu_access)
    baf_solar = 0.0 if baf_included else (base_baf_per_teu * teu_solar)

    st.markdown("---")
    st.markdown("##### 3. דמי טיפול בנמל יעד (DTHC - Destination THC) לפי סוג מכולה/ציוד:")
    dthc_mult = carrier_data["dthc_mult"]
    
    dh_col1, dh_col2, dh_col3 = st.columns(3)
    with dh_col1:
        dthc_bess = st.number_input("BESS (20/40 DG Heavy) DTHC ($):", value=650.0 * dthc_mult, step=50.0, key="dthc_bess")
        dthc_oog = st.number_input("OOG Flat Rack DTHC ($):", value=850.0 * dthc_mult, step=50.0, key="dthc_oog")
    with dh_col2:
        dthc_mvs = st.number_input("MVS Station DTHC ($):", value=420.0 * dthc_mult, step=30.0, key="dthc_mvs")
        dthc_trans = st.number_input("Transformer DTHC ($):", value=480.0 * dthc_mult, step=30.0, key="dthc_trans")
    with dh_col3:
        dthc_access = st.number_input("Accessories (20/40 Dry) DTHC ($):", value=280.0 * dthc_mult, step=20.0, key="dthc_access")
        dthc_solar = st.number_input("Solar PV DTHC ($):", value=300.0 * dthc_mult, step=20.0, key="dthc_solar")

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
    st.subheader("🚚 תעריפי הובלה יבשתית נפרדים מנמל לאתר (Itemized Inland Drayage)" if is_hebrew else "Itemized Inland Drayage per Equipment Type")
    
    st.markdown("##### הגדרת עלות הובלת משאיות ליחידה (Port to Site):")
    dr_col1, dr_col2, dr_col3 = st.columns(3)
    with dr_col1:
        drayage_bess = st.number_input("BESS Drayage / Unit ($):", value=3200.0, step=200.0, key="dray_bess")
        drayage_oog = st.number_input("OOG Drayage / Unit ($):", value=3800.0, step=200.0, key="dray_oog")
    with dr_col2:
        drayage_mvs = st.number_input("MVS Drayage / Unit ($):", value=1400.0, step=100.0, key="dray_mvs")
        drayage_trans = st.number_input("Transformer Drayage / Unit ($):", value=1800.0, step=100.0, key="dray_trans")
    with dr_col3:
        drayage_access = st.number_input("Accessories Drayage / Unit ($):", value=850.0, step=100.0, key="dray_access")
        drayage_solar = st.number_input("Solar PV Drayage / Unit ($):", value=950.0, step=100.0, key="dray_solar")

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
    st.subheader("⚖️ רגולציה, אישורים מנדטוריים שוטפים ותחזית סוף חיים" if is_hebrew else "Regulatory Compliance & Decommissioning")

    if dest_country == "Israel":
        st.markdown("### 🇮🇱 רגולציית חומ\"ס ואישורי הובלה שוטפים (ישראל)")
        st.error("🚨 **מנדטורי (חובה חוקית בישראל):** אישור הובלה פרטני מאגף הפיקוח והרכב במשרד התחבורה לכל מכולת BESS.")
        mot_fee_per_bess = st.number_input("עלות אגרת אישור הובלה ממשרד התחבורה ליחידת BESS ($):", value=350.0, step=50.0, key="mot_fee_input")
        mot_total_approval_cost = mot_fee_per_bess * float(bess_count + oog_count)

        st.warning("⚠️ **מנדטורי (חובה נמלית):** אגרות בדיקה, פיקוח חומ\"ס ואישורי כבאות בנמלי הים.")
        local_regulatory_permits = st.number_input("עלות כוללת להיתרי חומ\"ס נמלים ($):", value=1500.0, step=100.0, key="reg_cost_input")
        
        epr_recycling_total_usd = 0.0
        battery_passport_total_usd = 0.0
        include_mot_approval = True
        include_regulatory = True

    else:
        st.markdown(f"### 🇪🇺 רגולציה שוטפת ואחריות יצרן (איחוד אירופי — {dest_country})")
        st.error("🚨 **מנדטורי (חובה באירופה):** דרכון סוללות דיגיטלי (EU Battery Passport) ותיעוד שרשרת אספקה.")
        battery_passport_flat = st.number_input("עלות כוללת לדרכון סוללות ותיעוד ($):", value=1200.0, step=100.0, key="bp_cost_input")
        battery_passport_total_usd = battery_passport_flat

        st.warning("⚠️ **מנדטורי (חובה באירופה):** דמי טיפול באחריות יצרן מורחבת (EPR / Recycling שוטף).")
        epr_fee_per_unit = st.number_input("עלות EPR שוטף ליחידת BESS ($):", value=450.0, step=50.0, key="epr_unit_input")
        epr_recycling_total_usd = epr_fee_per_unit * float(bess_count + oog_count)

        include_regulatory = st.checkbox("כלול אגרות היתרי כניסה והיערכות אתר מקומיים באירופה [בחירה]", value=True, key="reg_permits_toggle")
        local_regulatory_permits = st.number_input("עלות היתרים מקומיים ($):", value=600.0, step=100.0, key="reg_cost_input") if include_regulatory else 0.0

        mot_total_approval_cost = 0.0
        include_mot_approval = False

    st.markdown("---")
    st.markdown("### 🔄 תחזית תקציבית למחזור ופירוק סוף חיים (Decommissioning Provision)")
    with st.expander("📌 ניהול והפרשה לעתיד (אופציונלי למנהל הפרויקט)", expanded=False):
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
    requires_heavy_lift = st.checkbox("דורש סקר מטענים כבדים / מנוף עוגן (Heavy-Lift Survey) [בחירה]", value=is_bess, key="hl_survey_toggle")
    heavy_lift_survey_cost = st.number_input("עלות סקר מטענים כבדים ($):", value=2500.0, step=250.0, key="hl_cost_input") if requires_heavy_lift else 0.0

# ---------------------------------------------------------
# טאב 5 (או 5_eu) - הנחות מסלולים אינדיקטיביות
# ---------------------------------------------------------
if show_route_optimization:
    with tab5:
        st.subheader("🗺️ הנחות מסלולים אינדיקטיביות באירופה (Romania / Poland / Germany)")
        st.info("ניתוח חלופות נמלי פריקה (לדוגמה Constanța מול Burgas) והובלה יבשתית לאתר הפרויקט.")
        st.markdown("""
        * **קונסטנצה (רומניה):** מתאים לפרויקטים בדרום/מרכז רומניה (כגון Iepurești ו־Ghimpați).
        * **בורגס (בולגריה):** שער כניסה חלופי לבלקן עם גישה למשאיות כבדות.
        * **גדנסק/גדיניה (פולין):** מתאים לפרויקטי צפון/מרכז אירופה.
        """)

# ---------------------------------------------------------
# טאב פרויקטי אנלייט (שירה)
# ---------------------------------------------------------
with tab_projects:
    st.subheader("📂 פרויקטי Enlight 2027-2028 (ניהול ובקרה — שירה)")
    st.info("בחינת תרחישים לפרויקטי אגירה ואנרגיה מתחדשת של קבוצת אנלייט בשנים 2027–2028.")
    
    enlight_project_type = st.selectbox("בחר פרויקט לטעינת נתונים אוטומטית:", [proj for proj in ["פרויקט אשלים / צאלים (ישראל)", "פרויקט Iepurești (רומניה)", "פרויקט Stk. Ned (מזרח אירופה)"]], key="enlight_proj_sel")
    if "אשלים" in enlight_project_type:
        st.markdown("📌 **מאפייני פרויקט ישראל:** 20 יחידות BESS, הובלה דרך נמל חיפה, אישורי משרד התחבורה חובה.")
    elif "Iepurești" in enlight_project_type:
        st.markdown("📌 **מאפייני פרויקט רומניה:** פרויקט סולארי + BESS, פריקה בקונסטנצה, רגולציית איחוד אירופי.")
    else:
        st.markdown("📌 **מאפייני פרויקט אירופאי כללי:** עמידה בדרכון סוללות ותקן UN3536.")

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
    "EXW (Ex Works)": trended_exw,
    "FOB (Free on Board)": trended_exw + china_inland_drayage + china_origin_thc,
    "CIF (Cost, Insurance & Freight)": trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd,
    "DAP (Delivered at Place)": ddp_supplier_scope_ex_vat,
    "DDP (Delivered Duty Paid)": ddp_supplier_scope_incl_vat
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

# ---------------------------------------------------------
# טאב הסיכום הפיננסי ויצוא לאקסל
# ---------------------------------------------------------
with tab_summary:
    st.subheader(f"📊 Financial & Regulatory Summary — {incoterm} ({display_currency})")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Economic Cost", f"{curr_symbol} {econ_val:,.2f}")
    m3.metric("Total Cash Requirement", f"{curr_symbol} {cash_val:,.2f}")
    m4.metric("Paid to Supplier", f"{curr_symbol} {supplier_val:,.2f}")

    st.markdown("---")
    st.subheader("📋 פירוט רכיבי העלויות לפרויקט (Cost Breakdown Table)")

    summary_df = pd.DataFrame({
        "Cost Component (רכיב עלות)": [
            "Equipment EXW (ערך ציוד במפעל)",
            "China Inland Drayage & THC",
            "Ocean Freight (הובלה ימית בסיסית)",
            "BAF (היטל דלק ימי לפי TEU)",
            "Destination THC (DTHC)",
            "Marine Insurance (ביטוח ימי)",
            "Customs Duty (מכס)",
            "Inland Drayage (הובלה יבשתית לאתר)",
            "Regulatory & MOT Approvals (רגולציה ומשרד התחבורה)",
            "Site Crane & Unloading (עגורן ופריקה)",
            "Decommissioning Provision (הפרשת סוף חיים)",
            "Contingency (בלת״ם)"
        ],
        "Amount (USD $)": [
            trended_exw,
            china_inland_drayage + china_origin_thc,
            total_base_ocean_freight * trend_multiplier,
            total_baf_ocean * trend_multiplier,
            destination_thc_total,
            insurance_total_usd,
            customs_duty_usd,
            inland_drayage_total_usd,
            active_regulatory_permits,
            active_site_crane,
            decommissioning_total_usd,
            contingency_usd
        ]
    })
    
    st.dataframe(summary_df.style.format({"Amount (USD $)": "${:,.2f}"}), use_container_width=True)

    st.markdown("---")
    st.subheader("📥 ייצוא נתונים לאקסל (Excel Export)")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        summary_df.to_excel(writer, sheet_name='Cost Summary', index=False)
    excel_data = output.getvalue()

    st.download_button(
        label="📥 הורד דוח פיננסי מלא לאקסל (Download Excel Report)",
        data=excel_data,
        file_name=f"TerraVol_Project_Report_{dest_country}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
