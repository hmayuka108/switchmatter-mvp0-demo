"""Accessible presentation theme for the Streamlit application."""
import streamlit as st

THEME_CSS = """
<style>
:root {--sm-navy:#0b1120;--sm-workspace:#edf2f7;--sm-panel:#fff;--sm-border:#cbd5e1;--sm-text:#152033;--sm-focus:#2563eb}
html,body,[data-testid="stAppViewContainer"]{font-family:"Segoe UI",Arial,sans-serif}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--sm-workspace);color:var(--sm-text)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1480px;padding:1.5rem 2rem 4rem}
h1,h2,h3{color:var(--sm-text);letter-spacing:-.025em}[data-testid="stWidgetLabel"] p{font-weight:600}
[data-testid="stSidebar"],[data-testid="stSidebar"]>div,[data-testid="stSidebarHeader"],[data-testid="stSidebarContent"],[data-testid="stSidebarUserContent"]{background:var(--sm-navy)!important}
[data-testid="stSidebar"]{border-right:1px solid #26334a}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#f8fafc!important}
[data-testid="stSidebar"] .stCaptionContainer p{color:#cbd5e1!important}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] textarea,[data-testid="stSidebar"] [data-baseweb="select"]>div{color:#111827!important;background:#fff!important;border-color:#94a3b8!important}
[data-testid="stSidebar"] input::placeholder,[data-testid="stSidebar"] textarea::placeholder{color:#64748b!important;opacity:1!important}
[data-testid="stSidebar"] [data-baseweb="select"] span,[data-testid="stSidebar"] [data-baseweb="select"] svg{color:#111827!important;fill:#111827!important}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{background:#fff!important;color:#111827!important}
[role="option"],[role="option"] *{color:#111827!important}[role="option"]:hover,[aria-selected="true"]{background:#dbeafe!important}
[data-testid="stSidebar"] .stButton>button,[data-testid="stSidebar"] .stFormSubmitButton>button{width:100%;min-height:2.75rem;color:#fff!important;background:var(--sm-focus)!important;border:1px solid #60a5fa!important;border-radius:8px;font-weight:700}
[data-testid="stSidebar"] .stButton>button:hover,[data-testid="stSidebar"] .stFormSubmitButton>button:hover{background:#1d4ed8!important}
.stButton>button,.stFormSubmitButton>button{border-radius:8px;font-weight:600}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--sm-border);border-radius:12px;background:var(--sm-panel)}
</style>
"""

def configure_page():
    st.set_page_config(page_title="SwitchMatter Pipeline", page_icon="SM", layout="wide")

def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
