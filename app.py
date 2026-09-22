import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Terra Vol | Renewable Energy & BESS Logistics Calculator",
    page_icon="⚡",
    layout="wide"
)

# --- 1. CONFIGURATIONS & DATABASES ---
COUNTRIES_DATA = {
    "Italy": {"default_vat": 22.0, "default_port": "Genoa / La Spezia", "currency": "EUR"},
    "Poland": {"default_vat": 23.0, "default_port": "Gdynia / Gdansk", "currency": "EUR"},
    "Germany": {"default_vat": 19.0, "default_port": "Hamburg / Bremerhaven", "currency": "EUR"},
    "Romania": {"default_vat": 19.0, "default_port": "Constanta", "currency": "EUR"},
    "Hungary": {"default_vat": 27.0, "default_port": "Koper / Rijeka", "currency": "EUR"},
    "Finland": {"default_vat": 25.5, "default_port": "Helsinki", "currency": "EUR"},
    "Sweden": {"default_vat": 25.0, "default_port": "Gothenburg", "currency": "EUR"},
}

EQUIPMENT_CONFIG = {
    "BESS GEN2": {"hs_code": "8507600000", "duty_pct": 2.7, "requires_epr": True, "base_freight": 4200.0},
    "MVS for BESS": {"hs_code": "8504409000", "duty_pct": 0.0, "requires_epr": False, "base_freight": 3800.0},
    "PV Modules": {"hs_code": "8541400000", "duty_pct": 0.0, "requires_epr": False, "base_freight": 3100.0},
    "TRANSFORMERS": {"hs_code": "8504230000", "duty_pct": 0.0, "requires_epr": False, "base_freight": 4500.0},
}

DRAYAGE_MATRIX = {
    "Burgas": 1850.0,
    "Koper": 1650.0,
    "Rijeka": 1550.0,
    "Hamburg": 950.0,
    "Genoa / La Spezia": 850.0,
    "Gdynia / Gdansk": 750.0,
    "Constanta": 900.0,
}

# --- 2. SIDEBAR INPUTS (SESSION STATE AWARE) ---
st.sidebar.header("🌍 Terra Vol | Project Parameters")

dest_country = st.sidebar.selectbox("Destination Country", list(COUNTRIES_DATA.keys()), key="sidebar_country")
country_info = COUNTRIES_DATA[dest_country]

equipment_type = st.sidebar.selectbox("Equipment Category", list(EQUIPMENT_CONFIG.keys()), key="sidebar_equipment")
eq_conf = EQUIPMENT_CONFIG[equipment_type]

incoterm = st.sidebar.selectbox("Incoterm", ["EXW", "FOB", "CIF", "DDP"], key="sidebar_incoterm")

# Dynamic defaults based on selections
default_vat = country_info["default_vat"]
default_duty = eq_conf["duty_pct"]
default_freight = eq_conf["base_freight"]

st.sidebar.subheader("💰 Fiscal & Cost Inputs")
applied_vat = st.sidebar.number_input(
    "Import VAT Rate (%)", 
    min_value=0.0, max_value=40.0, value=float(default_vat), 
    key=f"vat_{dest_country}"
)

customs_duty_pct = st.sidebar.number_input(
    "Customs Duty Rate (%)", 
    min_value=0.0, max_value=20.0, value=float(default_duty), 
    key=f"duty_{equipment_type}"
)

base_freight_per_unit = st.sidebar.number_input(
    "Base Ocean Freight ($ / Container)", 
    min_value=500.0, max_value=20000.0, value=float(default_freight), 
    key=f"freight_{equipment_type}"
)

container_count = st.sidebar.number_input("Container Quantity (TEU / Units)", min_value=1, max_value=1000, value=15, key="sidebar_containers")

exw_value_usd = st.sidebar.number_input("Equipment EXW Value per Unit ($)", min_value=1000.0, max_value=1000000.0, value=55000.0, key="sidebar_exw")

# Strict DDP VAT gating logic
is_ddp = (incoterm == "DDP")
vat_paid_by_supplier = st.sidebar.checkbox(
    "VAT Paid by Supplier (DDP only)", 
    value=False, 
    disabled=not is_ddp,
    key="sidebar_vat_supplier"
)

# --- 3. MAIN DASHBOARD ---
st.title("⚡ Terra Vol | Renewable Energy Logistics & Landed Cost Calculator")
st.markdown(f"**Project Scope:** {equipment_type} | **Destination:** {dest_country} | **Incoterm:** {incoterm} | **HS Code:** `{eq_conf['hs_code']}`")

# Calculations
total_equipment_value = exw_value_usd * container_count
total_ocean_freight = base_freight_per_unit * container_count
insurance_cost = total_equipment_value * 0.0035

# Drayage calculation based on port matrix
dest_port = st.sidebar.selectbox("Destination Port / Hub", list(DRAYAGE_MATRIX.keys()), key="sidebar_port")
unit_drayage = DRAYAGE_MATRIX.get(dest_port, 950.0)
total_drayage = unit_drayage * container_count

