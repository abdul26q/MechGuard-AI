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
    page_title="MechGuard AI | Risk Engine",
    layout="wide",
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# Force Dark Theme via config (optional, but good practice)
st.config.set_option('theme.backgroundColor', '#000000')
st.config.set_option('theme.secondaryBackgroundColor', '#111111')
st.config.set_option('theme.textColor', '#FFFFFF')

def get_api_key():
    """Safely fetch API Key from Streamlit Secrets or Environment Variables."""
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key
        
    st.error("🔑 Groq API Key missing! Add `GROQ_API_KEY` to `.streamlit/secrets.toml` or set it as an environment variable.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. Custom CSS Injection (The Magic)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    body, .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar Styling */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebar"] {
        background-color: rgba(17, 17, 17, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .css-1d391kg h1, .css-1lcbmhc h1, [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Header & Titles */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Custom Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(30, 30, 35, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricLabel"] {
        color: #8e8e8e !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 999px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 999px;
        padding: 10px 24px;
        color: #8e8e8e;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Secondary Button (for sidebar or other uses) */
    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }

    /* Text Inputs & File Uploaders */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px !important;
    }
    .stFileUploader > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
    }

    /* Expanders (Component Cards) */
    .streamlit-expanderHeader {
        background-color: rgba(30, 30, 35, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background-color: rgba(20, 20, 25, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* Dataframes */
    .dataframe {
        background-color: rgba(20, 20, 25, 0.8) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    .dataframe th {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
    }

    /* Custom Component Boxes */
    .comp-box-original { 
        background-color: rgba(30, 27, 75, 0.6); 
        padding: 16px; 
        border-radius: 12px; 
        border-left: 4px solid #6366F1; 
        backdrop-filter: blur(10px);
    }
    .comp-box-recommended { 
        background-color: rgba(6, 78, 59, 0.6); 
        padding: 16px; 
        border-radius: 12px; 
        border-left: 4px solid #10B981; 
        backdrop-filter: blur(10px);
    }
    .box-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; opacity: 0.8; }
    .title-orig { color: #A5B4FC; }
    .title-rec { color: #6EE7B7; }
    .part-mpn { font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; }
    
    .risk-high { color: #EF4444; font-weight: 700; }
    .risk-medium { color: #F59E0B; font-weight: 700; }
    .risk-low { color: #10B981; font-weight: 700; }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Sidebar Navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ MechGuard AI")
    st.markdown("---")
    st.success(" Core Engine: Active")
    st.info("🔧 Risk Analysis: Ready")
    st.markdown("---")
    st.caption("• **Low Risk (🟢):** Standard parts, stable supply")
    st.caption("• **Medium Risk (🟡):** Limited suppliers, longer lead times")
    st.caption("• **High Risk (🔴):** Single source, scarce materials")
    
    # Add a back button to landing page
    st.markdown("---")
    st.page_link("https://papaya-blancmange-a20aa4.netlify.app/", label="← Back to Landing Page", icon="🏠")

# -----------------------------------------------------------------------------
# 4. Main Header
# -----------------------------------------------------------------------------
st.markdown('<h1 style="font-size: 3rem; margin-bottom: 0.5rem;">Mechanical BOM Risk Engine</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8e8e8e; font-size: 1.1rem; margin-bottom: 2rem;">Analyze supply chain risks, material scarcity, and manufacturing alternatives using advanced AI.</p>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. AI Engine Core Functions
# -----------------------------------------------------------------------------
def analyze_mechanical_components_with_groq(bom_data_str, api_key):
    try:
        client = Groq(api_key=api_key)

        prompt = f"""
You are an expert Mechanical Engineering Supply Chain Analyst.
Analyze mechanical components in this Bill of Materials (BOM) for supply chain risks.

{bom_data_str}

MANDATORY PARSING PROTOCOL:
- Component Type, Material Spec, Standard, Manufacturing Process, Dimensions, Surface Finish.

RISK CATEGORIES:
- LOW RISK: Standard part, 3+ suppliers, common material, lead time < 4 weeks
- MEDIUM RISK: Semi-custom, 2-3 suppliers, specialized process, lead time 4-12 weeks
- HIGH RISK: Custom/single-source, scarce material, obsolete process, lead time > 12 weeks

ALTERNATIVE RULES:
- Material substitutions, Process alternatives, Standard conversions, DFM improvements.

STRICT JSON OUTPUT (array format):
[
  {{
    "part_number": "M8-1.25 x 25mm Socket Head Cap Screw",
    "component_type": "Fastener",
    "material": "Alloy Steel Grade 8.8",
    "standard": "ISO 4762",
    "manufacturing_process": "Cold Forming",
    "current_risk_level": "Low",
    "risk_factors": ["Standard off-the-shelf", "Multiple suppliers"],
    "lead_time_weeks": 2,
    "alternative_part": "M8-1.25 x 25mm SHCS - Stainless Steel 316",
    "alternative_material": "316 Stainless Steel",
    "alternative_process": "Same",
    "alternative_standard": "ISO 4762",
    "pin_compatible": "Yes - Direct drop-in",
    "key_differences": "316 SS provides superior corrosion resistance.",
    "supplier_links": {{
      "mcmaster": "https://www.mcmaster.com/",
      "grainger": "https://www.grainger.com/",
      "fastenal": "https://www.fastenal.com/",
      "misumi": "https://www.misumi-ec.com/"
    }},
    "analysis": "Standard M8 SHCS with excellent availability.",
    "dfm_recommendations": ["Standardize material across assembly"]
  }}
]

Output ONLY valid JSON array. No markdown.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_completion_tokens=4096
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

    risk_upper = risk_level.upper()
    if "HIGH" in risk_upper:
        badge = "🔴 HIGH RISK"
        risk_class = "risk-high"
    elif "MEDIUM" in risk_upper:
        badge = "🟡 MEDIUM RISK"
        risk_class = "risk-medium"
    else:
        badge = "🟢 LOW RISK"
        risk_class = "risk-low"

    mcmaster_url = links.get("mcmaster", "#")
    grainger_url = links.get("grainger", "#")
    fastenal_url = links.get("fastenal", "#")
    misumi_url = links.get("misumi", "#")

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
                '<div class="box-title title-rec">Recommended Alternative</div>'
                f'<div class="part-mpn">{alt_part}</div>'
                f'<p style="margin-bottom: 4px;"><b>Material:</b> {alt_material}</p>'
                f'<p style="margin-bottom: 4px;"><b>Process:</b> {alt_process}</p>'
                f'<p style="margin-bottom: 0px;"><b>Compatibility:</b> {pin_compat}</p>'
                '</div>'
            )
            st.markdown(right_box, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Key Differences:**")
        st.info(diffs)

        st.markdown("**Analysis:**")
        st.write(analysis)

        if dfm_recs:
            st.markdown("**DFM Recommendations:**")
            for rec in dfm_recs:
                st.success(f"✓ {rec}")

        st.markdown(f"**Suppliers:** [McMaster]({mcmaster_url}) | [Grainger]({grainger_url}) | [Fastenal]({fastenal_url}) | [MISUMI]({misumi_url})")

# -----------------------------------------------------------------------------
# 6. Interface Tabs
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs([" Instant Search", "📁 Batch Upload"])

# TAB 1: INSTANT SEARCH
with tab1:
    st.subheader("Search Component Risk")
    col_input, col_btn_search = st.columns([3, 1])
    with col_input:
        search_part = st.text_input(
            "Enter Part Number:", 
            placeholder="e.g. M8-1.25 x 25mm SHCS, 6061-T6 Bracket",
            label_visibility="collapsed"
        )
    with col_btn_search:
        btn_search = st.button("Analyze", type="primary", use_container_width=True)

    if btn_search and search_part.strip():
        active_key = get_api_key()
        with st.spinner("Analyzing..."):
            query_str = f"Part: {search_part.strip()}"
            search_results = analyze_mechanical_components_with_groq(query_str, active_key)

        if search_results:
            st.markdown("---")
            for item in search_results:
                render_mechanical_component_card(item)

# TAB 2: BATCH BOM AUDIT
with tab2:
    st.subheader("Upload BOM for Audit")
    uploaded_file = st.file_uploader("Upload CSV/XLSX", type=["csv", "xlsx", "xls"])

    if uploaded_file:
        bom_df = None
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
                    st.error(f"Unable to parse file: {str(parse_err)}")
                    st.stop()

        col_map = {str(col).strip().lower(): col for col in bom_df.columns}

        with st.expander("Preview BOM Data", expanded=False):
            st.dataframe(bom_df, use_container_width=True)

        btn_audit = st.button("🚀 Run Full Audit", type="primary", use_container_width=True)

        if btn_audit:
            active_key = get_api_key()
            bom_summary = []
            for _, row in bom_df.iterrows():
                part_num = str(
                    row.get(col_map.get("part number", "")) or
                    row.get(col_map.get("part_number", "")) or ""
                ).strip()
                if part_num and part_num.lower() != "nan":
                    bom_summary.append(f"Part: {part_num}")

            if not bom_summary:
                st.error("No valid part numbers detected!")
            else:
                total_items = len(bom_summary)
                CHUNK_SIZE = 10
                bom_chunks = [bom_summary[i:i + CHUNK_SIZE] for i in range(0, total_items, CHUNK_SIZE)]
                
                progress_bar = st.progress(0)
                all_results = []

                for idx, chunk in enumerate(bom_chunks):
                    bom_data_str = "\n".join(chunk)
                    chunk_results = analyze_mechanical_components_with_groq(bom_data_str, active_key)
                    if chunk_results:
                        all_results.extend(chunk_results)
                    progress_bar.progress((idx + 1) / len(bom_chunks))
                    if idx < len(bom_chunks) - 1:
                        time.sleep(1.0)

                st.success("Audit Complete!")

                if all_results:
                    total_parts = len(all_results)
                    high_risk = sum(1 for x in all_results if "HIGH" in str(x.get("current_risk_level", "")).upper())
                    medium_risk = sum(1 for x in all_results if "MEDIUM" in str(x.get("current_risk_level", "")).upper())
                    low_risk = total_parts - (high_risk + medium_risk)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Parts", total_parts)
                    m2.metric("Low Risk", low_risk)
                    m3.metric("Medium Risk", medium_risk)
                    m4.metric("High Risk", high_risk)

                    st.markdown("---")
                    for item in all_results:
                        render_mechanical_component_card(item)
