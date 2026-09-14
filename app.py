import streamlit as st
import pandas as pd
import os
import requests
import base64

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
    "caption": "Professional MVP Project Cargo Calculator incorporating Supply Chain Costs, Incoterms, DG Class 9 Compliance, Battery Passports & EPR" if not is_hebrew else "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, Incoterms, רגולציה מלאה, חומ\"ס DG Class 9, דרכון סוללה ואחריות סביבתית",
    "scenario_header": "🗂️ Scenario, Incoterm & Market Forecast" if not is_hebrew else "🗂️ הגדרות תרחיש, תנאי סחר ותחזית שוק",
    "incoterm_label": "Commercial Incoterm (Supplier Scope):" if not is_hebrew else "תנאי סחר מסחרי (אחריות ספק):",
    "currency_label": "Dashboard Main Currency:" if not is_hebrew else "מטבע הצגה ראשי בדשבורד:",
    "tab1": "📋 Cargo & Destination" if not is_hebrew else "📋 פרטי מטען, יעד ומיקום",
    "tab2": "⚓ Supply Chain & Incoterms" if not is_hebrew else "⚓ שרשרת אספקה ותנאי סחר",
    "tab3": "📦 Storage & Site Drayage" if not is_hebrew else "📦 אחסנה, השהיות והובלת אתר",
    "tab4": "⚖️ DG Compliance, Customs & EoL Regulation" if not is_hebrew else "⚖️ רגולציית חומ\"ס DG, מכס, דרכון סוללה וסוף חיים",
    "tab5_eu": "🗺️ Illustrative Route Assumptions" if not is_hebrew else "🗺️ הנחות מסלולים אינדיקטיביות",
    "tab_summary": "📊 Financial & Regulatory Summary" if not is_hebrew else "📊 דוח בקרה פיננסית ורגולטורית",
    "cargo_type": "Cargo Type / Equipment:" if not is_hebrew else "סוג ציוד / מערכת אגירה:",
    "bess_capacity": "Total Project Capacity (MWh):" if not is_hebrew else "קיבולת אגירה כוללת לפרויקט (MWh):",
    "container_cnt": "Container Count:" if not is_hebrew else "כמות מכולות:",
    "system_cnt": "BESS System Count:" if not is_hebrew else "כמות מערכות BESS:",
    "exw_val": "EXW Equipment Value (USD):" if not is_hebrew else "ערך ציוד בבית המפעל בסין (EXW USD):",
    "origin_port": "Port of Loading:" if not is_hebrew else "נמל מוצא:",
    "dest_port": "Port of Discharge:" if not is_hebrew else "נמל יעד ימי (Port of Discharge):",
    "dest_country": "Final Project Country:" if not is_hebrew else "מדינת יעד סופית (אתר הפרויקט):",
    "site_address": "Project Site Name / Location:" if not is_hebrew else "שם / מיקום אתר הפרויקט:",
    "site_coords": "GPS Coordinates (Lat, Long):" if not is_hebrew else "קואורדינטות GPS (רוחב, אורך):",
    "site_zip": "Postal / Zip Code:" if not is_hebrew else "מיקוד / קוד דואר:",
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

REGULATORY_DATA_META = {
    "source": "Assumptions refreshed and embedded defaults (BloombergNEF aligned trends)" if not is_hebrew else "רענון הנחות עבודה מבוסס מגמות שוק ומדדי BNEF",
    "last_updated": "2026-09-14",
    "verification_required": True
}

VAT_RATES = {
    "Israel": 18.0, "Romania": 19.0, "Germany": 19.0, "Spain": 21.0, 
    "Italy": 22.0, "Greece": 24.0, "Poland": 23.0, "Other / Custom": 0.0
}

