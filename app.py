import json
import os
import re
import time
import pandas as pd
import streamlit as st
from groq import Groq

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MechGuard AI | Mechanical Component Risk Engine",
    layout="wide",
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

def get_api_key():
    """Safely fetch API Key from Streamlit Secrets or Environment Variables."""
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key
        
    st.error("🔑 Groq API Key missing! Add `GROQ_API_KEY` to `.streamlit/secrets.toml` or set it as an environment variable.")
    st.stop()

# Custom Styling
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 30px !important; font-weight: 800 !important; }
    [data-testid="stMetric"] { background-color: #1E293B; padding: 15px 20px; border-radius: 12px; border: 1px solid #334155; }
    .main-header { font-size: 2.6rem; font-weight: 800; background: linear-gradient(90deg, #0EA5E9 0%, #22C55E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #94A3B8; margin-bottom: 1.5rem; }
    .comp-box-original { background-color: #1E1B4B; padding: 16px; border-radius: 10px; border-left: 5px solid #6366F1; margin-bottom: 10px; }
    .comp-box-recommended { background-color: #064E3B; padding: 16px; border-radius: 10px; border-left: 5px solid #10B981; margin-bottom: 10px; }
    .box-title { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .title-orig { color: #A5B4FC; }
    .title-rec { color: #6EE7B7; }
    .part-mpn { font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; }
    .risk-high { color: #EF4444; font-weight: 700; }
    .risk-medium { color: #F59E0B; font-weight: 700; }
    .risk-low { color: #10B981; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Header Section
if os.path.exists("logo.png"):
    st.image("logo.png", width=400)

st.markdown('<div class="main-header">Engineer Confidence. Secure Your Supply Chain.</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Mechanical Component Risk Analysis & Alternative Sourcing</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Sidebar Navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=400)
    st.title("System Status")
    st.success("⚙️ MechGuard AI Core: Active")
    st.info("🔧 Material Availability & Manufacturing Risk Analysis: Active")
    st.markdown("---")
    st.caption("• **Low Risk ():** Standard parts, multiple suppliers, stable materials")
    st.caption("• **Medium Risk (🟡):** Limited suppliers, material constraints, long lead times")
    st.caption("• **High Risk (🔴):** Single source, obsolete processes, material scarcity")

# -----------------------------------------------------------------------------
# 3. AI Engine Core Functions
# -----------------------------------------------------------------------------
def analyze_mechanical_components_with_groq(bom_data_str, api_key):
    try:
        client = Groq(api_key=api_key)

        prompt = f"""
        You are an expert Mechanical Engineering Supply Chain Analyst, Manufacturing Process Specialist, and Material Science Expert.
        Your task is to analyze mechanical components submitted in a Bill of Materials (BOM), evaluate their supply chain risks, 
        material availability, manufacturing process viability, and recommend alternative parts, materials, or processes.

        {bom_data_str}

        ====================================================================================================
        0. MANDATORY MECHANICAL COMPONENT PARSING PROTOCOL
        ====================================================================================================
        Before making any risk assessment, mentally deconstruct each mechanical component:
        - STEP 1 (COMPONENT TYPE): Identify category (Fastener, Bearing, Gear, Spring, Structural, Housing, Custom Machined, etc.)
        - STEP 2 (MATERIAL SPEC): Extract material (e.g., '6061-T6 Aluminum', '304 Stainless Steel', 'Delrin POM', 'AISI 4140')
        - STEP 3 (STANDARD/SPEC): Identify standards (ISO, DIN, ANSI, ASME, JIS, ASTM, etc.)
        - STEP 4 (MANUFACTURING PROCESS): Determine process (CNC Machining, Injection Molding, Stamping, Casting, Forging, 3D Printing, etc.)
        - STEP 5 (DIMENSIONS & TOLERANCES): Note critical dimensions and tolerance classes (IT6, IT7, ±0.1mm, etc.)
        - STEP 6 (SURFACE FINISH/TREATMENT): Identify finishes (Anodizing, Plating, Heat Treatment, Powder Coat, etc.)

        ====================================================================================================
        1. RISK ASSESSMENT CATEGORIES
        ====================================================================================================
        Classify each component's supply chain risk into one of these categories:
        
        **LOW RISK (🟢):**
        - Standard off-the-shelf component
        - Multiple qualified suppliers (3+)
        - Common material with stable supply
        - Standard manufacturing process
        - Lead time < 4 weeks
        
        **MEDIUM RISK (🟡):**
        - Semi-custom or limited standard options
        - 2-3 qualified suppliers
        - Material with moderate availability concerns
        - Specialized manufacturing process
        - Lead time 4-12 weeks
        - Single standard (metric/imperial conversion needed)
        
        **HIGH RISK (🔴):**
        - Custom designed part (single source)
        - Sole supplier or obsolete manufacturer
        - Critical material scarcity (rare alloys, restricted plastics)
        - Obsolete manufacturing process
        - Lead time > 12 weeks
        - Regulatory restrictions (RoHS, REACH, conflict minerals)

        ====================================================================================================
        2. ALTERNATIVE SOURCING & SUBSTITUTION RULES
        ====================================================================================================
        - MATERIAL SUBSTITUTIONS: Suggest equivalent or superior materials (e.g., 6061-T6 → 7075-T6 for strength, 
          304 SS → 316 SS for corrosion resistance, Steel → Aluminum for weight reduction)
        - PROCESS SUBSTITUTIONS: Recommend alternative manufacturing (CNC → Casting for volume, Machined → 
          Injection Molded for plastics, Traditional → Additive Manufacturing for prototypes)
        - STANDARD CONVERSIONS: Provide metric/imperial equivalents (M8 → 5/16"-18, ISO → DIN → ANSI)
        - SUPPLIER DIVERSIFICATION: Identify alternative manufacturers and distributors
        - DESIGN MODIFICATIONS: Suggest DFM (Design for Manufacturing) improvements to reduce cost/lead time

        ====================================================================================================
        3. STRICT OUTPUT POLICY & JSON SCHEMA
        ====================================================================================================
        Respond STRICTLY in valid raw JSON array format matching this exact schema:
        [
          {{
            "part_number": "M8-1.25 x 25mm Socket Head Cap Screw",
            "component_type": "Fastener - Socket Head Cap Screw",
            "material": "Alloy Steel Grade 8.8",
            "standard": "ISO 4762 / DIN 912",
            "manufacturing_process": "Cold Forming + Thread Rolling",
            "current_risk_level": "Low",
            "risk_factors": [
              "Standard off-the-shelf component",
              "Multiple global suppliers available",
              "Stable material supply chain"
            ],
            "lead_time_weeks": 2,
            "alternative_part": "M8-1.25 x 25mm SHCS - Stainless Steel 316",
            "alternative_material": "316 Stainless Steel (for corrosion resistance)",
            "alternative_process": "Same - Cold Forming",
            "alternative_standard": "ISO 4762 / DIN 912 (same standard)",
            "pin_compatible": "Yes - Direct drop-in replacement with improved corrosion resistance",
            "key_differences": "316 SS provides superior corrosion resistance vs alloy steel. Slightly lower tensile strength (Grade 8.8 equivalent). 15-20% cost increase.",
            "supplier_links": {{
              "mcmaster": "https://www.mcmaster.com/",
              "grainger": "https://www.grainger.com/",
              "fastenal": "https://www.fastenal.com/",
              "misumi": "https://www.misumi-ec.com/"
            }},
            "analysis": "Standard M8 socket head cap screw with excellent availability. Consider 316 SS alternative if operating in corrosive environments. Current alloy steel is cost-effective for general applications.",
            "dfm_recommendations": [
              "Consider standardizing on one material across assembly",
              "Evaluate if Grade 8.8 is necessary or if lower grade suffices"
            ]
          }}
        ]
        Do not wrap in triple backticks or write conversational text. Output pure JSON only.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        text = response.choices[0].message.content.strip()

        # Clean markdown code wrappers
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError("Failed to parse valid JSON from AI response.")

    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
        return None

def render_mechanical_component_card(item):
    part_num = str(item.get("part_number", "Unknown"))
    comp_type = str(item.get("component_type", "N/A"))
    material = str(item.get("material", "N/A"))
    standard = str(item.get("standard", "N/A"))
    mfg_process = str(item.get("manufacturing_process", "N/A"))
    risk_level = str(item.get("current_risk_level", "Unknown"))
    risk_factors = item.get("risk_factors", [])
    lead_time = str(item.get("lead_time_weeks", "N/A"))
    alt_part = str(item.get("alternative_part", "None required"))
    alt_material = str(item.get("alternative_material", "N/A"))
    alt_process = str(item.get("alternative_process", "N/A"))
    pin_compat = str(item.get("pin_compatible", "N/A"))
    diffs = str(item.get("key_differences", "None noted."))
    analysis = str(item.get("analysis", "No analysis provided."))
    dfm_recs = item.get("dfm_recommendations", [])
    links = item.get("supplier_links", {})

    # Risk level badge
    risk_upper = risk_level.upper()
    if "HIGH" in risk_upper:
        badge = " HIGH RISK"
        risk_class = "risk-high"
    elif "MEDIUM" in risk_upper:
        badge = "🟡 MEDIUM RISK"
        risk_class = "risk-medium"
    else:
        badge = " LOW RISK"
        risk_class = "risk-low"

    mcmaster_url = links.get("mcmaster", "https://www.mcmaster.com/")
    grainger_url = links.get("grainger", "https://www.grainger.com/")
    fastenal_url = links.get("fastenal", "https://www.fastenal.com/")
    misumi_url = links.get("misumi", "https://www.misumi-ec.com/")

    with st.expander(f"{badge}  |  {comp_type}: {part_num}", expanded=True):
        c_left, c_right = st.columns(2)

        with c_left:
            left_box = (
                '<div class="comp-box-original">'
                '<div class="box-title title-orig">Current BOM Component</div>'
                f'<div class="part-mpn">{part_num}</div>'
                f'<p style="margin-bottom: 4px;"><b>Material:</b> {material}</p>'
                f'<p style="margin-bottom: 4px;"><b>Standard:</b> {standard}</p>'
                f'<p style="margin-bottom: 4px;"><b>Process:</b> {mfg_process}</p>'
                f'<p style="margin-bottom: 4px;"><b>Lead Time:</b> {lead_time} weeks</p>'
                f'<p style="margin-bottom: 0px;"><b>Risk Level:</b> <span class="{risk_class}">{risk_level}</span></p>'
                '</div>'
            )
            st.markdown(left_box, unsafe_allow_html=True)
            
            if risk_factors:
                st.markdown("**⚠️ Risk Factors:**")
                for factor in risk_factors:
                    st.caption(f"• {factor}")

        with c_right:
            right_box = (
                '<div class="comp-box-recommended">'
                '<div class="box-title title-rec">MechGuard Recommended Alternative</div>'
                f'<div class="part-mpn">{alt_part}</div>'
                f'<p style="margin-bottom: 4px;"><b>Alternative Material:</b> {alt_material}</p>'
                f'<p style="margin-bottom: 4px;"><b>Process:</b> {alt_process}</p>'
                f'<p style="margin-bottom: 0px;"><b>Compatibility:</b> {pin_compat}</p>'
                '</div>'
            )
            st.markdown(right_box, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Key Specification & Functional Differences:**")
        st.info(diffs)

        st.markdown("**Supply Chain & Manufacturing Analysis:**")
        st.write(analysis)

        if dfm_recs:
            st.markdown("**DFM (Design for Manufacturing) Recommendations:**")
            for rec in dfm_recs:
                st.success(f"✓ {rec}")

        st.markdown("**Supplier & Distributor Links:**")
        st.markdown(f"[ McMaster-Carr]({mcmaster_url}) &nbsp;|&nbsp; [ Grainger]({grainger_url}) &nbsp;|&nbsp; [⚡ Fastenal]({fastenal_url}) &nbsp;|&nbsp; [🌐 MISUMI]({misumi_url})")

# -----------------------------------------------------------------------------
# 4. Interface Tabs
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 Instant Part Search", "📁 Batch BOM Upload Audit"])

# TAB 1: INSTANT SEARCH
with tab1:
    st.subheader("Search Mechanical Component Risk & Alternatives")
    st.caption("Enter any mechanical part number, description, or specification to analyze supply chain risk and find alternatives.")

    col_input, col_btn_search = st.columns([3, 1])
    with col_input:
        search_part = st.text_input(
            "Enter Part Number or Description:", 
            placeholder="e.g. M8-1.25 x 25mm SHCS, 6061-T6 Aluminum Bracket, 6205-2RS Bearing, 1/4-20 x 1 Hex Bolt",
            label_visibility="collapsed"
        )
    with col_btn_search:
        btn_search = st.button("🔎 Analyze Risk", type="primary", use_container_width=True)

    if btn_search and search_part.strip():
        active_key = get_api_key()
        with st.spinner(f"🤖 Analyzing supply chain risk for {search_part.strip()}..."):
            query_str = f"Part: {search_part.strip()} | Single Part Risk Analysis"
            search_results = analyze_mechanical_components_with_groq(query_str, active_key)

        if search_results:
            st.markdown("---")
            st.subheader(" Component Risk Analysis Results")
            for item in search_results:
                render_mechanical_component_card(item)

# TAB 2: BATCH BOM AUDIT
with tab2:
    uploaded_file = st.file_uploader(
        "Upload Mechanical BOM (CSV/XLSX)", 
        type=["csv", "xlsx", "xls"], 
        help="Upload CSV or Excel containing Part Number, Description, Material, Quantity columns"
    )

    if uploaded_file:
        bom_df = None
        
        # Multi-engine fallback parser
        try:
            bom_df = pd.read_csv(uploaded_file)
        except Exception:
            try:
                uploaded_file.seek(0)
                bom_df = pd.read_csv(uploaded_file, sep=None, engine="python", on_bad_lines="skip")
            except Exception:
                try:
                    uploaded_file.seek(0)
                    bom_df = pd.read_excel(uploaded_file)
                except Exception as parse_err:
                    st.error(f"❌ Unable to parse file structure: {str(parse_err)}. Ensure file is valid CSV/XLSX.")
                    st.stop()

        col_map = {str(col).strip().lower(): col for col in bom_df.columns}

        with st.expander(f"📄 Raw Uploaded BOM Data Preview ({len(bom_df)} Total Rows)", expanded=False):
            st.dataframe(bom_df, use_container_width=True)

        col_btn_audit, _ = st.columns([1, 3])
        with col_btn_audit:
            run_audit = st.button("🚀 Run Full Mechanical BOM Risk Audit", type="primary", use_container_width=True)

        if run_audit:
            active_key = get_api_key()

            bom_summary = []
            for _, row in bom_df.iterrows():
                part_num = str(
                    row.get(col_map.get("part number", "")) or
                    row.get(col_map.get("part_number", "")) or
                    row.get(col_map.get("part no", "")) or
                    row.get(col_map.get("item number", "")) or ""
                ).strip()

                desc = str(row.get(col_map.get("description", ""), "")).strip()
                material = str(row.get(col_map.get("material", ""), "")).strip()
                qty = str(row.get(col_map.get("quantity", ""), "")).strip()

                if part_num and part_num.lower() != "nan":
                    part_info = f"Part: {part_num}"
                    if desc and desc.lower() != "nan":
                        part_info += f" | Desc: {desc}"
                    if material and material.lower() != "nan":
                        part_info += f" | Material: {material}"
                    if qty and qty.lower() != "nan":
                        part_info += f" | Qty: {qty}"
                    bom_summary.append(part_info)

            if not bom_summary:
                st.error("❌ No valid part numbers detected! Ensure columns like 'Part Number' or 'Part No' exist in your file.")
            else:
                total_items = len(bom_summary)
                CHUNK_SIZE = 10  # Smaller chunks for detailed mechanical analysis
                bom_chunks = [bom_summary[i:i + CHUNK_SIZE] for i in range(0, total_items, CHUNK_SIZE)]
                total_chunks = len(bom_chunks)

                st.info(f"📦 Processing **{total_items} mechanical components** across **{total_chunks} batch requests** (10 parts/batch) for detailed risk analysis...")

                progress_bar = st.progress(0)
                status_text = st.empty()
                all_results = []

                for idx, chunk in enumerate(bom_chunks):
                    status_text.text(f"⏳ Analyzing Batch {idx + 1} of {total_chunks} ({len(chunk)} parts)...")
                    
                    bom_data_str = "\n".join(chunk)
                    chunk_results = analyze_mechanical_components_with_groq(bom_data_str, active_key)

                    if chunk_results and isinstance(chunk_results, list):
                        all_results.extend(chunk_results)
                    else:
                        st.warning(f"⚠️ Batch {idx + 1} returned incomplete results. Continuing processing remaining items.")

                    progress_bar.progress((idx + 1) / total_chunks)

                    # 1.5 second pause for detailed mechanical analysis
                    if idx < total_chunks - 1:
                        time.sleep(1.5)

                status_text.success("✅ Complete Mechanical BOM Risk Audit Finished!")

                st.markdown("---")
                if all_results:
                    total_parts = len(all_results)
                    high_risk = sum(1 for x in all_results if "HIGH" in str(x.get("current_risk_level", "")).upper())
                    medium_risk = sum(1 for x in all_results if "MEDIUM" in str(x.get("current_risk_level", "")).upper())
                    low_risk = total_parts - (high_risk + medium_risk)

                    risk_score = round(((high_risk * 1.0 + medium_risk * 0.5) / max(total_parts, 1)) * 100, 1)

                    # Executive KPI Summary Dashboard
                    st.subheader("📊 Mechanical BOM Risk Overview")
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Components Audited", total_parts)
                    m2.metric("Low Risk Components", low_risk, delta="Stable Supply", delta_color="normal")
                    m3.metric("At-Risk Components", medium_risk + high_risk, delta=f"{high_risk} High | {medium_risk} Medium", delta_color="inverse")
                    m4.metric("Overall Risk Score", f"{risk_score}%", delta="Critical Review Needed" if risk_score > 30 else "Acceptable Risk", delta_color="inverse" if risk_score > 30 else "normal")

                    st.markdown("---")
                    st.subheader("🔍 Component Risk Analysis & Alternative Matrix")

                    export_rows = []
                    for item in all_results:
                        render_mechanical_component_card(item)

                        export_rows.append({
                            "Part Number": str(item.get("part_number", "")),
                            "Component Type": str(item.get("component_type", "")),
                            "Current Material": str(item.get("material", "")),
                            "Risk Level": str(item.get("current_risk_level", "")),
                            "Lead Time (Weeks)": str(item.get("lead_time_weeks", "")),
                            "Alternative Part": str(item.get("alternative_part", "")),
                            "Alternative Material": str(item.get("alternative_material", "")),
                            "Key Differences": str(item.get("key_differences", "")),
                            "Supply Chain Analysis": str(item.get("analysis", ""))
                        })

                    st.markdown("---")
                    export_df = pd.DataFrame(export_rows)
                    csv_data = export_df.to_csv(index=False).encode('utf-8')

                    st.download_button(
                        label=f" Export Full Mechanical Risk Report ({len(export_df)} Items CSV)",
                        data=csv_data,
                        file_name="MechGuard_Full_BOM_Risk_Report.csv",
                        mime="text/csv",
                        type="primary"
                    )
