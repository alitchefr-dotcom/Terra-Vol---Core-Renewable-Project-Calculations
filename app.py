import streamlit as st
import pandas as pd
import os
import requests
import base64
from datetime import date

# ---------------------------------------------------------
# הגדרת תצורת עמוד ושפה
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
lang = st.sidebar.radio("Select Language / בחר שפה:", ["Hebrew (עברית)", "English"], index=0)
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
    "tab1": "📋 Cargo & Destination" if not is_hebrew else "📋 פרטי מטען, יעד ומיקום",
    "tab2": "⚓ Supply Chain & Incoterms" if not is_hebrew else "⚓ שרשרת אספקה ותנאי סחר",
    "tab3": "📦 Storage & Site Drayage" if not is_hebrew else "📦 אחסנה, השהיות והובלת אתר",
    "tab4": "⚖️ DG Compliance & Regulation" if not is_hebrew else "⚖️ רגולציית חומ\"ס DG ורגולציית מוצר",
    "tab5_eu": "🗺️ Illustrative Route Assumptions" if not is_hebrew else "🗺️ הנחות מסלולים אינדיקטיביות",
    "tab_summary": "📊 Financial & Regulatory Summary" if not is_hebrew else "📊 דוח בקרה פיננסית ורגולטורית",
    "origin_port": "Port of Loading:" if not is_hebrew else "נמל מוצא:",
    "dest_port": "Port of Discharge:" if not is_hebrew else "נמל יעד ימי (Port of Discharge):",
    "dest_country": "Final Project Country:" if not is_hebrew else "מדינת יעד סופית (אתר הפרויקט):",
    "site_address": "Project Site Name / Location:" if not is_hebrew else "שם / מיקום אתר הפרויקט:",
    "site_coords": "GPS Coordinates (Lat, Long):" if not is_hebrew else "קואורדינטות GPS (רוחב, אורך):",
    "site_zip": "Postal / Zip Code:" if not is_hebrew else "מיקוד / קוד דואר:",
    "exw_val": "EXW Equipment Value (USD):" if not is_hebrew else "ערך ציוד בבית המפעל בסין (EXW USD):",
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

EQUIPMENT_CONFIG = {
    "BESS Container (UN3536 Class 9)": {
        "code_key": "BESS",
        "is_bess": True,
        "default_exw": 500000.0,
        "default_freight": 6300.0,
        "capacity_label": "Total Project Capacity (MWh):" if not is_hebrew else "קיבולת אגירה כוללת לפרויקט (MWh):",
        "unit_label": "BESS System Count:" if not is_hebrew else "כמות מערכות BESS:",
        "unit_metric": "MWh",
        "eu_duty": 2.7, "eu_hs": "8507600000",
        "il_duty": 0.0, "il_hs": "8507.60.00",
        "has_passport_epr": True,
        "default_un": "UN3536 (Cargo Transport Unit containing lithium ion batteries)"
    },
    "Solar PV Modules": {
        "code_key": "Solar",
        "is_bess": False,
        "default_exw": 300000.0,
        "default_freight": 3360.0,
        "capacity_label": "Total Project Capacity (MWp):" if not is_hebrew else "הספק פרויקט סולארי כולל (MWp):",
        "unit_label": "PV Module Pallets / Units:" if not is_hebrew else "כמות משטחי / יחידות פאנלים:",
        "unit_metric": "MWp",
        "eu_duty": 0.0, "eu_hs": "8541400000",
        "il_duty": 0.0, "il_hs": "8541.40.00",
        "has_passport_epr": False,
        "default_un": "Non-DG / Other"
    },
    "Transformers / Heavy Equipment": {
        "code_key": "Transformer",
        "is_bess": False,
        "default_exw": 400000.0,
        "default_freight": 5500.0,
        "capacity_label": "Total Transformer Capacity (MVA):" if not is_hebrew else "הספק שנאים כולל (MVA):",
        "unit_label": "Transformer Count:" if not is_hebrew else "כמות שנאים:",
        "unit_metric": "MVA",
        "eu_duty": 3.7, "eu_hs": "8504230000",
        "il_duty": 0.0, "il_hs": "8504.23.00",
        "has_passport_epr": False,
        "default_un": "Non-DG / Other"
    },
    "Inverters / MV Station / Power Skids": {
        "code_key": "MVS",
        "is_bess": False,
        "default_exw": 250000.0,
        "default_freight": 4200.0,
        "capacity_label": "Total Station Capacity (MW):" if not is_hebrew else "הספק תחנות המרה / סקידים כולל (MW):",
        "unit_label": "Station / Skid Count:" if not is_hebrew else "כמות תחנות / סקידים:",
        "unit_metric": "MW",
        "eu_duty": 0.0, "eu_hs": "8504409000",
        "il_duty": 0.0, "il_hs": "8504.40.90",
        "has_passport_epr": False,
        "default_un": "Non-DG / Other"
    },
    "E-House Units": {
        "code_key": "EHouse",
        "is_bess": False,
        "default_exw": 350000.0,
        "default_freight": 4800.0,
        "capacity_label": "Total Project Capacity (MW equivalent):" if not is_hebrew else "הספק שקול לפרויקט (MW):",
        "unit_label": "E-House Unit Count:" if not is_hebrew else "כמות מבני E-House:",
        "unit_metric": "MW",
        "eu_duty": 2.1, "eu_hs": "8537200000",
        "il_duty": 0.0, "il_hs": "8537.20.00",
        "has_passport_epr": False,
        "default_un": "Non-DG / Other"
    }
}

