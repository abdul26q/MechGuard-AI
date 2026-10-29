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
    page_title="MechGuard AI | Enterprise Risk Engine",
    layout="wide",
    page_icon="️",
    initial_sidebar_state="expanded"
)

def get_api_key():
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        return env_key
    st.error("🔑 Groq API Key missing! Add `GROQ_API_KEY` to `.streamlit/secrets.toml`.")
    st.stop()

# Custom Styling (Dark Theme)
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; }
    [data-testid="stMetric"] { background-color: #1E293B; padding: 15px 20px; border-radius: 12px; border: 1px solid #334155; }
    .main-header { font-size: 2.4rem; font-weight: 800; background: linear-gradient(90deg, #0EA5E9 0%, #22C55E 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #94A3B8; margin-bottom: 1.5rem; }
    
    /* Component Cards */
    .comp-box-original { background-color: rgba(30, 27, 75, 0.6); padding: 16px; border-radius: 10px; border-left: 5px solid #6366F1; margin-bottom: 10px; backdrop-filter: blur(10px); }
    .comp-box-recommended { background-color: rgba(6, 78, 59, 0.6); padding: 16px; border-radius: 10px; border-left: 5px solid #10B981; margin-bottom: 10px; backdrop-filter: blur(10px); }
    .box-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; opacity: 0.8; }
    .title-orig { color: #A5B4FC; }
    .title-rec { color: #6EE7B7; }
    .part-mpn { font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; }
    .part-detail { font-size: 0.9rem; color: #CBD5E1; margin-bottom: 4px; }
    
    /* Badges */
    .risk-high { color: #EF4444; font-weight: 700; }
    .risk-medium { color: #F59E0B; font-weight: 700; }
    .risk-low { color: #10B981; font-weight: 700; }
    .confidence-badge { background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">MechGuard AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Enterprise Mechanical Component Risk & Sourcing Engine</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("System Status")
    st.success("️ Core Engine: Active")
    st.info("🔧 Risk Analysis: Ready")
    st.markdown("---")
    st.caption("• **Low Risk (🟢):** Standard, stable supply")
    st.caption("• **Medium Risk (🟡):** Limited suppliers")
    st.caption("• **High Risk (🔴):** Single source/Obsolete")
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** AI suggestions require human engineering verification before production.")
    st.markdown("---") 
    st.page_link("https://mechxguard.netlify.app", label="← Back to Landing Page", icon="🏠")

# -----------------------------------------------------------------------------
# 2. AI Engine Core Functions (Foolproof Prompting & Parsing)
# -----------------------------------------------------------------------------
def analyze_mechanical_components(bom_data_str, api_key):
    try:
        client = Groq(api_key=api_key)

        prompt = f"""
You are an expert Mechanical Engineering Supply Chain Analyst. 
Analyze the following mechanical Bill of Materials (BOM) data.

DATA:
{bom_data_str}

TASK:
For each component, perform a deep technical analysis. You MUST output ONLY a valid JSON array. No markdown, no conversational text.

STRICT JSON SCHEMA:
[
  {{
    "original_part": {{
      "name": "Exact part name/number",
      "type": "Component category (e.g., Fastener, Bearing)",
      "manufacturer": "Original Company (e.g., SKF, Hilti)",
      "material": "Exact material composition"
    }},
    "risk_assessment": {{
      "level": "Low, Medium, or High",
      "lead_time_weeks": 4,
      "risk_factors": ["Factor 1", "Factor 2"]
    }},
    "recommended_alternative": {{
      "name": "Alternative part name",
      "manufacturer": "Alternative Company",
      "material": "Alternative material",
      "standard": "Industry Standard (ISO/DIN/ANSI)"
    }},
    "compatibility": {{
      "is_drop_in": true,
      "logic": "1-sentence engineering reason why they are compatible (e.g., matching thread pitch and tensile strength)",
      "required_modifications": "None or specific changes needed"
    }},
    "verification": {{
      "confidence_score": 95,
      "datasheet_search_query": "Exact search term to find the official PDF datasheet"
    }},
    "sourcing": {{
      "mcmaster": "https://www.mcmaster.com/?q=PART_NUMBER",
      "grainger": "https://www.grainger.com/search?searchQuery=PART_NUMBER"
    }},
    "analysis": {{
      "summary": "Brief supply chain summary",
      "dfm_recommendations": ["Recommendation 1"]
    }}
  }}
]
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_completion_tokens=4096
        )

        text = response.choices[0].message.content.strip()

        # FOOLPROOF JSON EXTRACTION
        # 1. Remove markdown code blocks if present
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        
        # 2. Find the JSON array using regex (handles any surrounding text)
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON array found in AI response.")

    except json.JSONDecodeError as e:
        st.error(f"⚠️ AI returned invalid JSON. Please try again. Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Analysis Error: {str(e)}")
        return None

def render_component_card(item):
    # Safe extraction with defaults
    orig = item.get("original_part", {})
    risk = item.get("risk_assessment", {})
    alt = item.get("recommended_alternative", {})
    compat = item.get("compatibility", {})
    verify = item.get("verification", {})
    sourcing = item.get("sourcing", {})
    analysis = item.get("analysis", {})

    part_name = orig.get("name", "Unknown Part")
    part_type = orig.get("type", "N/A")
    part_mfr = orig.get("manufacturer", "N/A")
    part_mat = orig.get("material", "N/A")
    
    risk_level = risk.get("level", "Unknown")
    risk_factors = risk.get("risk_factors", [])
    lead_time = risk.get("lead_time_weeks", "N/A")
    
    alt_name = alt.get("name", "None suggested")
    alt_mfr = alt.get("manufacturer", "N/A")
    alt_mat = alt.get("material", "N/A")
    
    is_drop_in = compat.get("is_drop_in", False)
    compat_logic = compat.get("logic", "N/A")
    
    confidence = verify.get("confidence_score", 0)
    ds_query = verify.get("datasheet_search_query", part_name)
    
    dfm_recs = analysis.get("dfm_recommendations", [])
    summary = analysis.get("summary", "No summary provided.")

    # Risk Badge Logic
    risk_upper = str(risk_level).upper()
    if "HIGH" in risk_upper:
        badge = "🔴 HIGH RISK"
        risk_class = "risk-high"
    elif "MEDIUM" in risk_upper:
        badge = "🟡 MEDIUM RISK"
        risk_class = "risk-medium"
    else:
        badge = "🟢 LOW RISK"
        risk_class = "risk-low"

    with st.expander(f"{badge}  |  {part_type}: {part_name}", expanded=True):
        
        # Confidence & Warning
        st.markdown(f'<div class="confidence-badge">🎯 AI Confidence: {confidence}%</div>', unsafe_allow_html=True)
        st.warning("⚠️ **Engineering Verification Required:** AI alternatives are based on standard industry equivalents. Always verify physical dimensions and official datasheets before production.")

        c_left, c_right = st.columns(2)

        with c_left:
            left_box = (
                '<div class="comp-box-original">'
                '<div class="box-title title-orig">Current BOM Component</div>'
                f'<div class="part-mpn">{part_name}</div>'
                f'<div class="part-detail"><b>Company:</b> {part_mfr}</div>'
                f'<div class="part-detail"><b>Type:</b> {part_type}</div>'
                f'<div class="part-detail"><b>Material:</b> {part_mat}</div>'
                f'<div class="part-detail"><b>Lead Time:</b> {lead_time} weeks</div>'
                f'<div class="part-detail"><b>Status:</b> <span class="{risk_class}">{risk_level}</span></div>'
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
                f'<div class="part-mpn">{alt_name}</div>'
                f'<div class="part-detail"><b>Company:</b> {alt_mfr}</div>'
                f'<div class="part-detail"><b>Material:</b> {alt_mat}</div>'
                f'<div class="part-detail"><b>Drop-in Replacement:</b> {"✅ Yes" if is_drop_in else "⚠️ No"}</div>'
                '</div>'
            )
            st.markdown(right_box, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("** Compatibility Logic:**")
        st.info(compat_logic)
        
        st.markdown("** Supply Chain Analysis:**")
        st.write(summary)

        if dfm_recs:
            st.markdown("**🛠️ DFM Recommendations:**")
            for rec in dfm_recs:
                st.success(f"✓ {rec}")

        st.markdown("**🔍 Verification & Sourcing:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Datasheet Query:** `{ds_query}`")
        with col2:
            mc_url = sourcing.get("mcmaster", f"https://www.mcmaster.com/?q={part_name}")
            gr_url = sourcing.get("grainger", f"https://www.grainger.com/search?searchQuery={part_name}")
            st.markdown(f"[🔩 McMaster-Carr]({mc_url}) | [🏭 Grainger]({gr_url})")

# -----------------------------------------------------------------------------
# 3. Interface Tabs
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 Instant Part Search", "📁 Batch BOM Audit"])

# TAB 1: INSTANT SEARCH
with tab1:
    st.subheader("Search Component Risk & Alternatives")
    col_input, col_btn_search = st.columns([3, 1])
    with col_input:
        search_part = st.text_input(
            "Enter Part Number or Description:", 
            placeholder="e.g. M8-1.25 x 25mm SHCS, 6061-T6 Bracket",
            label_visibility="collapsed"
        )
    with col_btn_search:
        btn_search = st.button(" Analyze Risk", type="primary", use_container_width=True)

    if btn_search and search_part.strip():
        active_key = get_api_key()
        with st.spinner("🤖 Analyzing supply chain risk..."):
            query_str = f"Part: {search_part.strip()} | Single Part Risk Analysis"
            search_results = analyze_mechanical_components(query_str, active_key)

        if search_results:
            st.markdown("---")
            for item in search_results:
                render_component_card(item)

# TAB 2: BATCH BOM AUDIT
with tab2:
    uploaded_file = st.file_uploader("Upload Mechanical BOM (CSV/XLSX)", type=["csv", "xlsx", "xls"])

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
                    st.error(f"❌ Unable to parse file: {str(parse_err)}")
                    st.stop()

        col_map = {str(col).strip().lower(): col for col in bom_df.columns}

        with st.expander("📄 Raw BOM Preview", expanded=False):
            st.dataframe(bom_df, use_container_width=True)

        btn_audit = st.button("🚀 Run Full Audit", type="primary", use_container_width=True)

        if btn_audit:
            active_key = get_api_key()
            bom_summary = []
            for _, row in bom_df.iterrows():
                part_num = str(row.get(col_map.get("part number", "")) or row.get(col_map.get("part_number", "")) or "").strip()
                if part_num and part_num.lower() != "nan":
                    bom_summary.append(f"Part: {part_num}")

            if not bom_summary:
                st.error("❌ No valid part numbers detected!")
            else:
                total_items = len(bom_summary)
                CHUNK_SIZE = 8 # Smaller chunk for higher accuracy
                bom_chunks = [bom_summary[i:i + CHUNK_SIZE] for i in range(0, total_items, CHUNK_SIZE)]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                all_results = []

                for idx, chunk in enumerate(bom_chunks):
                    status_text.text(f" Analyzing Batch {idx + 1} of {len(bom_chunks)}...")
                    bom_data_str = "\n".join(chunk)
                    chunk_results = analyze_mechanical_components(bom_data_str, active_key)
                    
                    if chunk_results:
                        all_results.extend(chunk_results)
                    
                    progress_bar.progress((idx + 1) / len(bom_chunks))
                    if idx < len(bom_chunks) - 1:
                        time.sleep(1.5)

                status_text.success("✅ Audit Complete!")

                if all_results:
                    total_parts = len(all_results)
                    high_risk = sum(1 for x in all_results if "HIGH" in str(x.get("risk_assessment", {}).get("level", "")).upper())
                    medium_risk = sum(1 for x in all_results if "MEDIUM" in str(x.get("risk_assessment", {}).get("level", "")).upper())
                    low_risk = total_parts - (high_risk + medium_risk)

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Parts", total_parts)
                    m2.metric("Low Risk", low_risk)
                    m3.metric("Medium Risk", medium_risk)
                    m4.metric("High Risk", high_risk)

                    st.markdown("---")
                    for item in all_results:
                        render_component_card(item)