CUSTOMS_DUTIES = {
    "EU": {
        "BESS Container (UN3536 Class 9)": {"duty_pct": 2.7, "hs_code": "8507600000"},
        "Solar PV Modules": {"duty_pct": 0.0, "hs_code": "8541400000"},
        "Transformers / Heavy Equipment": {"duty_pct": 3.7, "hs_code": "8504230000"},
        "Inverters / MV Station / Power Skids": {"duty_pct": 0.0, "hs_code": "8504409000"},
        "E-House Units": {"duty_pct": 2.1, "hs_code": "8537200000"}
    },
    "Israel": {
        "BESS Container (UN3536 Class 9)": {"duty_pct": 0.0, "hs_code": "8507.60.00"},
        "Solar PV Modules": {"duty_pct": 0.0, "hs_code": "8541.40.00"},
        "Transformers / Heavy Equipment": {"duty_pct": 0.0, "hs_code": "8504.23.00"},
        "Inverters / MV Station / Power Skids": {"duty_pct": 0.0, "hs_code": "8504.40.90"},
        "E-House Units": {"duty_pct": 0.0, "hs_code": "8537.20.00"}
    }
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

# סרגל צד: תרחיש, מטבע ותחזית מחירים עתידית (Price Forecasting / BNEF Trend)
st.sidebar.subheader(T["scenario_header"])
incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)", "EXW (Ex Works)"])
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"])

price_trend_option = st.sidebar.selectbox(
    "Market Price Trend Horizon / BNEF Adjustment:" if not is_hebrew else "אופק תחזית מחירים בשוק / התאמת BNEF:",
    ["Current Spot (Base 0%)", "Q1/Q2 2027 (+3.5%)", "H2 2027 (+6.0%)", "2028 Long-term Outlook (+10.0%)", "Custom Adjustment %"]
)
if "Custom" in price_trend_option:
    trend_pct = st.sidebar.number_input("Custom Trend Adjustment (%):" if not is_hebrew else "התאמת מגמה מותאמת אישית (%):", value=0.0, step=0.5)
elif "+3.5%" in price_trend_option:
    trend_pct = 3.5
elif "+6.0%" in price_trend_option:
    trend_pct = 6.0
elif "+10.0%" in price_trend_option:
    trend_pct = 10.0
else:
    trend_pct = 0.0

trend_multiplier = 1.0 + (trend_pct / 100.0)

def fetch_live_exchange_rates():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=EUR,ILS", timeout=5)
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            return rates.get("EUR", 0.92), rates.get("ILS", 3.70)
    except Exception:
        pass
    return 0.92, 3.70

live_eur, live_ils = fetch_live_exchange_rates()
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

