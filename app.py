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

# פונקציית עזר להמרת תמונה ל־Base64 לצורך הטמעה מדויקת ב־HTML
def get_base64_of_bin_file(bin_file):
    if not bin_file or not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_of_bin_file(logo_path) if logo_path else ""

# ---------------------------------------------------------
# סרגל צד: לוגו קטן למעלה, ואז מתג שפה
# ---------------------------------------------------------
if logo_base64:
    st.sidebar.markdown(
        f'<div style="text-align: center; margin-bottom: 1.5rem;"><img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: auto;" /></div>',
        unsafe_allow_html=True
    )

st.sidebar.header("🌐 Language / שפה")
lang = st.sidebar.radio("Select Language / בחר שפה:", ["Hebrew (עברית)", "English"], index=0)
is_hebrew = (lang == "Hebrew (עברית)")

# הזרקת CSS גלובלי ליישור לימין בעברית
if is_hebrew:
    st.markdown(
        """
        <style>
        .stApp {
            direction: rtl;
            text-align: right;
        }
        h1, h2, h3, h4, h5, h6, p, label, div {
            direction: rtl;
            text-align: right;
        }
        .stTextInput label, .stSelectbox label, .stNumberInput label {
            direction: rtl;
            text-align: right;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# מילון מונחים דו-לשוני מקיף
T = {
    "caption": "Professional MVP Project Cargo Calculator incorporating Supply Chain Costs, Incoterms, DG Class 9 Compliance, Battery Passports & EPR" if not is_hebrew else "מחשבון פרויקטלי מקצועי לניהול עלויות יעד, Incoterms, רגולציה מלאה, חומ\"ס DG Class 9, דרכון סוללה ואחריות סביבתית",
    "scenario_header": "🗂️ Scenario & Incoterm Setup" if not is_hebrew else "🗂️ הגדרות תרחיש ותנאי סחר (Incoterms)",
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

# הצגת כותרת ראשית גדולה ומרשימה בגוף העמוד בהתאם לכיוון השפה
logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" style="width: 140px; height: auto;" />' if logo_base64 else '⚡'

if is_hebrew:
    header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; direction: rtl; margin-bottom: 0rem;">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">Terra Vol</h1>
        <div>{logo_img_tag}</div>
    </div>
    """
else:
    header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; direction: ltr; margin-bottom: 0rem;">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">Terra Vol</h1>
        <div>{logo_img_tag}</div>
    </div>
    """

st.markdown(header_html, unsafe_allow_html=True)
st.caption(T["caption"])

# ---------------------------------------------------------
# נתונים ופרמטרים רגולטוריים (מטא-דאטה אינדיקטיבי)
# ---------------------------------------------------------
REGULATORY_DATA_META = {
    "source": "Assumptions refreshed and embedded defaults" if not is_hebrew else "רענון הנחות עבודה ונתוני ברירת מחדל משולבים",
    "last_updated": "2026-08-30",
    "verification_required": True
}

VAT_RATES = {
    "Israel": 18.0,
    "Romania": 19.0,
    "Germany": 19.0,
    "Spain": 21.0,
    "Italy": 22.0,
    "Greece": 24.0,
    "Poland": 23.0,
    "Other / Custom": 0.0
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

# ---------------------------------------------------------
# סרגל צד: תרחיש ומטבע המשך
# ---------------------------------------------------------
st.sidebar.subheader(T["scenario_header"])
incoterm = st.sidebar.selectbox(T["incoterm_label"], ["DDP (Delivered Duty Paid)", "CIF (Cost, Insurance & Freight)", "FOB (Free on Board)", "EXW (Ex Works)"])
display_currency = st.sidebar.selectbox(T["currency_label"], ["USD ($)", "EUR (€)", "ILS (₪)"])

# פונקציה לשליפת שערי חליפין מעודכנים מ־API חינמי
def fetch_live_exchange_rates():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=EUR,ILS", timeout=5)
        if response.status_code == 200:
            data = response.json()
            rates = data.get("rates", {})
            eur_rate = rates.get("EUR", 0.92)
            ils_rate = rates.get("ILS", 3.70)
            return eur_rate, ils_rate
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
        origin_port = st.selectbox(T["origin_port"], ["Shanghai", "Ningbo", "Shenzhen / Yantian", "Guangzhou / Nansha", "Custom Origin Port"])
        
        # התאמה דינמית של נמלי יעד לפי מדינת הפרויקט
        if dest_country == "Israel":
            dest_port_options = ["Haifa / Ashdod, Israel", "Custom Destination Port"]
        elif dest_country == "Romania":
            dest_port_options = ["Constanța, Romania", "Burgas, Bulgaria (Transit to Romania)", "Hamburg / Rotterdam, North Europe", "Custom Destination Port"]
        elif dest_country == "Spain":
            dest_port_options = ["Valencia / Barcelona, Spain", "Burgas, Bulgaria (Transit)", "Hamburg / Rotterdam, North Europe", "Custom Destination Port"]
        elif dest_country == "Germany":
            dest_port_options = ["Hamburg / Bremerhaven, Germany", "Rotterdam, Netherlands", "Custom Destination Port"]
        elif dest_country == "Italy":
            dest_port_options = ["Genoa / Trieste, Italy", "Burgas, Bulgaria (Transit)", "Custom Destination Port"]
        elif dest_country == "Greece":
            dest_port_options = ["Piraeus / Thessaloniki, Greece", "Custom Destination Port"]
        elif dest_country == "Poland":
            dest_port_options = ["Gdansk / Gdynia, Poland", "Hamburg / Rotterdam, North Europe", "Custom Destination Port"]
        else:
            dest_port_options = [
                "Constanța, Romania", 
                "Burgas, Bulgaria (Transit)", 
                "Piraeus / Thessaloniki, Greece", 
                "Hamburg / Rotterdam, North Europe", 
                "Custom Destination Port"
            ]
            
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
        if vat_paid_by_supplier and incoterm != "DDP (Delivered Duty Paid)":
            st.warning("VAT is marked as paid by the supplier under a non-DDP Incoterm. Verify the commercial agreement." if not is_hebrew else "המע״מ מסומן כמשולם על ידי הספק תחת תנאי סחר שאינם DDP. יש לוודא את ההסכם המסחרי.")

    with col2:
        cargo_type = st.selectbox(T["cargo_type"], list(CUSTOMS_DUTIES["EU"].keys()))
        
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            system_count = st.number_input(T["system_cnt"], min_value=1, value=10, step=1)
        with sub_c2:
            container_count = st.number_input(T["container_cnt"], min_value=1, value=10, step=1)

        if cargo_type == "BESS Container (UN3536 Class 9)" and system_count != container_count:
            st.warning("⚠️ System count differs from container count. Verify mapping." if not is_hebrew else "⚠️ מספר המערכות שונה ממספר המכולות. מומלץ לוודא את המיפוי.")

        bess_mwh = st.number_input(T["bess_capacity"], value=40.0, step=5.0, min_value=0.1)
        
        if container_count > 0 and system_count > 0:
            mwh_per_container = bess_mwh / container_count
            mwh_per_system = bess_mwh / system_count
            if mwh_per_container > 8.0:
                st.warning(f"⚠️ High capacity per container ({mwh_per_container:.2f} MWh)." if not is_hebrew else f"⚠️ קיבולת גבוהה יחסית למכולה ({mwh_per_container:.2f} MWh).")
            if mwh_per_container > 10.0:
                st.error("⚠️ Capacity per container appears unrealistic. Verify container count and project MWh." if not is_hebrew else "⚠️ קיבולת מכולה נראית לא ריאלית. יש לאמת את כמות המכולות וקיבולת הפרויקט.")
            if mwh_per_system > 8.0:
                st.warning(f"⚠️ High capacity per BESS system ({mwh_per_system:.2f} MWh)." if not is_hebrew else f"⚠️ קיבולת גבוהה יחסית למערכת אגירה ({mwh_per_system:.2f} MWh).")

        if cargo_type == "BESS Container (UN3536 Class 9)":
            weight_tier = st.selectbox("Weight Tier (MTS / Ton):" if not is_hebrew else "מדרגת משקל ליחידת BESS (MTS / Ton):", [
                "Below 27 MTS ($6,300)", "27.0 - 34.9 MTS ($12,600)", "35.0 - 44.9 MTS ($18,375)", "45.0 - 48.0 MTS ($21,000)"
            ], index=3)
            suggested_freight = 6300.0 if "Below 27" in weight_tier else (12600.0 if "27.0" in weight_tier else (18375.0 if "35.0" in weight_tier else 21000.0))
        else:
            suggested_freight = 3360.0

        un_number = st.selectbox("UN Number (Dangerous Goods Classification):" if not is_hebrew else "מספר UN (סיווג מטען מסוכן):", ["UN3536 (Cargo Transport Unit containing lithium ion batteries)", "UN3480 (Lithium ion batteries)", "UN3481 (Lithium ion batteries packed with equipment)", "Non-DG / Other"])
        
        is_dg = (un_number != "Non-DG / Other")
        if is_dg:
            if is_hebrew:
                msg = '<div dir="rtl" style="text-align: right;">⚠️ סיווג ה־UN הוא אינדיקטיבי בלבד. יש לאמת מול גיליון בטיחות חומרים (MSDS) ויועץ חומ״ס.</div>'
            else:
                msg = '⚠️ UN classification is indicative. Confirm with MSDS, dangerous-goods advisor and carrier.'
            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.info("ℹ️ DG-related permit costs remain user-controlled and are not automatically zeroed." if not is_hebrew else "ℹ️ עלויות היתרי חומ״ס נשארות בשליטת המשתמש ואינן מתאפסות אוטומטית.")
        
        if cargo_type == "BESS Container (UN3536 Class 9)" and not is_dg:
            st.error("BESS cargo is marked as Non-DG. Verify SDS and transport classification." if not is_hebrew else "מטען BESS מסומן כ־Non-DG. יש לאמת את גיליון הבטיחות וסיווג ההובלה.")
        elif cargo_type != "BESS Container (UN3536 Class 9)" and is_dg:
            st.warning("DG classification is enabled for non-BESS cargo. Verify the selected UN number." if not is_hebrew else "סיווג DG מופעל עבור מטען שאינו BESS. יש לוודא את מספר ה־UN שנבחר.")

        exw_value_usd = st.number_input(T["exw_val"], value=500000.0, step=10000.0, min_value=0.0)
        if exw_value_usd <= 0:
            st.warning("EXW equipment value is zero. Financial results may be incomplete." if not is_hebrew else "ערך ה־EXW הוא אפס. ייתכן שתוצאות החישוב אינן מלאות.")
        if container_count > 0:
            exw_value_per_container = exw_value_usd / float(container_count)
            if exw_value_per_container < 1000:
                st.warning("⚠️ EXW value per container appears unusually low. Verify pricing." if not is_hebrew else "⚠️ ערך ה־EXW למכולה נראה נמוך באופן חריג. יש לוודא את התמחור.")
            if exw_value_per_container > 1_000_000:
                st.warning("⚠️ EXW value per container appears unusually high. Verify pricing." if not is_hebrew else "⚠️ ערך ה־EXW למכולה נראה גבוה באופן חריג. יש לוודא את התמחור.")

with tab2:
    sub_title_html = (
        '<div dir="rtl" style="text-align: right; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">שרשרת אספקה מלאה והקצאת עלויות לפי Incoterms</div>'
        if is_hebrew
        else '<div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Full Supply Chain & Incoterms Allocation</div>'
    )
    st.markdown(sub_title_html, unsafe_allow_html=True)
    
    info_msg = (
        f'<div dir="rtl" style="text-align: right;">💡 תנאי הסחר המסחרי: <b>{incoterm}</b>. מגדיר את היקף מחיר הספק.</div>'
        if is_hebrew
        else f'💡 Current commercial Incoterm: <b>{incoterm}</b>. Defines seller\'s price scope.'
    )
    st.markdown(info_msg, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        selected_carrier = st.selectbox("Shipping Carrier:" if not is_hebrew else "חברת ספנות מובילה:", list(CARRIER_FUEL_SURCHARGES.keys()), index=0)
        base_freight_per_unit = st.number_input("Base Ocean Freight per Container ($):" if not is_hebrew else "מחיר הובלה ימית בסיס ליחידה ($):", value=float(suggested_freight), step=500.0, min_value=0.0)
        
        baf_included = st.checkbox(
            "Bunker Surcharge (BAF) included in Base Ocean Freight" if not is_hebrew else "תוספת דלק (BAF) כלולה כבר במחיר ההובלה הימית הבסיסי",
            value=False
        )
        active_baf = 0.0 if baf_included else float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"])
        
        baf_surcharge = st.number_input(f"Bunker Surcharge ({CARRIER_FUEL_SURCHARGES[selected_carrier]['code']}) ($):", value=active_baf, step=50.0, min_value=0.0)
        dest_thc_port_fee = st.number_input("Destination THC / Port Fee per Container ($):" if not is_hebrew else "אגרות ותעריפי נמל יעד (Destination THC / Wharfage) ליחידה ($):", value=380.0, step=20.0, min_value=0.0)
        
    with col_b:
        china_inland_drayage = st.number_input("China Inland Transport + Export Customs ($):" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא (USD סה\"כ):", value=2200.0, step=300.0, min_value=0.0)
        china_origin_thc = st.number_input("China Origin THC & Port Fees ($):" if not is_hebrew else "אגרות ותעריפי נמל מוצא בסין (Origin THC סה\"כ):", value=1300.0, step=200.0, min_value=0.0)
        heavy_lift_survey = st.number_input("Heavy Lift / Route Survey ($):" if not is_hebrew else "סקר הנדסי / היטל הובלה חריגה פרויקטלית ($ סה\"כ):", value=2500.0, step=500.0, min_value=0.0)
        
        region_key = "Israel" if dest_country == "Israel" else "EU"
        customs_duty_pct = st.number_input("Indicative Import Customs Duty (%):" if not is_hebrew else "שיעור מכס אינדיקטיבי (%):", value=float(CUSTOMS_DUTIES[region_key][cargo_type]["duty_pct"]), step=0.1, min_value=0.0, max_value=100.0)
        
        selected_hs_code = CUSTOMS_DUTIES[region_key][cargo_type]["hs_code"]
        st.caption(f"Country: {dest_country} | Indicative HS Code: {selected_hs_code} | Last updated: {REGULATORY_DATA_META['last_updated']}" if not is_hebrew else f"מדינה: {dest_country} | קוד HS אינדיקטיבי: {selected_hs_code} | עודכן לאחרונה: {REGULATORY_DATA_META['last_updated']}")

        insurance_pct = st.number_input("Marine Cargo Insurance Rate (% — enter 0.08 for 0.08%):" if not is_hebrew else "שיעור ביטוח ימי (% — הזן 0.08 עבור 0.08%):", value=DEFAULT_INSURANCE_RATES.get(dest_country, 0.08), step=0.01, min_value=0.0, max_value=20.0)
        if insurance_pct > 5:
            st.warning("⚠️ שיעור הביטוח נראה גבוה באופן חריג. יש לוודא את יחידות האחוז." if is_hebrew else "⚠️ Insurance rate appears unusually high. Verify percentage units.")

    supplier_quote_available = st.checkbox("Enter actual supplier commercial quote" if not is_hebrew else "הזן הצעת מחיר מסחרית אמיתית מהספק", value=False)
    if supplier_quote_available:
        supplier_quoted_price = st.number_input("Supplier Quoted Price under Selected Incoterm (USD):" if not is_hebrew else "מחיר ספק מוצע תחת תנאי הסחר הנבחר (USD):", min_value=0.0, value=exw_value_usd)
        st.info("💡 **Supplier Quote Benchmark — not netted against project cost:** Displayed as a benchmark only. Verify which scope components are included or excluded." if not is_hebrew else "💡 **בנצ'מרק הצעת ספק — אינה מופחתת מעלות הפרויקט:** מוצג להשוואה בלבד. יש לאמת אילו רכיבי Scope כלולים ואילו מוחרגים.")

with tab3:
    st.subheader("Port Demurrage, Storage & Inland Drayage" if not is_hebrew else "קנסות נמל, אחסנה חיצונית והובלה יבשתית לאתר")
    col_x, col_y = st.columns(2)
    with col_x:
        free_days = st.number_input("Port Free Days:" if not is_hebrew else "ימים חופשיים בנמל (Free Days):", value=DEFAULT_FREE_DAYS.get(dest_country, 7), step=1, min_value=0)
        actual_port_days = st.number_input("Actual Port Dwell Days:" if not is_hebrew else "ימי אחסנה בפועל בנמל:", value=12, step=1, min_value=0)
        demurrage_daily_rate = st.number_input("Daily Demurrage Rate per DG Container ($):" if not is_hebrew else "קנס השהיה יומי ממוצע למכולת חומ\"ס ($):", value=250.0 if is_dg else 150.0, step=10.0, min_value=0.0)
        
    with col_y:
        use_external_storage = st.checkbox("External Staging Yard" if not is_hebrew else "שימוש בחצר אחסנה חיצונית / שטח היערכות", value=True)
        ext_storage_days = st.number_input("External Storage Days:" if not is_hebrew else "ימי אחסנה בפועל בחצר החיצונית:", value=15, step=1, min_value=0)
        ext_storage_daily_rate = st.number_input("External Storage Daily Rate ($):" if not is_hebrew else "עלות אחסנה יומית בחצר החיצונית למכולה ($):", value=65.0 if is_dg else 45.0, step=5.0, min_value=0.0)
        
        default_drayage = 1850.0 if "Burgas" in dest_port else 600.0
        inland_drayage_per_unit = st.number_input("Inland Drayage from Port to Site ($ per container):" if not is_hebrew else "הובלה יבשתית מהנמל לאתר הפרויקט ($ למכולה):", value=default_drayage, step=50.0, min_value=0.0)

    st.markdown("---")
    col_ddp1, col_ddp2 = st.columns(2)
    with col_ddp1:
        include_site_crane = st.checkbox("Include site crane and pad offloading" if not is_hebrew else "כלול מנוף פריקה והצבה באתר", value=True)
        site_crane_unloading = st.number_input("Site Crane & Pad Offloading ($):" if not is_hebrew else "מנוף פריקה כבד באתר + הצבה ($ סה\"כ):", value=8500.0, step=500.0, min_value=0.0, disabled=not include_site_crane)
    with col_ddp2:
        ddp_contingency_pct = st.number_input("Project Risk Contingency (%):" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי (%):", value=5.0, step=1.0, min_value=0.0, max_value=100.0)
        include_delay_scenario = st.checkbox("Include demurrage and external storage in project cost" if not is_hebrew else "כלול קנסות השהיה ואחסנה חיצונית בעלות הפרויקט", value=False)

with tab4:
    st.subheader("🛡️ DG Compliance, Battery Passports & End-of-Life Regulation" if not is_hebrew else "🛡️ רגולציית חומ\"ס DG, דרכון סוללה ותקנות סוף חיים (EoL)")
    
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.markdown("### 📦 Dangerous Goods & Safety Permits" if not is_hebrew else "### 📦 מטענים מסוכנים והיתרי בטיחות")
        if dest_country == "Israel":
            st.info("💡 **Israel Regulatory Requirements (Indicative):** Import of BESS may require a Ministry of Environmental Protection Poisons Permit, Fire & Rescue Authority safety approval. Verify with a licensed customs broker." if not is_hebrew else "💡 **דרישות רגולטוריות בישראל (אינדיקטיבי):** יבוא BESS עשוי לדרוש היתר רעלים ואישור כיבוי אש. יש לאמת מול עמיל מכס.")
        else:
            st.info("💡 **EU Battery Regulation Compliance (Indicative):** Shipments into the EU may require adherence to the EU Battery Regulation. Verify with a licensed customs broker." if not is_hebrew else "💡 **ציות לרגולציית הסוללות באיחוד (אינדיקטיבי):** משלוחים לאירופה עשויים לחייב עמידה ברגולציית הסוללות. יש לאמת מול עמיל מכס.")

        local_regulatory_permits = st.number_input("Hazardous Permits & DG Clearance ($):" if not is_hebrew else "אישורי חומ\"ס, היתר רעלים ואישורי כיבוי ($ סה\"כ):", value=1500.0 if is_dg else 400.0, step=100.0, min_value=0.0)

    with col_reg2:
        st.markdown("### ♻️ Battery Passport, EPR & End-of-Life (EoL)" if not is_hebrew else "### ♻️ דרכון סוללה, EPR וסוף חיים (EoL)")
        
        include_epr = st.checkbox("Include EPR / Recycling cost" if not is_hebrew else "כלול עלות EPR / מיחזור", value=True)
        include_battery_passport = st.checkbox("Include Battery Passport / Carbon Audit cost" if not is_hebrew else "כלול עלות דרכון סוללה / ביקורת פחמן", value=True)
        
        if include_battery_passport and cargo_type != "BESS Container (UN3536 Class 9)":
            st.warning("⚠️ Battery Passport cost is enabled for non-BESS cargo. Verify applicability." if not is_hebrew else "⚠️ עלות דרכון סוללה מופעלת עבור מטען שאינו BESS. יש לוודא תחולה.")

        epr_basis = st.selectbox(
            "EPR Calculation Basis" if not is_hebrew else "בסיס חישוב EPR",
            ["Per Container", "Per BESS System", "Per MWh", "Fixed Project Fee"]
        )

        epr_applicable = (cargo_type == "BESS Container (UN3536 Class 9)")
        force_epr_for_non_bess = False
        if cargo_type != "BESS Container (UN3536 Class 9)" and include_epr:
            force_epr_for_non_bess = st.checkbox("Apply EPR manually to non-BESS cargo" if not is_hebrew else "החל EPR ידנית למטען שאינו BESS", value=False)
            if not force_epr_for_non_bess:
                st.warning("⚠️ EPR cost was excluded because applicability for this cargo type has not been confirmed." if not is_hebrew else "⚠️ עלות ה־EPR לא נכללה משום שהתחולה עבור סוג מטען זה לא אושרה.")
        
        epr_fee_per_unit = st.number_input("EPR / Battery Recycling Unit Fee ($):" if not is_hebrew else "אגרת מיחזור סוללות / EPR ליחידת בסיס ($):", value=450.0 if "BESS" in cargo_type else 80.0, step=50.0, min_value=0.0, disabled=not include_epr)
        
        if epr_basis == "Per Container":
            calculated_epr_cost = epr_fee_per_unit * float(container_count)
        elif epr_basis == "Per BESS System":
            calculated_epr_cost = epr_fee_per_unit * float(system_count)
        elif epr_basis == "Per MWh":
            calculated_epr_cost = epr_fee_per_unit * float(bess_mwh)
        else:
            calculated_epr_cost = epr_fee_per_unit

        if include_epr and (epr_applicable or force_epr_for_non_bess):
            epr_recycling_total_usd = calculated_epr_cost
        else:
            epr_recycling_total_usd = 0.0

        battery_passport_fee = st.number_input("Battery Passport & Carbon Audit Fee ($):" if not is_hebrew else "עלות הפקת דרכון סוללה ובדיקת טביעת רגל פחמנית ($ סה\"כ):", value=1200.0 if "BESS" in cargo_type else 200.0, step=100.0, min_value=0.0, disabled=not include_battery_passport)
        battery_passport_total_usd = battery_passport_fee if include_battery_passport else 0.0

    requires_heavy_lift = st.checkbox("Heavy-haul / abnormal-load handling required" if not is_hebrew else "נדרשת הובלה חריגה / מטען כבד", value=(cargo_type == "BESS Container (UN3536 Class 9)"))
    if requires_heavy_lift and cargo_type != "BESS Container (UN3536 Class 9)":
        st.info("ℹ️ Heavy-haul is enabled for non-BESS cargo. Confirm that this is intentional." if not is_hebrew else "ℹ️ הובלה חריגה מופעלת עבור מטען שאינו BESS. יש לאמת שזו הכוונה.")

# ---------------------------------------------------------
# הגדרה מוקדמת של חישובים בסיסיים למניעת NameError ב־Tab 5
# ---------------------------------------------------------
total_ocean_freight = (base_freight_per_unit + baf_surcharge) * float(container_count)
inland_drayage_total_usd = inland_drayage_per_unit * float(container_count)

if show_route_optimization:
    with tab5:
        display_site = site_address if site_address else ("Unnamed Site" if not is_hebrew else "אתר ללא שם")
        st.subheader(f"🗺️ Illustrative Route & Port Comparison ({dest_country})" if not is_hebrew else f"🗺️ הנחות מסלולים והשוואת נמלים אינדיקטיבית ({dest_country})")
        st.warning("⚠️ This tab is illustrative only. Route-specific freight, transit time, port fees and customs costs are not separately modeled." if not is_hebrew else "⚠️ לשונית זו היא אינדיקטיבית בלבד. עלויות הובלה, זמן מעבר, אגרות נמל ועלויות מכס אינן מחושבות בנפרד לכל מסלול.")
        st.caption(f"Route comparison assumptions for site: {display_site} in {dest_country} (Note: Values reflect current scenario inputs)" if not is_hebrew else f"הנחות השוואת מסלולים לאתר הפרויקט: {display_site} ב־{dest_country} (הערה: הערכים משקפים את קלטי התרחיש הנוכחיים)")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if dest_country == "Romania":
                r1_title = "🇧🇬 Route A: via Burgas Port (Bulgaria)"
                r1_adv = "Fast DG Class 9 port clearance" if not is_hebrew else "שחרור מהיר מטעני חומ״ס DG Class 9"
            elif dest_country == "Spain":
                r1_title = "🇪🇸 Route A: via Mediterranean Ports (Valencia / Barcelona)"
                r1_adv = "Direct maritime access to southern and central Spain" if not is_hebrew else "גישה ימית ישירה לדרום ולמרכז ספרד"
            elif dest_country == "Germany":
                r1_title = "🇩🇪 Route A: via Hamburg / Bremerhaven"
                r1_adv = "Direct deep-sea container discharge" if not is_hebrew else "פריקת מכולות ישירה בנמלי הים הצפוני"
            else:
                r1_title = f"⚓ Route A: Primary Port Entry ({dest_country})"
                r1_adv = "Standard regional import gateway" if not is_hebrew else "שער יבוא אזורי סטנדרטי"

            st.markdown(f"### {r1_title}")
            st.markdown(f"* **Ocean Freight:** ~${total_ocean_freight:,.0f}")
            st.markdown(f"* **Inland Drayage to {display_site}:** ~${inland_drayage_total_usd:,.0f}")
            st.markdown(f"* **Key Advantage:** {r1_adv}")

        with col_r2:
            if dest_country == "Romania":
                r2_title = "🇷🇴 Route B: via Constanța Port (Romania)"
                r2_adv = "Direct discharge in destination country" if not is_hebrew else "פריקה ישירה במדינת היעד"
            elif dest_country == "Spain":
                r2_title = "🇪🇸 Route B: via Northern Ports (Bilbao / Alternative)"
                r2_adv = "Alternative gateway for northern project sites" if not is_hebrew else "שער חלופי עבור אתרי פרויקט בצפון המדינה"
            elif dest_country == "Germany":
                r2_title = "🇩🇪 Route B: via Rotterdam (Netherlands) Transit"
                r2_adv = "Alternative multimodal barge / rail connection" if not is_hebrew else "חיבור מולטימודלי חלופי ברכבת או ברג'ים"
            else:
                r2_title = f"⚓ Route B: Alternative Gateway"
                r2_adv = "Alternative regional routing option" if not is_hebrew else "אפשרות ניתוב אזורית חלופית"

            st.markdown(f"### {r2_title}")
            st.markdown(f"* **Ocean Freight:** ~${total_ocean_freight:,.0f}")
            st.markdown(f"* **Inland Drayage to {display_site}:** ~${inland_drayage_total_usd:,.0f}")
            st.markdown(f"* **Key Advantage:** {r2_adv}")

# =========================================================
# מנוע החישוב הפיננסי המלא (כולל התאמות מע״מ ו־DDP מוקדם)
# =========================================================
cif_valuation_base = exw_value_usd + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)
destination_thc_total = dest_thc_port_fee * float(container_count)

# חישוב בסיס מע״מ ומע״מ לצורך שילוב נכון במחיר הספק DDP ובזרימה הפיננסית
indicative_vat_base_import_usd = customs_valuation_base_usd + customs_duty_usd + destination_thc_total
vat_total_usd = indicative_vat_base_import_usd * (applied_vat / 100.0)

supplier_vat_component = (
    vat_total_usd
    if vat_paid_by_supplier and incoterm == "DDP (Delivered Duty Paid)"
    else 0.0
)

ddp_supplier_scope_ex_vat = (
    exw_value_usd
    + china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + insurance_total_usd
    + customs_duty_usd
    + destination_thc_total
    + inland_drayage_total_usd
)

ddp_supplier_scope_incl_vat = ddp_supplier_scope_ex_vat + supplier_vat_component

overdue_days = max(0, actual_port_days - free_days)
demurrage_total_usd = float(overdue_days) * demurrage_daily_rate * float(container_count)
external_storage_total_usd = (float(ext_storage_days) * ext_storage_daily_rate * float(container_count)) if use_external_storage else 0.0

effective_demurrage_total_usd = demurrage_total_usd if include_delay_scenario else 0.0
effective_external_storage_total_usd = external_storage_total_usd if include_delay_scenario else 0.0
effective_delay_cost = effective_demurrage_total_usd + effective_external_storage_total_usd

regulatory_permits_total_usd = local_regulatory_permits
effective_site_crane = site_crane_unloading if include_site_crane else 0.0
effective_heavy_lift = heavy_lift_survey if requires_heavy_lift else 0.0

project_delivery_cost = (
    ddp_supplier_scope_ex_vat
    + effective_site_crane
    + regulatory_permits_total_usd
    + epr_recycling_total_usd
    + battery_passport_total_usd
    + effective_heavy_lift
    + effective_delay_cost
)

supplier_commercial_price_options = {
    "EXW (Ex Works)": exw_value_usd,
    "FOB (Free on Board)": (
        exw_value_usd
        + china_inland_drayage
        + china_origin_thc
    ),
    "CIF (Cost, Insurance & Freight)": (
        exw_value_usd
        + china_inland_drayage
        + china_origin_thc
        + total_ocean_freight
        + insurance_total_usd
    ),
    "DDP (Delivered Duty Paid)": ddp_supplier_scope_incl_vat
}

modeled_supplier_price = supplier_commercial_price_options.get(
    incoterm,
    exw_value_usd
)

if supplier_quote_available:
    supplier_commercial_price = supplier_quoted_price
    quote_variance_usd = supplier_quoted_price - modeled_supplier_price
else:
    supplier_commercial_price = modeled_supplier_price
    quote_variance_usd = 0.0

effective_vat_cash = 0.0 if vat_paid_by_supplier else vat_total_usd
recoverable_vat = vat_total_usd * (vat_recovery_pct / 100.0)
non_recoverable_vat = vat_total_usd - recoverable_vat
effective_non_recoverable_vat = 0.0 if vat_paid_by_supplier else non_recoverable_vat

buyer_supply_chain_total = project_delivery_cost
contingency_usd = buyer_supply_chain_total * (ddp_contingency_pct / 100.0)
total_landed_cost_ex_vat = buyer_supply_chain_total + contingency_usd
economic_cost_ex_vat = total_landed_cost_ex_vat + effective_non_recoverable_vat
total_cash_requirement_incl_vat = total_landed_cost_ex_vat + effective_vat_cash

total_kwh = bess_mwh * 1000.0 if bess_mwh > 0 else 1.0
operational_logistics_only_usd = (
    china_inland_drayage
    + china_origin_thc
    + total_ocean_freight
    + destination_thc_total
    + inland_drayage_total_usd
    + effective_site_crane
    + effective_heavy_lift
)
regulatory_only_usd = (
    regulatory_permits_total_usd
    + battery_passport_total_usd
    + epr_recycling_total_usd
)

operational_logistics_kwh = operational_logistics_only_usd / total_kwh
regulatory_kwh = regulatory_only_usd / total_kwh

# המרות מטבע לתצוגה
display_val, curr_symbol = convert_from_usd(total_landed_cost_ex_vat, display_currency)
supplier_val, _ = convert_from_usd(supplier_commercial_price, display_currency)
cash_val, _ = convert_from_usd(total_cash_requirement_incl_vat, display_currency)
econ_val, _ = convert_from_usd(economic_cost_ex_vat, display_currency)
op_log_display, _ = convert_from_usd(operational_logistics_kwh, display_currency)
reg_kwh_display, _ = convert_from_usd(regulatory_kwh, display_currency)
vat_base_display, _ = convert_from_usd(indicative_vat_base_import_usd, display_currency)

if supplier_quote_available:
    quote_variance_display, _ = convert_from_usd(quote_variance_usd, display_currency)
modeled_supplier_display, _ = convert_from_usd(modeled_supplier_price, display_currency)

if supplier_quote_available and supplier_quoted_price < exw_value_usd:
    st.warning("Supplier quote is below the modeled EXW equipment value. Verify currency, quantity and quote scope." if not is_hebrew else "הצעת הספק נמוכה מערך ה־EXW המחושב. יש לוודא מטבע, כמות והיקף ההצעה.")

# ----- דוח סיכום ובקרה (Tab Summary) -----
with tab_summary:
    st.subheader(f"📊 Financial & Regulatory Control Dashboard - {incoterm} ({display_currency})")
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Economic Cost", f"{curr_symbol} {econ_val:,.2f}", help="Includes non-recoverable VAT unless paid by supplier")
    m3.metric(
        "Total Project Cash Requirement", 
        f"{curr_symbol} {cash_val:,.2f}", 
        help="Includes import VAT cash requirement unless VAT is paid by the supplier." if not is_hebrew else "כולל את תזרים מע״מ היבוא, אלא אם המע״מ משולם על ידי הספק."
    )
    m4.metric("Supplier Commercial Price", f"{curr_symbol} {supplier_val:,.2f}", help="Commercial supplier scope under selected Incoterm")
    m5.metric("Operational Logistics / kWh", f"{curr_symbol} {op_log_display:.4f} /kWh", help="Includes planned logistics, site crane and heavy-haul. Excludes demurrage, external storage, equipment, customs, insurance and contingency")
    m6.metric("Regulatory / kWh", f"{curr_symbol} {reg_kwh_display:.4f} /kWh")
    
    if supplier_quote_available:
        q1, q2, q3 = st.columns(3)
        q1.metric(
            "Supplier Quote Variance",
            f"{curr_symbol} {quote_variance_display:,.2f}",
            help="Difference between supplier quote and modeled price under the selected Incoterm"
        )
        q2.metric(
            "Modeled Supplier Price",
            f"{curr_symbol} {modeled_supplier_display:,.2f}"
        )
        q3.metric(
            "Quoted Incoterm",
            incoterm.split(" ")[0]
        )

    st.markdown("---")
    st.info(f"📌 Regulatory data status: {REGULATORY_DATA_META['source']} | Last updated: {REGULATORY_DATA_META['last_updated']} | Broker verification required: {REGULATORY_DATA_META['verification_required']}" if not is_hebrew else f"📌 סטטוס נתונים רגולטוריים: {REGULATORY_DATA_META['source']} | עודכן לאחרונה: {REGULATORY_DATA_META['last_updated']} | נדרשת בדיקת עמיל מכס: כן")
    st.caption(f"Indicative VAT base: ${indicative_vat_base_import_usd:,.2f} ({curr_symbol} {vat_base_display:,.2f}). Confirm inclusions with the local customs broker." if not is_hebrew else f"בסיס מע\"מ אינדיקטיבי: ${indicative_vat_base_import_usd:,.2f} ({curr_symbol} {vat_base_display:,.2f}). יש לאמת רכיבים כלולים מול עמיל מכס מורשה.")

    st.subheader("Detailed Cost Breakdown (USD Base)" if not is_hebrew else "פילוח עלויות מפורט (USD Base)")
    
    cost_labels = [
        "Equipment Value (EXW)" if not is_hebrew else "ערך ציוד (EXW)",
        "China Inland Transport & Export" if not is_hebrew else "הובלה פנימית בסין + עמילות יצוא",
        "China Origin THC & Port Fees" if not is_hebrew else "אגרות נמל מוצא בסין (Origin THC)",
        f"Ocean Freight + BAF ({selected_carrier})" if not is_hebrew else f"הובלה ימית + BAF ({selected_carrier})",
        "Marine Cargo Insurance" if not is_hebrew else "ביטוח ימי למטען",
        "Indicative Import Customs Duty" if not is_hebrew else "מכס יבוא אינדיקטיבי",
        "Destination THC & Wharfage" if not is_hebrew else "אגרות נמל יעד (Dest THC)",
        "Hazardous Permits & DG Clearance" if not is_hebrew else "אישורי חומ\"ס והיתר רעלים",
        "Battery Passport & Carbon Audit" if not is_hebrew else "דרכון סוללה ובדיקת פחמן",
        "EPR / Battery Recycling Fee" if not is_hebrew else "אגרת מיחזור סוללות / EPR",
        "Port Demurrage Charges" if not is_hebrew else "קנסות השהיה בנמל (Demurrage)",
        "External Staging Yard Storage" if not is_hebrew else "אחסנה חיצונית בחצר היערכות",
        "Inland Drayage (Port to Site)" if not is_hebrew else "הובלה יבשתית (מהנמל לאתר)",
        "Site Crane & Pad Offloading" if not is_hebrew else "מנוף פריקה והצבה באתר",
        "Heavy Lift / Route Survey" if not is_hebrew else "סקר הנדסי והובלה חריגה",
        "Project Risk Contingency" if not is_hebrew else "מקדם סיכון ובלתי מתוכנן פרויקטלי",
        "Import VAT (Total)" if not is_hebrew else "מע\"מ יבוא (סך הכל)"
    ]
    
    amounts_no_vat = [
        exw_value_usd, china_inland_drayage, china_origin_thc, 
        total_ocean_freight, insurance_total_usd, customs_duty_usd, 
        destination_thc_total, regulatory_permits_total_usd, battery_passport_total_usd,
        epr_recycling_total_usd, effective_demurrage_total_usd, effective_external_storage_total_usd, 
        inland_drayage_total_usd, effective_site_crane, effective_heavy_lift, contingency_usd
    ]
    
    # בקרת התאמה (Reconciliation Check) מלאה
    sum_amounts = sum(amounts_no_vat)
    reconciliation_difference = sum_amounts - total_landed_cost_ex_vat
    if abs(reconciliation_difference) > 0.1:
        st.error(
            (
                f"⚠️ Cost breakdown reconciliation warning: sum of components (${sum_amounts:,.2f}) differs from total landed cost (${total_landed_cost_ex_vat:,.2f})."
            )
            if not is_hebrew
            else
            (
                f"⚠️ נמצאה אי־התאמה בפירוט העלויות: סכום הרכיבים (${sum_amounts:,.2f}) שונה מעלות ה־Landed Cost הכוללת (${total_landed_cost_ex_vat:,.2f})."
            )
        )
    else:
        st.success(
            "✅ Cost breakdown reconciles with total landed cost."
            if not is_hebrew
            else
            "✅ פירוט העלויות תואם במלואו את עלות ה־Landed Cost הכוללת."
        )

    df_summary = pd.DataFrame({
        "Cost Component" if not is_hebrew else "רכיב עלות": cost_labels,
        "Amount (USD)": amounts_no_vat + [vat_total_usd]
    })
    
    if total_landed_cost_ex_vat > 0:
        pct_list = [
            (amt / total_landed_cost_ex_vat) * 100.0
            for amt in amounts_no_vat
        ] + [0.0]
    else:
        pct_list = [0.0] * (len(amounts_no_vat) + 1)

    df_summary["% of Landed Cost ex-VAT"] = [f"{p:.2f}%" for p in pct_list]
    
    st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    
    if is_hebrew:
        csv_data = df_summary.to_csv(index=False).encode('utf-8-sig')
    else:
        csv_data = df_summary.to_csv(index=False).encode('utf-8')
        
    st.download_button(
        label="📥 Export Financial & Regulatory CSV Report" if not is_hebrew else "📥 ייצוא דוח פיננסי ורגולטורי ל-CSV",
        data=csv_data,
        file_name=f"BESS_Regulatory_Financial_Report_{incoterm.split(' ')[0]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Renewable Energy Logistics & Landed Cost Calculator — Professional MVP Edition.")