ORIGIN_PORTS = [
    "Shanghai", "Ningbo-Zhoushan", "Shenzhen / Yantian", 
    "Guangzhou / Nansha", "Qingdao", "Tianjin", "Xiamen"
]

DESTINATION_PORTS = {
    "Israel": [
        "Haifa Port", 
        "Ashdod Port (South Port / Main)", 
        "Israel Shipyards Port"
    ],
    "Romania": [
        "Constanța, Romania", 
        "Burgas, Bulgaria (Transit to Romania)"
    ],
    "Spain": [
        "Valencia, Spain", 
        "Barcelona, Spain"
    ],
    "Germany": [
        "Hamburg, Germany", 
        "Bremerhaven, Germany"
    ],
    "Italy": [
        "Genoa, Italy", 
        "Trieste, Italy"
    ],
    "Greece": [
        "Piraeus, Greece", 
        "Thessaloniki, Greece"
    ],
    "Poland": [
        "Gdansk, Poland", 
        "Gdynia, Poland"
    ],
    "Other / Custom": [
        "Rotterdam, Netherlands",
        "Antwerp-Bruges, Belgium",
        "Koper, Slovenia"
    ]
}

VAT_RATES = {
    "Israel": 18.0, "Romania": 19.0, "Germany": 19.0, "Spain": 21.0, 
    "Italy": 22.0, "Greece": 24.0, "Poland": 23.0, "Other / Custom": 0.0
}

DEFAULT_INSURANCE_RATES = {"Israel": 0.08, "Romania": 0.15, "Germany": 0.15, "Spain": 0.15, "Italy": 0.15, "Greece": 0.15, "Poland": 0.15, "Other / Custom": 0.15}
DEFAULT_FREE_DAYS = {"Israel": 4, "Romania": 7, "Germany": 7, "Spain": 7, "Italy": 7, "Greece": 7, "Poland": 7, "Other / Custom": 7}
CARRIER_FUEL_SURCHARGES = {
    "ZIM (Integrated Shipping)": {"baf": 843.0, "code": "NBF / EFS"},
    "Hapag-Lloyd": {"baf": 780.0, "code": "MFR / EFS"},
    "COSCO Shipping": {"baf": 720.0, "code": "FAF / Bunker"},
    "MSC": {"baf": 750.0, "code": "BRS / BAF"},
    "Maersk": {"baf": 760.0, "code": "EFF / BAF"},
    "Custom Carrier": {"baf": 450.0, "code": "Custom BAF"}
}

st.sidebar.subheader(T["scenario_header"])
incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)", "EXW (Ex Works)"])
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"])

st.sidebar.markdown("---")
st.sidebar.markdown("📅 **Market Forecast Engine**" if not is_hebrew else "📅 **מנוע תחזית שוק לפי תאריך**")
forecast_date = st.sidebar.date_input("Target Delivery Date:" if not is_hebrew else "תאריך יעד למשלוח:", value=date(2027, 6, 30))
market_scenario = st.sidebar.selectbox("Market Scenario:" if not is_hebrew else "תרחיש שוק:", ["Conservative (+8.0% p.a.)", "Base Market Trend (+4.5% p.a.)", "Optimistic / Stable (0.0%)"])

