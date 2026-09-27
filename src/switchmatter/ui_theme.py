"""Presentation-only visual system for the Streamlit application shell."""

from html import escape

import streamlit as st


THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --sm-navy: #0b1120;
  --sm-workspace: #edf2f7;
  --sm-panel: #ffffff;
  --sm-inset: #f5f8fb;
  --sm-border: #dbe4ee;
  --sm-text: #152033;
  --sm-muted: #64748b;
  --sm-blue: #1769ff;
  --sm-green: #059669;
  --sm-amber: #d97706;
  --sm-red: #dc2626;
  --sm-radius: 12px;
  --sm-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: "Manrope", "Segoe UI", sans-serif;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--sm-workspace);
  color: var(--sm-text);
}
[data-testid="stHeader"] { background: transparent; height: 0; }
.block-container { max-width: 1360px; padding: 1.15rem 1.5rem 3rem; }
h1, h2, h3 { color: var(--sm-text); letter-spacing: -0.025em; }
h1 { font-weight: 700 !important; }
h2, h3 { font-weight: 650 !important; }
label, [data-testid="stWidgetLabel"] p { font-weight: 600 !important; }
code, pre, .sm-mono { font-family: Consolas, "Liberation Mono", monospace; }

[data-testid="stSidebar"] {
  min-width: 278px;
  max-width: 278px;
  background: var(--sm-navy);
  border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] > div:first-child { padding: 0; }
[data-testid="stSidebar"] .stButton { padding: 0 1.25rem 0.35rem; }
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  min-height: 40px;
  border: 1px solid #2b3a52;
  border-radius: 9px;
  background: #1a273a;
  color: #f8fafc;
  font-weight: 600;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  border-color: var(--sm-blue);
  background: var(--sm-blue);
  color: #ffffff;
}
[data-testid="stSidebar"] .stButton > button:disabled {
  border-color: #1e293b;
  background: #101827;
  color: #64748b;
  opacity: 1;
}

.sm-topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: 58px;
  margin: -1.5rem -2rem 1.5rem;
  padding: 0 2rem;
  border-bottom: 1px solid var(--sm-border);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--sm-border);
  border-radius: var(--sm-radius);
  background: var(--sm-panel);
  box-shadow: var(--sm-shadow);
}
.stButton > button, .stFormSubmitButton > button {
  border-radius: 8px;
  font-weight: 600;
}
[data-testid="stFormSubmitButton"] button[kind="primary"] {
  border-color: var(--sm-blue);
  background: var(--sm-blue);
  color: #ffffff;
}
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
  border-color: #0f5de5;
  background: #0f5de5;
  color: #ffffff;
}
[data-testid="stFormSubmitButton"] button[kind="primary"]:focus-visible {
  border-color: var(--sm-blue);
  outline: 3px solid rgba(23, 105, 255, 0.24);
  outline-offset: 2px;
  box-shadow: none;
}
.stButton > button[kind="primary"] {
  border-color: var(--sm-blue);
  background: var(--sm-blue);
  color: #ffffff;
}
.stButton > button[kind="primary"]:hover {
  border-color: #0f5de5;
  background: #0f5de5;
  color: #ffffff;
}
.stButton > button[kind="primary"]:focus-visible {
  border-color: var(--sm-blue);
  outline: 3px solid rgba(23, 105, 255, 0.24);
  outline-offset: 2px;
  box-shadow: none;
}

