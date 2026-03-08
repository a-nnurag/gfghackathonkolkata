import streamlit as st

def load_ui():

    st.set_page_config(
        page_title="AI BI Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #050816 0%, #0b1023 45%, #111827 100%);
    color: white;
}

/* Remove default top padding a bit */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Main title */
.main-title {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.3rem;
    background: linear-gradient(90deg, #ffffff, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* Glass cards */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 22px;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 1rem;
}

/* Section headings */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.8rem;
}

/* Metric pills */
.metric-pill {
    background: linear-gradient(135deg, rgba(167,139,250,0.22), rgba(34,211,238,0.18));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 0.9rem 1rem;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

.metric-label {
    color: #cbd5e1;
    font-size: 0.9rem;
    margin-bottom: 0.2rem;
}

.metric-value {
    color: white;
    font-size: 1.4rem;
    font-weight: 700;
}

/* Inputs */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    padding: 0.9rem 1rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.7rem 1.2rem;
    font-weight: 700;
    box-shadow: 0 8px 20px rgba(124, 58, 237, 0.25);
    transition: 0.2s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px rgba(6, 182, 212, 0.28);
}

/* Dataframe and code blocks */
div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
}

pre {
    border-radius: 16px !important;
}

/* Small helper text */
.helper-text {
    color: #94a3b8;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)