today_date = date.today()
delta_days = (forecast_date - today_date).days
years_diff = max(0.0, delta_days / 365.25)

if "Conservative" in market_scenario:
    annual_inflation = 0.08
elif "Base" in market_scenario:
    annual_inflation = 0.045
else:
    annual_inflation = 0.0

trend_multiplier = (1.0 + annual_inflation) ** years_diff
trend_pct = (trend_multiplier - 1.0) * 100.0

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
    st.sidebar.toast("⚠️ Live exchange rates unavailable. Using default fallback rates.", icon="⚠️")
    live_eur, live_ils = 0.92, 3.70

usd_to_eur = st.sidebar.number_input("USD to EUR Rate:", value=float(live_eur), step=0.01, min_value=0.0001)
usd_to_ils = st.sidebar.number_input("USD to ILS Rate:", value=float(live_ils), step=0.01, min_value=0.0001)

if usd_to_eur <= 0 or usd_to_ils <= 0:
    st.error("Exchange rates must be greater than zero.")
    st.stop()

def convert_from_usd(amount_usd, target_curr):
    if target_curr == "USD ($)": return amount_usd, "$"
    if target_curr == "EUR (€)": return amount_usd * usd_to_eur, "€"
    if target_curr == "ILS (₪)": return amount_usd * usd_to_ils, "₪"
    return amount_usd, "$"

st.sidebar.markdown("---")
dest_country = st.sidebar.selectbox(T["dest_country"], list(VAT_RATES.keys()), index=0)

if 'last_country' not in st.session_state:
    st.session_state.last_country = dest_country
if st.session_state.last_country != dest_country:
    st.session_state.last_country = dest_country
    st.session_state.site_name_input = ""
    st.session_state.site_coords_input = ""
    st.session_state.site_zip_input = ""

show_route_optimization = (dest_country != "Israel")

if show_route_optimization:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_summary"]])
    tab_summary = tab6
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_summary"]])
    tab_summary = tab5

with tab1:
    st.subheader("Equipment Specification & Site Destination" if not is_hebrew else "מפרט ציוד, מאפייני פרויקט ומיקום אתר")
    col1, col2 = st.columns(2)
    
    with col1:
        origin_port = st.selectbox(T["origin_port"], ORIGIN_PORTS)
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["Other / Custom"])
        dest_port = st.selectbox(T["dest_port"], available_dest_ports)

        site_address = st.text_input(T["site_address"], key="site_name_input", placeholder="e.g. Ashalim / Iepurești")
        
        sub_col_a, sub_col_b = st.columns(2)
        with sub_col_a:
            site_coords = st.text_input(T["site_coords"], key="site_coords_input", placeholder="Lat, Long")
        with sub_col_b:
            site_zip = st.text_input(T["site_zip"], key="site_zip_input", placeholder="Postal Code")

        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0)
        vat_recovery_pct = st.number_input("VAT Recoverability (%)" if not is_hebrew else "אחוז קיזוז מע\"מ (%):", value=100.0, min_value=0.0, max_value=100.0, step=1.0)
        vat_paid_by_supplier = st.checkbox("VAT paid by supplier under commercial arrangement" if not is_hebrew else "המע״מ משולם על ידי הספק במסגרת ההסכם המסחרי", value=False)

    with col2:
        cargo_type = st.selectbox("Cargo Type / Equipment:" if not is_hebrew else "סוג ציוד / מערכת:", list(EQUIPMENT_CONFIG.keys()))
        cfg = EQUIPMENT_CONFIG[cargo_type]
        is_bess = cfg["is_bess"]
        
        current_duty = cfg["il_duty"] if dest_country == "Israel" else cfg["eu_duty"]
        current_hs = cfg["il_hs"] if dest_country == "Israel" else cfg["eu_hs"]
        
        st.caption(f"📌 **HS Code:** {current_hs} | **Duty:** {current_duty}% | **Source:** EU/IL Taric (Verified 2026)")

        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            unit_count = st.number_input(cfg["unit_label"], min_value=1, value=10, step=1)
        with sub_c2:
            container_count = st.number_input("Container Count:" if not is_hebrew else "כמות מכולות משלוח:", min_value=1, value=10, step=1)

        capacity_val = st.number_input(cfg["capacity_label"], value=40.0, step=5.0, min_value=0.1)
        
        if is_bess:
            weight_tier_options = {
                "Below 27 MTS ($6,300)": 6300.0,
                "27.0 - 34.9 MTS ($12,600)": 12600.0,
                "35.0 - 44.9 MTS ($18,375)": 18375.0,
                "45.0 - 48.0 MTS ($21,000)": 21000.0
            }
            weight_tier = st.selectbox("Weight Tier (MTS / Ton):" if not is_hebrew else "מדרגת משקל ליחידת BESS (MTS / Ton):", list(weight_tier_options.keys()), index=3)
            suggested_freight = weight_tier_options[weight_tier]
        else:
            suggested_freight = cfg["default_freight"]

        if is_bess:
            un_number = st.selectbox(
                "UN Number (Dangerous Goods Classification):" if not is_hebrew else "מספר UN (סיווג מטען מסוכן):", 
                ["UN3536 (Cargo Transport Unit containing lithium ion batteries)", "UN3480 (Lithium ion batteries)", "UN3481 (Lithium ion batteries packed with equipment)", "Non-DG / Other"]
            )
        else:
            un_number = st.selectbox(
                "UN Number (Dangerous Goods Classification):" if not is_hebrew else "מספר UN (סיווג מטען מסוכן):", 
                ["Non-DG / Other", "UN3480 (Lithium ion batteries)", "UN3481 (Lithium ion batteries packed with equipment)", "UN3536 (Cargo Transport Unit containing lithium ion batteries)"]
            )
        
        is_dg = (un_number != "Non-DG / Other")

        if 'last_cargo_type' not in st.session_state:
            st.session_state.last_cargo_type = cargo_type
            st.session_state.exw_user_value = cfg["default_exw"]

        if st.session_state.last_cargo_type != cargo_type:
            st.session_state.last_cargo_type = cargo_type
            st.session_state.exw_user_value = cfg["default_exw"]

        exw_value_usd = st.number_input(T["exw_val"], value=float(st.session_state.exw_user_value), step=10000.0, min_value=0.0)
        st.session_state.exw_user_value = exw_value_usd

