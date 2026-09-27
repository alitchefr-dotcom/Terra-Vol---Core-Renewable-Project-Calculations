import streamlit as st
import pandas as pd
import os
import requests
import base64
from datetime import date

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
    "tab1": "📋 Multi-Item Project Scope" if not is_hebrew else "📋 תמהיל רכיבי הפרויקט (Multi-Item)",
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
EUROPE_TRUCK_RATES_CPK = {
    "Germany": {"dry": 2.45, "dg_heavy": 3.20},
    "Poland": {"dry": 1.85, "dg_heavy": 2.40},
    "Romania": {"dry": 1.95, "dg_heavy": 2.55},
    "Other / Custom": {"dry": 2.20, "dg_heavy": 2.90}
}
DRAYAGE_PORT_MATRIX = {"Hamburg, Germany": 950.0, "Gdansk, Poland": 750.0, "Constanța, Romania": 900.0}
CARRIER_FUEL_SURCHARGES = {
    "ZIM (Integrated Shipping)": {"baf": 843.0},
    "Hapag-Lloyd": {"baf": 780.0},
    "MSC": {"baf": 750.0}
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
show_route_optimization = (dest_country != "Israel")

if show_route_optimization:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab5_eu"], T["tab_projects"], T["tab_summary"]])
    tab_summary = tab7
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"], T["tab_projects"], T["tab_summary"]])
    tab_summary = tab6

with tab1:
    st.subheader("Multi-Item Project Bill of Materials (BoM)" if not is_hebrew else "תמהיל רכיבי הציוד לפרויקט (Multi-Item BoM)")
    st.info("כעת ניתן להגדיר את כל סוגי המוצרים בפרויקט במקביל, כולל מכולות אביזרים וציוד כללי (Accessories / Dry Containers).")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        origin_port = st.selectbox(T["origin_port"], ORIGIN_PORTS, key="tab1_origin_port")
        available_dest_ports = DESTINATION_PORTS.get(dest_country, DESTINATION_PORTS["Other / Custom"])
        dest_port = st.selectbox(T["dest_port"], available_dest_ports, key=f"tab1_dest_port_{dest_country}")
        site_address = st.text_input("Project Site Name", key="site_name_input", placeholder="e.g. Iepurești")

    with col_meta2:
        applied_vat = st.number_input(f"VAT Rate ({dest_country}) %:", value=float(VAT_RATES[dest_country]), step=0.5, min_value=0.0, max_value=100.0, key=f"tab1_vat_{dest_country}")
        vat_recovery_pct = st.number_input("VAT Recoverability (%)", value=100.0, min_value=0.0, max_value=100.0, step=1.0, key="tab1_vat_rec")
        vat_paid_by_supplier = st.checkbox("VAT paid by supplier under commercial arrangement", value=False, key="tab1_vat_supplier")

    st.markdown("---")
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("#### BESS & OOG Containers")
        bess_count = st.number_input("BESS Containers Count:", min_value=0, value=20, step=1, key="proj_bess_count")
        bess_exw = st.number_input("BESS Unit EXW ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_bess_exw")
        bess_freight_unit = 31850.0

        oog_count = st.number_input("OOG Flat Rack Count:", min_value=0, value=0, step=1, key="proj_oog_count")
        oog_exw = st.number_input("OOG Unit EXW ($):", min_value=0.0, value=400000.0, step=10000.0, key="proj_oog_exw")
        oog_freight_unit = 29900.0

    with col_q2:
        st.markdown("#### MVS & Transformers")
        mvs_count = st.number_input("MVS Stations Count:", min_value=0, value=4, step=1, key="proj_mvs_count")
        mvs_exw = st.number_input("MVS Unit EXW ($):", min_value=0.0, value=250000.0, step=10000.0, key="proj_mvs_exw")
        mvs_freight_unit = 4200.0

        transformer_count = st.number_input("Transformers Count:", min_value=0, value=2, step=1, key="proj_trans_count")
        transformer_exw = st.number_input("Transformer Unit EXW ($):", min_value=0.0, value=120000.0, step=10000.0, key="proj_trans_exw")
        transformer_freight_unit = 5500.0

    with col_q3:
        st.markdown("#### Accessories & Solar PV")
        access_count = st.number_input("Accessories / Dry Containers Count:", min_value=0, value=2, step=1, key="proj_access_count")
        access_exw = st.number_input("Accessories Unit EXW ($):", min_value=0.0, value=50000.0, step=5000.0, key="proj_access_exw")
        access_freight_unit = 3200.0

        solar_count = st.number_input("Solar PV Units Count:", min_value=0, value=0, step=1, key="proj_solar_count")
        solar_exw = st.number_input("Solar Unit EXW ($):", min_value=0.0, value=300000.0, step=10000.0, key="proj_solar_exw")
        solar_freight_unit = 3360.0

    total_containers_project = max(1, bess_count + oog_count + mvs_count + transformer_count + access_count + solar_count)
    total_exw_project = (
        (bess_count * bess_exw) + (oog_count * oog_exw) + 
        (mvs_count * mvs_exw) + (transformer_count * transformer_exw) + 
        (access_count * access_exw) + (solar_count * solar_exw)
    )
    
    weighted_freight_total = (
        (bess_count * bess_freight_unit) + (oog_count * oog_freight_unit) +
        (mvs_count * mvs_freight_unit) + (transformer_count * transformer_freight_unit) +
        (access_count * access_freight_unit) + (solar_count * solar_freight_unit)
    )
    base_freight_per_unit = weighted_freight_total / total_containers_project
    total_capacity_bess_mwh = float(bess_count + oog_count) * 5.0
    is_bess = (bess_count > 0 or oog_count > 0)
    is_dg = is_bess

    st.success(f"📊 סה״כ מכולות/יחידות בפרויקט: {total_containers_project} | סה״כ ערך EXW: ${total_exw_project:,.2f}")

with tab2:
    selected_carrier = st.selectbox("Shipping Carrier:", list(CARRIER_FUEL_SURCHARGES.keys()), key="tab2_carrier")
    base_freight_input = st.number_input("Average Base Ocean Freight per Container ($):", value=float(base_freight_per_unit), step=500.0, key="tab2_freight_weighted")
    baf_surcharge = st.number_input("Bunker Surcharge ($):", value=float(CARRIER_FUEL_SURCHARGES[selected_carrier]["baf"]), step=50.0, key="tab2_baf")
    dest_thc_port_fee = st.number_input("Destination THC per Container ($):", value=380.0, step=20.0, key="tab2_dest_thc")
    china_inland_drayage = 2200.0 * (total_containers_project / 10)
    china_origin_thc = 1300.0 * (total_containers_project / 10)
    heavy_lift_survey = 2500.0
    customs_duty_pct = 2.7 if is_bess else 0.0
    insurance_pct = DEFAULT_INSURANCE_RATES.get(dest_country, 0.15)

with tab3:
    cpk_label = "Calculate inland drayage based on distance (km) & country rate" if not is_hebrew else "חשב הובלה יבשתית אוטומטית לפי מרחק (ק\"מ) ותעריף מקומי במדינה"
    use_cpk_calc = st.checkbox(cpk_label, value=False, key="tab3_cpk_toggle")
    if use_cpk_calc:
        route_km = st.number_input("Estimated Port-to-Site Distance (One-way KM):", value=350.0, step=25.0, key="tab3_route_km")
        country_rates = EUROPE_TRUCK_RATES_CPK.get(dest_country, {"dry": 2.20, "dg_heavy": 2.90})
        active_cpk_rate = country_rates["dg_heavy"] if is_dg else country_rates["dry"]
        cpk_rate_input = st.number_input("Applicable Truck Rate per KM:", value=float(active_cpk_rate), step=0.05, key="tab3_cpk_rate")
        calculated_inland_drayage = route_km * cpk_rate_input * 1.55
        st.info("ℹ️ הערה: חישוב זה מהווה הערכה תקציבית בלבד המבוססת על ממוצעי שוק.")
    else:
        calculated_inland_drayage = DRAYAGE_PORT_MATRIX.get(dest_port, 600.0)

    inland_drayage_per_unit = calculated_inland_drayage
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
    include_regulatory = True
    local_regulatory_permits = 1500.0 if is_dg else 400.0
    include_epr = True
    include_battery_passport = True
    epr_recycling_total_usd = (450.0 * float(bess_count + oog_count)) if include_epr else 0.0
    battery_passport_total_usd = 1200.0 if include_battery_passport else 0.0
    requires_heavy_lift = is_bess

trended_exw = total_exw_project * trend_multiplier
trended_ocean_freight = ((base_freight_input + baf_surcharge) * float(total_containers_project)) * trend_multiplier
trended_drayage = (inland_drayage_per_unit * float(total_containers_project)) * trend_multiplier

total_ocean_freight = trended_ocean_freight
inland_drayage_total_usd = trended_drayage

cif_valuation_base = trended_exw + china_inland_drayage + china_origin_thc + total_ocean_freight
insurance_total_usd = cif_valuation_base * (insurance_pct / 100.0)

customs_valuation_base_usd = cif_valuation_base + insurance_total_usd
customs_duty_usd = customs_valuation_base_usd * (customs_duty_pct / 100.0)
destination_thc_total = dest_thc_port_fee * float(total_containers_project)

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

with tab_summary:
    st.subheader(f"📊 Financial Dashboard - {incoterm} ({display_currency})")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Landed Cost (ex-VAT)", f"{curr_symbol} {display_val:,.2f}")
    m2.metric("Economic Cost", f"{curr_symbol} {econ_val:,.2f}")
    m3.metric("Total Cash Requirement", f"{curr_symbol} {cash_val:,.2f}")
    m4.metric("Paid to Supplier", f"{curr_symbol} {supplier_val:,.2f}")