.sm-sidebar-brand {
  display: flex;
  gap: 0.7rem;
  align-items: center;
  padding: 1.15rem 1.25rem 1rem;
  border-bottom: 1px solid #1e293b;
}
.sm-sidebar-brand__mark {
  display: grid;
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  place-items: center;
  border-radius: 8px;
  background: var(--sm-blue);
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 800;
}
.sm-sidebar-brand__name {
  margin: 0;
  color: #f8fafc;
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.sm-sidebar-brand__tagline {
  margin: 0.25rem 0 0;
  color: #94a3b8;
  font-size: 0.75rem;
  line-height: 1.4;
}
.sm-sidebar-nav {
  padding: 1rem 1.25rem 0.25rem;
}
.sm-sidebar-nav__label {
  margin: 0 0 0.75rem;
  color: #64748b;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.sm-sidebar-nav__item {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  min-height: 38px;
  color: #cbd5e1;
  font-size: 0.84rem;
  font-weight: 500;
}
.sm-sidebar-nav__number {
  color: #64748b;
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 0.72rem;
}

.sm-sidebar-nav__item--active {
  margin: 0.2rem -0.45rem;
  padding: 0.6rem 0.65rem;
  border-radius: 8px;
  background: #1769ff;
  color: #ffffff;
  font-weight: 650;
}

.sm-sidebar-nav__item--active .sm-sidebar-nav__number {
  color: #dbeafe;
}
.sm-sidebar-current {
  margin: 0 1.25rem;
  padding: 0.8rem;
  border: 1px solid #25344b;
  border-radius: 9px;
  background: #111c2e;
}
.sm-sidebar-current__label {
  margin: 0 0 0.45rem;
  color: #64748b;
  font-size: 0.64rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.sm-sidebar-current__value {
  overflow: hidden;
  margin: 0.12rem 0 0;
  color: #e2e8f0;
  font-size: 0.76rem;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sm-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sm-topbar > div {
  display: flex;
  gap: 0.55rem;
  align-items: baseline;
}
.sm-topbar__eyebrow {
  color: var(--sm-muted);
  font-size: 0.7rem;
  font-weight: 650;
}
.sm-topbar__eyebrow::after {
  margin-left: 0.55rem;
  color: #cbd5e1;
  content: "/";
}
.sm-topbar__title {
  color: var(--sm-text);
  font-size: 0.95rem;
  font-weight: 700;
}
.sm-topbar__meta {
  color: var(--sm-muted);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.sm-page-header {
  margin: 0 0 0.9rem;
}

.sm-page-header__title {
  margin: 0;
  color: var(--sm-text);
  font-size: clamp(1.45rem, 1.7vw, 1.75rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.15;
}

.sm-page-header__subtitle {
  margin: 0.3rem 0 0;
  color: var(--sm-muted);
  font-size: 0.86rem;
  line-height: 1.4;
}
.sm-section-kicker {
  margin: 0 0 0.3rem;
  color: var(--sm-blue);
  font-size: 0.68rem;
  font-weight: 750;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}
.sm-section-title {
  margin: 0;
  color: var(--sm-text);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.sm-section-copy {
  margin: 0.2rem 0 0.65rem;
  color: var(--sm-muted);
  font-size: 0.8rem;
  line-height: 1.4;
}
div[data-testid="stFileUploader"] section {
  border-color: var(--sm-border);
  border-radius: 10px;
  background: var(--sm-inset);
  padding: 0.55rem 0.75rem;
  min-height: auto;
}

.sm-review-kicker {
  color: var(--sm-blue);
}

.sm-review-title {
  font-size: 1.15rem;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.sm-topbar {
  min-height: 46px;
  margin: -1.15rem -1.5rem 0.9rem;
  padding: 0 1.5rem;
}

div[data-testid="stFileUploader"] {
  margin-bottom: 0.15rem;
}
div[data-testid="stFileUploader"] section:hover {
  border-color: var(--sm-blue);
}
div[data-testid="stFileUploader"] button {
  min-height: 34px;
  border-color: #cbd5e1;
  border-radius: 7px;
  background: #ffffff;
  font-weight: 650;
}

.sm-step-header {
  display: flex;
  gap: 0.9rem;
  align-items: center;
  margin: 0 0 0.9rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--sm-border);
  border-radius: var(--sm-radius);
  background: var(--sm-panel);
  box-shadow: var(--sm-shadow);
}
.sm-step-header__number {
  display: grid;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 9px;
  background: #eaf1ff;
  color: var(--sm-blue);
  font-size: 0.74rem;
  font-weight: 800;
}
.sm-step-header__eyebrow {
  margin: 0 0 0.1rem;
  color: var(--sm-blue);
  font-size: 0.65rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.sm-step-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 750;
  line-height: 1.25;
}
.sm-step-header__subtitle {
  margin: 0.15rem 0 0;
  color: var(--sm-muted);
  font-size: 0.78rem;
  line-height: 1.35;
}
.sm-panel-heading {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
}
.sm-panel-heading__badge,
.sm-panel-heading__status {
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 750;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.sm-panel-heading__badge {
  background: #eef2f7;
  color: var(--sm-muted);
}
.sm-panel-heading__status {
  background: #eaf1ff;
  color: var(--sm-blue);
}
.sm-screening-filters {
  display: flex;
  gap: 0.35rem;
  margin: 0 0 0.9rem;
  padding: 0.3rem;
  border: 1px solid var(--sm-border);
  border-radius: 10px;
  background: #e8eef5;
}
.sm-screening-filter {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
  padding: 0.42rem 0.7rem;
  border-radius: 7px;
  color: var(--sm-muted);
  font-size: 0.72rem;
  font-weight: 700;
}
.sm-screening-filter--active {
  background: #ffffff;
  color: var(--sm-text);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}
.sm-screening-filter__count {
  color: var(--sm-muted);
  font-size: 0.66rem;
}
.sm-candidate-list,
.sm-rule-list {
  overflow: hidden;
  border: 1px solid var(--sm-border);
  border-radius: 9px;
}
.sm-candidate-row,
.sm-rule-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  justify-content: space-between;
  padding: 0.62rem 0.7rem;
  border-bottom: 1px solid var(--sm-border);
  background: #ffffff;
}
.sm-candidate-row:last-child,
.sm-rule-row:last-child {
  border-bottom: 0;
}
.sm-candidate-row--selected {
  box-shadow: inset 3px 0 0 var(--sm-blue);
  background: #f6f9ff;
}
.sm-candidate-row__name,
.sm-rule-row__name {
  margin: 0;
  color: var(--sm-text);
  font-size: 0.76rem;
  font-weight: 700;
}
.sm-candidate-row__meta,
.sm-rule-row__reason {
  margin: 0.12rem 0 0;
  color: var(--sm-muted);
  font-size: 0.66rem;
  line-height: 1.35;
}
.sm-evidence-count {
  display: grid;
  flex: 0 0 auto;
  gap: 0.25rem;
  justify-items: end;
  color: var(--sm-muted);
  font-size: 0.64rem;
  font-weight: 650;
}
.sm-status-badge,
.sm-rule-result {
  flex: 0 0 auto;
  padding: 0.2rem 0.45rem;
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.035em;
  text-transform: uppercase;
}
.sm-status-badge--eligible,
.sm-rule-result--pass {
  background: #dcfce7;
  color: #047857;
}
.sm-status-badge--potential,
.sm-rule-result--unknown {
  background: #fef3c7;
  color: #b45309;
}
.sm-status-badge--excluded,
.sm-rule-result--fail {
  background: #fee2e2;
  color: #b91c1c;
}
.sm-rule-result--not_applicable {
  background: #eef2f7;
  color: #64748b;
}
.sm-detail-heading {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.sm-detail-heading__id {
  margin: 0 0 0.15rem;
  color: var(--sm-muted);
  font-size: 0.64rem;
  font-weight: 750;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.sm-detail-heading__name {
  margin: 0;
  color: var(--sm-text);
  font-size: 1rem;
  font-weight: 750;
}
.sm-rule-list {
  margin-top: 0.45rem;
}
.sm-resolved-state {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  padding: 0.25rem;
}
.sm-resolved-state__icon {
  display: grid;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  place-items: center;
  border-radius: 9px;
  background: #dcfce7;
  color: var(--sm-green);
  font-weight: 800;
}
.sm-resolved-state h2 {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 750;
}
.sm-resolved-state p {
  margin: 0.14rem 0 0;
  color: var(--sm-muted);
  font-size: 0.72rem;
}
.sm-ranking-table {
  overflow-x: auto;
  margin-bottom: 0.9rem;
  border: 1px solid var(--sm-border);
  border-radius: 10px;
  background: #ffffff;
  box-shadow: var(--sm-shadow);
}
.sm-ranking-row {
  display: grid;
  grid-template-columns: 56px minmax(180px, 1.5fr) minmax(90px, 0.8fr) repeat(3, minmax(92px, 0.72fr));
  gap: 0.65rem;
  align-items: center;
  min-width: 760px;
  padding: 0.65rem 0.8rem;
  border-bottom: 1px solid var(--sm-border);
  color: var(--sm-text);
  font-size: 0.72rem;
}
.sm-ranking-row:last-child {
  border-bottom: 0;
}
.sm-ranking-row--header {
  background: var(--sm-inset);
  color: var(--sm-muted);
  font-size: 0.64rem;
  font-weight: 750;
  letter-spacing: 0.035em;
  text-transform: uppercase;
}
.sm-ranking-row--selected {
  box-shadow: inset 3px 0 0 var(--sm-blue);
  background: #f6f9ff;
}
.sm-ranking-row__rank {
  color: var(--sm-blue);
  font-size: 0.8rem;
  font-weight: 800;
}
.sm-ranking-row__candidate {
  display: grid;
  gap: 0.08rem;
}
.sm-ranking-row__candidate small {
  color: var(--sm-muted);
  font-size: 0.62rem;
}
.sm-ranking-row__final {
  color: var(--sm-blue);
  font-size: 0.8rem;
}
.sm-ranking-detail {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) repeat(3, minmax(110px, 0.42fr));
  gap: 0.65rem;
  align-items: stretch;
}
.sm-ranking-detail__material {
  margin: 0.18rem 0 0;
  color: var(--sm-muted);
  font-size: 0.72rem;
}
.sm-score-card {
  display: grid;
  align-content: center;
  padding: 0.6rem 0.7rem;
  border: 1px solid var(--sm-border);
  border-radius: 8px;
  background: var(--sm-inset);
}
.sm-score-card span {
  color: var(--sm-muted);
  font-size: 0.62rem;
  font-weight: 700;
}
.sm-score-card strong {
  margin-top: 0.12rem;
  color: var(--sm-text);
  font-size: 1rem;
}
.sm-score-card--final {
  border-color: #bfdbfe;
  background: #eff6ff;
}
.sm-score-card--final strong {
  color: var(--sm-blue);
  font-size: 1.25rem;
}
.sm-score-helper {
  margin: 0.65rem 0 0;
  color: var(--sm-muted);
  font-size: 0.68rem;
}
.sm-not-scored {
  display: flex;
  gap: 0.7rem;
  align-items: center;
  margin-top: 0.75rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--sm-border);
  border-radius: 8px;
  background: var(--sm-inset);
  color: var(--sm-muted);
  font-size: 0.68rem;
}
.sm-not-scored strong {
  color: var(--sm-text);
}
.sm-rule-row > div {
  min-width: 0;
}
div[data-testid="stForm"]:has(.sm-review-form-marker)
  div[data-testid="stVerticalBlock"] {
  gap: 0.55rem;
}
div[data-testid="stForm"]:has(.sm-review-form-marker)
  [data-testid="stWidgetLabel"] {
  min-height: auto;
  margin-bottom: 0.1rem;
}
div[data-testid="stForm"]:has(.sm-review-form-marker)
  [data-testid="stWidgetLabel"] p {
  font-size: 0.74rem;
}
div[data-testid="stForm"]:has(.sm-review-form-marker)
  input {
  min-height: 38px;
}

div[data-testid="stForm"]:has(.sm-review-form-marker)
  [data-testid="stFormSubmitButton"] {
  margin: 0.3rem -0.15rem -0.15rem;
  padding: 0.7rem 0.15rem 0.15rem;
  border-top: 1px solid var(--sm-border);
}
div[data-testid="stForm"]:has(.sm-review-form-marker)
  [data-testid="stFormSubmitButton"] button {
  min-height: 42px;
  border-color: var(--sm-blue);
  background: var(--sm-blue);
  box-shadow: 0 4px 12px rgba(23, 105, 255, 0.2);
}

@media (max-width: 900px) {
  [data-testid="stSidebar"] {
    min-width: 244px;
    max-width: 244px;
  }
  .block-container {
    padding: 1rem 0.85rem 3rem;
  }
  .sm-topbar {
    margin: -1rem -0.85rem 1rem;
    padding: 0 0.85rem;
  }
  .sm-step-header {
    align-items: flex-start;
    padding: 0.8rem;
  }
  .sm-ranking-detail {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .sm-topbar__meta {
    display: none;
  }
  .sm-step-header__number {
    display: none;
  }
  .sm-step-header {
    display: block;
  }
  .sm-ranking-detail {
    grid-template-columns: 1fr;
  }
}
</style>
"""


def configure_page():
    """Configure the Streamlit page before visible output."""
    st.set_page_config(
        page_title="SwitchMatter MVP0",
        page_icon="♻️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def apply_theme():
    """Inject presentation-only design tokens and surface styles."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_sidebar():
    """Render the application identity above the sidebar controls."""
    st.sidebar.markdown(
        """
        <div class="sm-sidebar-brand">
          <div class="sm-sidebar-brand__mark">S</div>
          <div>
            <p class="sm-sidebar-brand__name">SwitchMatter</p>
            <p class="sm-sidebar-brand__tagline">Material intelligence</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_details(confirmed=None, active_step=1, unlocked_steps=(1,)):
    """Render current analysis context and state-driven workflow navigation."""

    current_analysis = ""
    if confirmed is not None:
        component_value = confirmed.get("component")
        material_value = confirmed.get("current_material")

        component = escape(
            str(component_value).replace("_", " ").title()
            if component_value else "Unknown"
        )
        material = escape(
            str(material_value) if material_value else "Unknown"
        )
        current_analysis = f"""
        <div class="sm-sidebar-current">
          <p class="sm-sidebar-current__label">Current analysis</p>
          <p class="sm-sidebar-current__value">{component}</p>
          <p class="sm-sidebar-current__value">{material}</p>
        </div>
        """

    st.sidebar.markdown(
        """
        <div class="sm-sidebar-nav">
          <p class="sm-sidebar-nav__label">Workflow</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    labels = {
        1: "01  Ingest & Review",
        2: "02  Regulation Screening",
        3: "03  Resolve Evidence",
        4: "04  Material Ranking",
    }
    unlocked = set(unlocked_steps)
    for step, label in labels.items():
        if st.sidebar.button(
            label,
            key=f"workflow_step_{step}",
            type="primary" if step == active_step else "secondary",
            disabled=step not in unlocked,
            use_container_width=True,
        ):
            st.session_state.workspace_step = step
            st.rerun()
    if current_analysis:
        st.sidebar.markdown(current_analysis, unsafe_allow_html=True)


def render_topbar(confirmed=None, workspace_title="Ingest &amp; Review"):
    """Render compact page context using only existing confirmed data."""
    component_value = confirmed.get("component") if confirmed else None
    component = (
        escape(str(component_value).replace("_", " ").title())
        if component_value else "Awaiting confirmation"
    )
    st.markdown(
        f"""
        <div class="sm-topbar">
          <div>
            <span class="sm-topbar__eyebrow">Current workspace</span>
            <span class="sm-topbar__title">{workspace_title}</span>
          </div>
          <span class="sm-topbar__meta">{component}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