with tab2:
    st.markdown('<div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">שרשרת אספקה מלאה והקצאת עלויות לפי Incoterms</div>' if is_hebrew else '<div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Full Supply Chain & Incoterms Allocation</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("Shipping Carrier:" if not is_hebrew else "חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        base_freight_per_unit = st.number_input("Base Ocean Freight per Container ($):" if not is_hebrew else "מחיר הובלה ימית בסיס ליחידה ($):", value=float(suggested_freight), step=500.0, min_value=0.0)
        baf_included = st.checkbox("Bunker Surcharge (BAF) included in Base Ocean Freight" if not is_hebrew else "תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית הבסיסי", value=False)
        active_baf = 0.0 if baf_included else float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"])
        baf_surcharge = st.number_input(f"Bunker Surcharge ($):", value=active_baf, step=50.0, min_value=0.0)
        dest_thc_port_fee = st.number_input("Destination THC / Port Fee per Container ($):" if not is_hebrew else "אגרות ותעריפי נמל יעד ליחידה ($):", value=380.0, step=20.0, min_value=0.0)
        
    with col_b:
        china_inland_drayage = st.number_input("China Inland Transport + Export Customs ($):" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא (USD סה\"כ):", value=2200.0, step=300.0, min_value=0.0)
        china_origin_thc = st.number_input("China Origin THC & Port Fees ($):" if not is_hebrew else "אגרות ותעריפי נמל מוצא בסין (Origin THC סה\"כ):", value=1300.0, step=200.0, min_value=0.0)
        heavy_lift_survey = st.number_input("Heavy Lift / Route Survey ($):" if not is_hebrew else "סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0, step=500.0, min_value=0.0)
        
        customs_duty_pct = st.number_input("Indicative Import Customs Duty (%):" if not is_hebrew else "שיעור מכס אינדיקטיבי (%):", value=float(current_duty), step=0.1, min_value=0.0, max_value=100.0)
        st.caption(f"Country: {dest_country} | Active HS Code: {current_hs}")
        insurance_pct = st.number_input("Marine Cargo Insurance Rate (%):" if not is_hebrew else "שיעור ביטוח ימי (%):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.08), step=0.01, min_value=0.0, max_value=20.0)

with tab3:
    st.subheader("Port Demurrage, Storage & Inland Drayage" if not is_hebrew else "קנסות נמל, אחסנה חיצונית והובלת אתר")
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("Port Free Days:", value=DEFAULT_FREE_DAYS.get(dest_country, 7), step=1, min_value=0)
        actual_port_days = st.number_input("Actual Port Dwell Days:", value=12, step=1, min_value=0)
        demurrage_daily_rate = st.number_input("Daily Demurrage Rate per Container ($):", value=250.0 if is_dg else 150.0, step=10.0, min_value=0.0)
    with col_y:
        use_external_storage = st.checkbox("External Staging Yard", value=True)
        ext_storage_days = st.number_input("External Storage Days:", value=15, step=1, min_value=0)
        ext_storage_daily_rate = st.number_input("External Storage Daily Rate ($):", value=65.0 if is_dg else 45.0, step=5.0, min_value=0.0)
        default_drayage = 1850.0 if "Burgas" in dest_port else 600.0
        inland_drayage_per_unit = st.number_input("Inland Drayage from Port to Site ($):", value=default_drayage, step=50.0, min_value=0.0)

    st.markdown("---")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        include_site_crane = st.checkbox("Include site crane and pad offloading", value=True)
        site_crane_unloading = st.number_input("Site Crane & Pad Offloading ($):", value=8500.0, step=500.0, min_value=0.0, disabled=not include_site_crane)
    with col_ddp2:
        ddp_contingency_pct = st.number_input("Project Risk Contingency (%):", value=5.0, step=1.0, min_value=0.0, max_value=100.0)
        include_delay_scenario = st.checkbox("Include demurrage and external storage in project cost", value=False)

with tab4:
    tab_title_reg = "🛡️ DG Compliance, Battery Passport & EPR" if is_bess else "🛡️ DG Compliance & Product Regulation"
    st.subheader(tab_title_reg)
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown("### 📦 Dangerous Goods & Safety Permits")
        include_regulatory = st.checkbox("Include Hazardous Permits & DG Clearance cost" if not is_hebrew else "כלול עלות אישורי חומ\"ס והיתר רעלים", value=True)
        local_regulatory_permits = st.number_input("Hazardous Permits & DG Clearance ($):", value=1500.0 if is_dg else 400.0, step=100.0, min_value=0.0, disabled=not include_regulatory)

    with col_reg2:
        if is_bess:
            st.markdown("### ♻️ Battery Passport, EPR & End-of-Life (EoL)")
            include_epr = st.checkbox("Include EPR / Recycling cost", value=True)
            include_battery_passport = st.checkbox("Include Battery Passport / Carbon Audit cost", value=True)
            epr_basis = st.selectbox("EPR Calculation Basis", ["Per Container", "Per BESS System", "Per MWh", "Fixed Project Fee"])
            epr_fee_per_unit = st.number_input("EPR / Battery Recycling Unit Fee ($):", value=450.0, step=50.0, min_value=0.0, disabled=not include_epr)
            
            if epr_basis == "Per Container":
                calculated_epr_cost = epr_fee_per_unit * float(container_count)
            elif epr_basis == "Per BESS System":
                calculated_epr_cost = epr_fee_per_unit * float(unit_count)
            elif epr_basis == "Per MWh":
                calculated_epr_cost = epr_fee_per_unit * float(capacity_val)
            else:
                calculated_epr_cost = epr_fee_per_unit

            epr_recycling_total_usd = calculated_epr_cost if include_epr else 0.0
            battery_passport_fee = st.number_input("Battery Passport & Carbon Audit Fee ($):", value=1200.0, step=100.0, min_value=0.0, disabled=not include_battery_passport)
            battery_passport_total_usd = battery_passport_fee if include_battery_passport else 0.0
        else:
            st.info("ℹ️ Battery Passport & EPR regulations are automatically disabled and hidden for non-BESS equipment." if not is_hebrew else "ℹ️ רגולציות דרכון סוללה ו־EPR מנוטרלות ומוסתרות אוטומטית עבור ציוד שאינו סוללות.")
            epr_recycling_total_usd = 0.0
            battery_passport_total_usd = 0.0

    include_heavy_lift_toggle = st.checkbox("Include heavy-haul / abnormal-load handling cost" if not is_hebrew else "כלול עלות הובלה חריגה / מטען כבד", value=is_bess)
    requires_heavy_lift = is_bess and include_heavy_lift_toggle

# תחזית מחירים והחלת מקדם הטרנד המבוסס על תאריך היעד
trended_exw = exw_value_usd * trend_multiplier
trended_ocean_freight = ((base_freight_per_unit + baf_surcharge) * float(container_count)) * trend_multiplier
trended_drayage = (inland_drayage_per_unit * float(container_count)) * trend_multiplier

total_ocean_freight = trended_ocean_freight
inland_drayage_total_usd = trended_drayage

if show_route_optimization:
    with tab5:
        display_site = site_address if site_address else ("Unnamed Site" if not is_hebrew else "אתר ללא שם")
        st.subheader(f"🗺️ Illustrative Route & Port Comparison ({dest_country})")
        st.markdown(f"* **Ocean Freight (Forecasted):** ~${total_ocean_freight:,.0f}")
        st.markdown(f"* **Inland Drayage to {display_site}:** ~${inland_drayage_total_usd:,.0f}")

# =========================================================
# מנוע החישוב הפיננסי המלא (הטמעת הפרדת Incoterms של קלוד)
# =========================================================
cif_valuation_base = trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)
destination_thc_total = dest_thc_port_fee * float(container_count)

indicative_vat_base_import_usd = customs_valuation_base_usd + customs_duty_usd + destination_thc_total
vat_total_usd = indicative_vat_base_import_usd * (applied_vat / 100.0)

supplier_vat_component = vat_total_usd if (vat_paid_by_supplier and incoterm == "DDP (Delivered Duty Paid)") else 0.0

ddp_supplier_scope_ex_vat = (
    trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + 
    insurance_total_usd + customs_duty_usd + destination_thc_total + inland_drayage_total_usd
)
ddp_supplier_scope_incl_vat = ddp_supplier_scope_ex_vat + supplier_vat_component

overdue_days = max(0, actual_port_days - free_days)
demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
external_storage_total_usd = (float(ext_storage_days) * ext_storage_daily_rate * float(container_count)) if use_external_storage else 0.0

active_regulatory_permits = local_regulatory_permits if include_regulatory else 0.0
active_site_crane = site_crane_unloading if include_site_crane else 0.0
active_heavy_lift = heavy_lift_survey if requires_heavy_lift else 0.0

effective_delay_cost = (demurrage_total_usd + external_storage_total_usd) if include_delay_scenario else 0.0

project_delivery_cost = (
    ddp_supplier_scope_ex_vat + 
    active_site_crane + 
    active_regulatory_permits + 
    epr_recycling_total_usd + 
    battery_passport_total_usd + 
    active_heavy_lift + 
    effective_delay_cost
)

supplier_commercial_price_options = {
    "EXW (Ex Works)": trended_exw,
    "FOB (Free on Board)": trended_exw + china_inland_drayage + china_origin_thc,
    "CIF (Cost, Insurance & Freight)": trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight + insurance_total_usd,
    "DDP (Delivered Duty Paid)": ddp_supplier_scope_incl_vat
}

modeled_supplier_price = supplier_commercial_price_options.get(incoterm, trended_exw)
supplier_commercial_price = modeled_supplier_price

# יישום ההצעה של קלוד להפרדת תשלום ספק מול תשלום ישיר של הקונה לפי Incoterm
supplier_scope_total = supplier_commercial_price_options.get(incoterm, trended_exw)
buyer_direct_payment_usd = max(0.0, project_delivery_cost - supplier_scope_total)

effective_vat_cash = 0.0 if vat_paid_by_supplier else vat_total_usd
recoverable_vat = vat_total_usd * (vat_recovery_pct / 100.0)
effective_non_recoverable_vat = 0.0 if vat_paid_by_supplier else (vat_total_usd - recoverable_vat)

buyer_supply_chain_total = project_delivery_cost
contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
economic_cost_ex_vat = total_landed_cost_ex_vat + effective_non_recoverable_vat
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + effective_vat_cash

metric_name = cfg["unit_metric"]
total_capacity_units = capacity_val if capacity_val > 0 else 1.0
operational_logistics_only_usd = china_inland_drayage + china_origin_thc + total_ocean_freight + destination_thc_total + inland_drayage_total_usd
logistics_per_unit_metric = operational_logistics_only_usd / total_capacity_units
regulatory_only_usd = active_regulatory_permits + battery_passport_total_usd + epr_recycling_total_usd
regulatory_per_unit_metric = regulatory_only_usd / total_capacity_units

display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_scope_total, display_currency)
buyer_direct_val, _ = convert_from_usd(buyer_direct_payment_usd, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
econ_val, _ = convert_from_usd(economic_cost_ex_vat, display_currency)
op_log_display, _ = convert_from_usd(logistics_per_unit_metric, display_currency)
reg_metric_display, _ = convert_from_usd(regulatory_per_unit_metric, display_currency)

with tab_summary:
    st.subheader(f"📊 Financial & Regulatory Control Dashboard - {incoterm} ({display_currency})")
    
    # הצגת 6 מדדים מרכזיים כולל ההפרדה המסחרית החדשה (Paid to Supplier מול Paid Directly by Buyer)
    m1, m2, m3, m4, m7, m5 = st.columns(6)
    m1.metric("Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Economic Cost", f"{curr_symbol} {econ_val:,.2f}")
    m3.metric("Total Cash Requirement", f"{curr_symbol} {cash_val:,.2f}")
    m4.metric("Paid to Supplier (Invoice)", f"{curr_symbol} {supplier_val:,.2f}")
    m7.metric("Paid Directly by Buyer", f"{curr_symbol} {buyer_direct_val:,.2f}")
    m5.metric(f"Logistics / {metric_name}", f"{curr_symbol} {op_log_display:.4f} /{metric_name}")

    st.markdown("---")
    st.info(f"📌 Market Model: Internal Verified Assumptions | Target Date: {forecast_date} | Trend Adjustment: {trend_pct:+.1f}%")

    st.subheader("Detailed Cost Breakdown (USD Base)")
    
    cost_labels = [
        "Equipment Value (EXW + Forecast Trend)" if not is_hebrew else "ערך ציוד (כולל תחזית שוק)",
        "China Inland Transport & Export", "China Origin THC & Port Fees",
        f"Ocean Freight + BAF ({selected_carrier})", "Marine Cargo Insurance",
        "Indicative Import Customs Duty", "Destination THC & Wharfage",
        "Hazardous Permits & DG Clearance"
    ]
    amounts_no_vat = [
        trended_exw, china_inland_drayage, china_origin_thc, total_ocean_freight,
        insurance_total_usd, customs_duty_usd, destination_thc_total,
        active_regulatory_permits
    ]

    if is_bess:
        cost_labels.extend(["Battery Passport & Carbon Audit", "EPR / Battery Recycling Fee"])
        amounts_no_vat.extend([battery_passport_total_usd, epr_recycling_total_usd])

    cost_labels.extend([
        "Port Demurrage Charges", "External Staging Yard Storage", 
        "Inland Drayage (Port to Site)", "Site Crane & Pad Offloading", 
        "Heavy Lift / Route Survey", "Project Risk Contingency", "Import VAT (Total)"
    ])
    amounts_no_vat.extend([
        (demurrage_total_usd if include_delay_scenario else 0.0),
        (external_storage_total_usd if include_delay_scenario else 0.0),
        inland_drayage_total_usd, active_site_crane,
        active_heavy_lift, contingency_usd
    ])

    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": cost_labels,
        "Amount (USD)": amounts_no_vat + [vat_total_usd]
    })
    
    pct_list = [(amt / total_landed_cost_ex_vat) * 100.0 for amt in amounts_no_vat] + [0.0] if total_landed_cost_ex_vat > 0 else [0.0]*(len(amounts_no_vat)+1)
    df_summary["% of Landed Cost ex-VAT"] = [f"{p:.2f}%" for p in pct_list]
    
    st.dataframe(df_summary, use_container_width=True)
    
    csv_filename = f"TerraVol_{cfg['code_key']}_Report_{incoterm.split(' ')[0]}.csv"
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig' if is_hebrew else 'utf-8')
    st.download_button(
        label="📥 Export Financial & Regulatory CSV Report" if not is_hebrew else "📥 ייצוא דוח פיננסי ורגולטורי ל-CSV",
        data=csv_data,
        file_name=csv_filename,
        mime="text/csv"
    )

st.markdown("---")
st.caption("Renewable Energy Logistics & Landed Cost Calculator — Professional MVP Edition.")