# =========================================================
# ממשק משתמש (לשוניות קלט)
# =========================================================
with tab1:
    st.subheader("Equipment Specification & Site Destination" if not is_hebrew else "מפרט ציוד, מאפייני פרויקט ומיקום אתר")
    col1, col2 = st.columns(2)
    
    with col1:
        # רשימה סגורה ומובנית לנמלי מוצא בסין
        origin_port = st.selectbox(
            T["origin_port"], 
            ["Shanghai", "Ningbo", "Shenzhen / Yantian", "Guangzhou / Nansha", "Qingdao", "Tianjin", "Xiamen"]
        )
        
        # רשימה סגורה ומובנית לנמלי יעד לפי מדינה (כולל הרחבה מדויקת לישראל)
        if dest_country == "Israel":
            dest_port_options = [
                "Haifa Port", 
                "Israel Shipyards Port", 
                "South Port (Ashdod)", 
                "Israel Petrochemical / Specialized Berths"
            ]
        elif dest_country == "Romania":
            dest_port_options = ["Constanța, Romania", "Burgas, Bulgaria (Transit to Romania)", "Hamburg / Rotterdam, North Europe"]
        elif dest_country == "Spain":
            dest_port_options = ["Valencia / Barcelona, Spain", "Burgas, Bulgaria (Transit)", "Hamburg / Rotterdam, North Europe"]
        elif dest_country == "Germany":
            dest_port_options = ["Hamburg / Bremerhaven, Germany", "Rotterdam, Netherlands"]
        elif dest_country == "Italy":
            dest_port_options = ["Genoa / Trieste, Italy", "Burgas, Bulgaria (Transit)"]
        elif dest_country == "Greece":
            dest_port_options = ["Piraeus / Thessaloniki, Greece"]
        elif dest_country == "Poland":
            dest_port_options = ["Gdansk / Gdynia, Poland", "Hamburg / Rotterdam, North Europe"]
        else:
            dest_port_options = ["Constanța, Romania", "Burgas, Bulgaria (Transit)", "Piraeus / Thessaloniki, Greece", "Hamburg / Rotterdam, North Europe"]
            
        dest_port = st.selectbox(T["dest_port"], dest_port_options)
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
        cargo_type = st.selectbox(T["cargo_type"], list(CUSTOMS_DUTIES["EU"].keys()))
        is_bess = (cargo_type == "BESS Container (UN3536 Class 9)")
        
        # הצגת קוד HS מותאם אישית ודינמי מיד עם בחירת הציוד
        region_key = "Israel" if dest_country == "Israel" else "EU"
        current_hs_data = CUSTOMS_DUTIES[region_key].get(cargo_type, {"duty_pct": 0.0, "hs_code": "N/A"})
        selected_hs_code = current_hs_data["hs_code"]
        default_duty_pct = current_hs_data["duty_pct"]
        st.caption(f"📌 **Selected Equipment HS Code:** {selected_hs_code} | **Indicative Duty:** {default_duty_pct}%" if not is_hebrew else f"📌 **קוד HS לציוד הנבחר:** {selected_hs_code} | **מכס אינדיקטיבי:** {default_duty_pct}%")

        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            system_count = st.number_input(T["system_cnt"], min_value=1, value=10, step=1)
        with sub_c2:
            container_count = st.number_input(T["container_cnt"], min_value=1, value=10, step=1)

        bess_mwh = st.number_input(T["bess_capacity"], value=40.0, step=5.0, min_value=0.1)
        
        if is_bess:
            weight_tier = st.selectbox("Weight Tier (MTS / Ton):" if not is_hebrew else "מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300)", "27.0 - 34.9 MTS ($12,600)", "35.0 - 44.9 MTS ($18,375)", "45.0 - 48.0 MTS ($21,000)"
            ], index=3)
            suggested_freight = 6300.0 if "Below 27" in weight_tier else (12600.0 if "27.0" in weight_tier else (18375.0 if "35.0" in weight_tier else 21000.0))
        else:
            suggested_freight = 3360.0

        un_number = st.selectbox("UN Number (Dangerous Goods Classification):" if not is_hebrew else "מספר UN (סיווג מטען מסוכן):", ["UN3536 (Cargo Transport Unit containing lithium ion batteries)", "UN3480 (Lithium ion batteries)", "UN3481 (Lithium ion batteries packed with equipment)", "Non-DG / Other"])
        is_dg = (un_number != "Non-DG / Other")

        exw_value_usd = st.number_input(T["exw_val"], value=500000.0, step=10000.0, min_value=0.0)

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
        
        customs_duty_pct = st.number_input("Indicative Import Customs Duty (%):" if not is_hebrew else "שיעור מכס אינדיקטיבי (%):", value=float(default_duty_pct), step=0.1, min_value=0.0, max_value=100.0)
        st.caption(f"Country: {dest_country} | Active HS Code: {selected_hs_code}")
        insurance_pct = st.number_input("Marine Cargo Insurance Rate (%):" if not is_hebrew else "שיעור ביטוח ימי (%):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.08), step=0.01, min_value=0.0, max_value=20.0)

with tab3:
    st.subheader("Port Demurrage, Storage & Inland Drayage" if not is_hebrew else "קנסות נמל, אחסנה חיצונית והובלה יבשתית לאתר")
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
    st.subheader("🛡️ DG Compliance & End-of-Life Regulation" if not is_hebrew else "🛡️ רגולציית חומ\"ס DG ותקנות סוף חיים (EoL)")
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown("### 📦 Dangerous Goods & Safety Permits")
        local_regulatory_permits = st.number_input("Hazardous Permits & DG Clearance ($):", value=1500.0 if is_dg else 400.0, step=100.0, min_value=0.0)

    with col_reg2:
        st.markdown("### ♻️ Battery Passport, EPR & End-of-Life (EoL)")
        
        if is_bess:
            include_epr = st.checkbox("Include EPR / Recycling cost", value=True)
            include_battery_passport = st.checkbox("Include Battery Passport / Carbon Audit cost", value=True)
            epr_basis = st.selectbox("EPR Calculation Basis", ["Per Container", "Per BESS System", "Per MWh", "Fixed Project Fee"])
            epr_fee_per_unit = st.number_input("EPR / Battery Recycling Unit Fee ($):", value=450.0, step=50.0, min_value=0.0, disabled=not include_epr)
            
            if epr_basis == "Per Container":
                calculated_epr_cost = epr_fee_per_unit * float(container_count)
            elif epr_basis == "Per BESS System":
                calculated_epr_cost = epr_fee_per_unit * float(system_count)
            elif epr_basis == "Per MWh":
                calculated_epr_cost = epr_fee_per_unit * float(bess_mwh)
            else:
                calculated_epr_cost = epr_fee_per_unit

            epr_recycling_total_usd = calculated_epr_cost if include_epr else 0.0
            battery_passport_fee = st.number_input("Battery Passport & Carbon Audit Fee ($):", value=1200.0, step=100.0, min_value=0.0, disabled=not include_battery_passport)
            battery_passport_total_usd = battery_passport_fee if include_battery_passport else 0.0
        else:
            st.info("ℹ️ Battery Passport & EPR regulations are automatically disabled for non-BESS equipment (e.g. Solar PV / Inverters)." if not is_hebrew else "ℹ️ רגולציות דרכון סוללה ו־EPR מנוטרלות אוטומטית עבור ציוד שאינו סוללות (כגון פאנלים סולאריים / ממירים).")
            epr_recycling_total_usd = 0.0
            battery_passport_total_usd = 0.0

    requires_heavy_lift = st.checkbox("Heavy-haul / abnormal-load handling required", value=is_bess)

# תחזית מחירים והחלת מקדם הטרנד (Trend Multiplier) על תשומות הלוגיסטיקה והציוד
trended_exw = exw_value_usd * trend_multiplier
trended_ocean_freight = ((base_freight_per_unit + baf_surcharge) * float(container_count)) * trend_multiplier
trended_drayage = (inland_drayage_per_unit * float(container_count)) * trend_multiplier

total_ocean_freight = trended_ocean_freight
inland_drayage_total_usd = trended_drayage

if show_route_optimization:
    with tab5:
        display_site = site_address if site_address else ("Unnamed Site" if not is_hebrew else "אתר ללא שם")
        st.subheader(f"🗺️ Illustrative Route & Port Comparison ({dest_country})")
        st.markdown(f"* **Ocean Freight (with trend):** ~${total_ocean_freight:,.0f}")
        st.markdown(f"* **Inland Drayage to {display_site}:** ~${inland_drayage_total_usd:,.0f}")

# =========================================================
# מנוע החישוב הפיננסי המלא
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

effective_delay_cost = (demurrage_total_usd + external_storage_total_usd) if include_delay_scenario else 0.0
project_delivery_cost = (
    ddp_supplier_scope_ex_vat + 
    (site_crane_unloading if include_site_crane else 0.0) + 
    local_regulatory_permits + 
    epr_recycling_total_usd + 
    battery_passport_total_usd + 
    (heavy_lift_survey if requires_heavy_lift else 0.0) + 
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
quote_variance_usd = 0.0

effective_vat_cash = 0.0 if vat_paid_by_supplier else vat_total_usd
recoverable_vat = vat_total_usd * (vat_recovery_pct / 100.0)
effective_non_recoverable_vat = 0.0 if vat_paid_by_supplier else (vat_total_usd - recoverable_vat)

buyer_supply_chain_total = project_delivery_cost
contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
economic_cost_ex_vat = total_landed_cost_ex_vat + effective_non_recoverable_vat
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + effective_vat_cash

total_kwh = bess_mwh * 1000.0 if (bess_mwh > 0 and is_bess) else 1.0
operational_logistics_only_usd = china_inland_drayage + china_origin_thc + total_ocean_freight + destination_thc_total + inland_drayage_total_usd
operational_logistics_kwh = operational_logistics_only_usd / total_kwh
regulatory_only_usd = local_regulatory_permits + battery_passport_total_usd + epr_recycling_total_usd
regulatory_kwh = regulatory_only_usd / total_kwh

display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_commercial_price, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
econ_val, _ = convert_from_usd(economic_cost_ex_vat, display_currency)
op_log_display, _ = convert_from_usd(operational_logistics_kwh, display_currency)
reg_kwh_display, _ = convert_from_usd(regulatory_kwh, display_currency)
vat_base_display, _ = convert_from_usd(indicative_vat_base_import_usd, display_currency)
modeled_supplier_display, _ = convert_from_usd(modeled_supplier_price, display_currency)

with tab_summary:
    st.subheader(f"📊 Financial & Regulatory Control Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Economic Cost", f"{curr_symbol} {econ_val:,.2f}")
    m3.metric("Total Project Cash Requirement", f"{curr_symbol} {cash_val:,.2f}")
    m4.metric("Supplier Commercial Price", f"{curr_symbol} {supplier_val:,.2f}")
    m5.metric("Operational Logistics / kWh", f"{curr_symbol} {op_log_display:.4f} /kWh")
    m6.metric("Regulatory / kWh", f"{curr_symbol} {reg_kwh_display:.4f} /kWh")

    st.markdown("---")
    st.info(f"📌 Regulatory & Trend status: {REGULATORY_DATA_META['source']} | Horizon: {price_trend_option} ({trend_pct:+.1f}%)")

    st.subheader("Detailed Cost Breakdown (USD Base)")
    cost_labels = [
        "Equipment Value (EXW + Trend)" if not is_hebrew else "ערך ציוד (כולל מגמת שוק)",
        "China Inland Transport & Export", "China Origin THC & Port Fees",
        f"Ocean Freight + BAF ({selected_carrier})", "Marine Cargo Insurance",
        "Indicative Import Customs Duty", "Destination THC & Wharfage",
        "Hazardous Permits & DG Clearance", "Battery Passport & Carbon Audit",
        "EPR / Battery Recycling Fee", "Port Demurrage Charges",
        "External Staging Yard Storage", "Inland Drayage (Port to Site)",
        "Site Crane & Pad Offloading", "Heavy Lift / Route Survey",
        "Project Risk Contingency", "Import VAT (Total)"
    ]
    amounts_no_vat = [
        trended_exw, china_inland_drayage, china_origin_thc, total_ocean_freight,
        insurance_total_usd, customs_duty_usd, destination_thc_total,
        local_regulatory_permits, battery_passport_total_usd, epr_recycling_total_usd,
        (demurrage_total_usd if include_delay_scenario else 0.0),
        (external_storage_total_usd if include_delay_scenario else 0.0),
        inland_drayage_total_usd, (site_crane_unloading if include_site_crane else 0.0),
        (heavy_lift_survey if requires_heavy_lift else 0.0), contingency_usd
    ]

    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": cost_labels,
        "Amount (USD)": amounts_no_vat + [vat_total_usd]
    })
    
    pct_list = [(amt / total_landed_cost_ex_vat) * 100.0 for amt in amounts_no_vat] + [0.0] if total_landed_cost_ex_vat > 0 else [0.0]*(len(amounts_no_vat)+1)
    df_summary["% of Landed Cost ex-VAT"] = [f"{p:.2f}%" for p in pct_list]
    
    st.dataframe(df_summary, use_container_width=True)
    
    csv_data = df_summary.to_csv(index=False).encode('utf-8-sig' if is_hebrew else 'utf-8')
    st.download_button(
        label="📥 Export Financial & Regulatory CSV Report" if not is_hebrew else "📥 ייצוא דוח פיננסי ורגולטורי ל-CSV",
        data=csv_data,
        file_name=f"BESS_Regulatory_Financial_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Renewable Energy Logistics & Landed Cost Calculator — Professional MVP Edition.")