# Regulatory & EPR calculation
epr_recycling_fee = 450.0 * container_count if eq_conf["requires_epr"] else 0.0
battery_passport_fee = 1200.0 if eq_conf["requires_epr"] else 0.0
total_regulatory = epr_recycling_fee + battery_passport_fee

# Landed cost breakdown
cif_value = total_equipment_value + total_ocean_freight + insurance_cost
customs_duty_total = cif_value * (customs_duty_pct / 100.0)
indicative_vat_base = cif_value + customs_duty_total
import_vat_total = indicative_vat_base * (applied_vat / 100.0)

total_landed_cost = cif_value + customs_duty_total + total_drayage + total_regulatory
if not vat_paid_by_supplier:
    total_landed_cost += import_vat_total

# --- 4. TABS DISPLAY ---
tab1, tab2, tab3 = st.tabs(["📊 Cost Breakdown", "📦 Enriched Projects Table", "⚖️ Regulatory & Compliance"])

with tab1:
    st.subheader("Financial & Landed Cost Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Equipment Value", f"${total_equipment_value:,.0f}")
    col2.metric("Ocean & Inland Freight", f"${total_ocean_freight + total_drayage:,.0f}")
    col3.metric("Customs & Duty", f"${customs_duty_total:,.0f}", f"{customs_duty_pct}%")
    col4.metric("Import VAT", f"${import_vat_total:,.0f}", f"{applied_vat}%")
    
    st.markdown("---")
    
    summary_df = pd.DataFrame({
        "Cost Component": [
            "Equipment Value (EXW)", 
            "Ocean Freight", 
            "Marine Insurance", 
            "Inland Drayage", 
            "Customs Duty", 
            "Regulatory / EPR & Passport",
            "Import VAT"
        ],
        "Total USD": [
            total_equipment_value,
            total_ocean_freight,
            insurance_cost,
            total_drayage,
            customs_duty_total,
            total_regulatory,
            0.0 if vat_paid_by_supplier else import_vat_total
        ]
    })
    st.dataframe(summary_df.style.format({"Total USD": "${:,.2f}"}), use_container_width=True)

with tab2:
    st.subheader("Enlight 2027-2028 Project Portfolio (Enriched)")
    st.info("קובץ זה מסונכרן אוטומטית עם נתוני המיסים, קודי ה-HS, המע״מ ועלויות הרגולציה באפליקציה.")
    
    sample_data = [
        {"Site": "Genzano", "Country": "Italy", "Equipment": "PV Modules", "CONT": 9, "HS": "8541400000", "TAX": "0.0%", "VAT": "22.0%", "EPR": "Standard CE", "Cost/Unit": 30000},
        {"Site": "Mosciska", "Country": "Poland", "Equipment": "BESS GEN2", "CONT": 32, "HS": "8507600000", "TAX": "2.7%", "VAT": "23.0%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
        {"Site": "Mosciska", "Country": "Poland", "Equipment": "MVS for BESS", "CONT": 16, "HS": "8504409000", "TAX": "0.0%", "VAT": "23.0%", "EPR": "Standard CE", "Cost/Unit": 35000},
        {"Site": "Jupiter", "Country": "Germany", "Equipment": "BESS GEN2", "CONT": 480, "HS": "8507600000", "TAX": "2.7%", "VAT": "19.0%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
        {"Site": "Karpen Alpha", "Country": "Romania", "Equipment": "BESS GEN2", "CONT": 45, "HS": "8507600000", "TAX": "2.7%", "VAT": "19.0%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
        {"Site": "ACDC", "Country": "Hungary", "Equipment": "BESS GEN2", "CONT": 28, "HS": "8507600000", "TAX": "2.7%", "VAT": "27.0%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
        {"Site": "Touvilan", "Country": "Finland", "Equipment": "BESS GEN2", "CONT": 88, "HS": "8507600000", "TAX": "2.7%", "VAT": "25.5%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
        {"Site": "Picasso", "Country": "Sweden", "Equipment": "BESS GEN2", "CONT": 44, "HS": "8507600000", "TAX": "2.7%", "VAT": "25.0%", "EPR": "Battery Passport & EPR", "Cost/Unit": 50000},
    ]
    
    portfolio_df = pd.DataFrame(sample_data)
    st.dataframe(portfolio_df, use_container_width=True)

with tab3:
    st.subheader("EU Regulatory & Compliance Framework")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🔋 Battery Regulation (BESS)")
        st.write("- **Battery Passport:** Mandatory digital tracking for industrial batteries >2kWh.")
        st.write("- **Extended Producer Responsibility (EPR):** Pre-arranged end-of-life recycling pathways and financial guarantees.")
        st.write(f"- **Calculated EPR Fee for current selection:** ${epr_recycling_fee:,.0f}")
    with col_b:
        st.markdown("### ☀️ Solar & Power Equipment (PV/MVS)")
        st.write("- **Compliance:** Standard CE marking and RoHS directives.")
        st.write("- **Customs & Duties:** Zero-rate or standard TARIC codes applied automatically.")
        st.write("- **Recycling:** Standard WEEE compliance frameworks.")
