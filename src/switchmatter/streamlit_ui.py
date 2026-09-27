"""Upload, confirmation, reset, and safe orchestration for Streamlit."""
import hashlib
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
import streamlit as st
from .pipeline import extract_and_parse, run_analysis
from .streamlit_results import show_results
from .ui_helpers import COMPONENT_OPTIONS, FOOD_CONTACT_OPTIONS
from .ui_helpers import build_confirmed_component, form_defaults
from .ui_safety import (extraction_error_message, missing_parsed_fields,
                        reset_analysis_state, validate_confirmation)
from .ui_theme import (
    apply_theme,
    configure_page,
    render_sidebar,
    render_sidebar_details,
    render_topbar,
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORM_KEYS = ("component", "current_material", "thickness_value", "thickness_unit", "food_contact")


def clear_document_state():
    keys = list(st.session_state)
    for key in (*FORM_KEYS, "parsed", "analysis", "confirmed", "extraction_error",
                "analysis_error", "confirmation_errors", "candidate_overrides"):
        st.session_state.pop(key, None)
    for key in keys:
        if str(key).startswith("override::"):
            st.session_state.pop(key, None)


def load_upload(pdf_bytes):
    with TemporaryDirectory(dir=PROJECT_ROOT, ignore_cleanup_errors=True) as directory:
        path = Path(directory) / "uploaded.pdf"
        with path.open("wb") as stream:
            stream.write(pdf_bytes)
        return extract_and_parse(path)


def accept_upload(uploaded):
    data = uploaded.getvalue()
    identity = hashlib.sha256(data).hexdigest()
    if identity == st.session_state.get("upload_identity"):
        return
    clear_document_state()
    st.session_state.upload_identity = identity
    try:
        parsed = load_upload(data)
        st.session_state.parsed = parsed
        for key, value in form_defaults(parsed["current_component"]).items():
            st.session_state[key] = value
    except Exception as exc:
        logging.exception("PDF extraction failed")
        st.session_state.extraction_error = extraction_error_message(exc)


def main():
    configure_page()
    apply_theme()
    render_sidebar()
    with st.sidebar:
        if st.button("New Analysis", use_container_width=True):
            reset_analysis_state(st.session_state)
            st.session_state.workspace_step = 1
            st.rerun()
    analysis = st.session_state.get("analysis")
    results_visible = bool(
        analysis and analysis.get("analysis_status") == "COMPLETE"
    )
    potential_exists = bool(
        results_visible and analysis["screening"].get("potential")
    )
    ranking_available = bool(
        results_visible and analysis.get("ranking")
    )
    unlocked_steps = {1}
    if results_visible:
        unlocked_steps.update((2, 3))
    if results_visible and not potential_exists and ranking_available:
        unlocked_steps.add(4)
    workspace_step = st.session_state.get("workspace_step", 1)
    if workspace_step not in {1, 2, 3, 4}:
        workspace_step = 1
    if workspace_step not in unlocked_steps:
        workspace_step = max(unlocked_steps)
    st.session_state.workspace_step = workspace_step
    render_sidebar_details(
        st.session_state.get("confirmed"),
        active_step=workspace_step,
        unlocked_steps=unlocked_steps,
    )
    workspace_titles = {
        1: "Ingest &amp; Review",
        2: "Regulation Screening",
        3: "Resolve Evidence",
        4: "Material Ranking",
    }
    render_topbar(
        st.session_state.get("confirmed"),
        workspace_title=workspace_titles[workspace_step],
    )

    if workspace_step != 1:
        show_results(analysis, workspace_step)
        return

    st.markdown(
        """
        <div class="sm-step-header">
          <div class="sm-step-header__number">01</div>
          <div class="sm-step-header__content">
            <p class="sm-step-header__eyebrow">Step 1 of 4</p>
            <h1 class="sm-step-header__title">
              Ingest &amp; Review Specifications
            </h1>
            <p class="sm-step-header__subtitle">
              Upload a component PDF and confirm the extracted values.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    workspace_columns = st.columns([0.82, 1.55], gap="medium")

    with workspace_columns[0]:
        with st.container(border=True):
            st.markdown(
                """
                <div class="sm-panel-heading">
                  <div>
                    <p class="sm-section-kicker">Source document</p>
                    <h2 class="sm-section-title">Component PDF</h2>
                  </div>
                  <span class="sm-panel-heading__badge">PDF</span>
                </div>
                <p class="sm-section-copy">
                  Upload a text-embedded component specification.
                </p>
                """,
                unsafe_allow_html=True,
            )
            version = st.session_state.get("upload_widget_version", 0)
            uploaded = st.file_uploader(
                "Upload PDF",
                type=["pdf"],
                key=f"pdf_upload_{version}",
                label_visibility="collapsed",
            )
            if uploaded is None:
                st.caption(
                    "Text-embedded PDFs only. Image-only PDFs are not "
                    "supported in MVP0."
                )

    if uploaded is None:
        return

    accept_upload(uploaded)
    if "extraction_error" in st.session_state:
        with workspace_columns[1]:
            st.error(st.session_state.extraction_error)
        return

    with workspace_columns[1]:
        with st.container(border=True):
            st.markdown(
                """
                <div class="sm-panel-heading">
                  <div>
                    <p class="sm-section-kicker">Review</p>
                    <h2 class="sm-section-title">Extracted from PDF</h2>
                  </div>
                  <span class="sm-panel-heading__status">Editable</span>
                </div>
                <p class="sm-section-copy">
                  Review and edit before confirmation.
                </p>
                """,
                unsafe_allow_html=True,
            )

            missing = missing_parsed_fields(
                st.session_state.parsed["current_component"]
            )
            if missing:
                st.warning(
                    "Parser could not determine: "
                    + ", ".join(missing)
                    + ". These values remain Unknown and may be edited below."
                )

            with st.form("confirmation_form"):
                st.markdown(
                    '<span class="sm-review-form-marker"></span>',
                    unsafe_allow_html=True,
                )

                identity_columns = st.columns(2, gap="small")
                with identity_columns[0]:
                    st.selectbox(
                        "Component",
                        COMPONENT_OPTIONS,
                        key="component",
                        format_func=lambda value: value or "Unknown / Missing",
                    )
                with identity_columns[1]:
                    st.text_input(
                        "Current Material",
                        key="current_material",
                        placeholder="Unknown / Missing",
                    )

                specification_columns = st.columns([1.35, 1, 1.35], gap="small")
                with specification_columns[0]:
                    st.number_input(
                        "Thickness",
                        min_value=0.0,
                        value=None,
                        key="thickness_value",
                        placeholder="Unknown / Missing",
                    )
                with specification_columns[1]:
                    st.text_input(
                        "Thickness Unit",
                        key="thickness_unit",
                        placeholder="Unknown / Missing",
                    )
                with specification_columns[2]:
                    st.selectbox(
                        "Food Contact",
                        FOOD_CONTACT_OPTIONS,
                        key="food_contact",
                    )

                confirmed = st.form_submit_button(
                    "Confirm & Run Regulation Screening →",
                    type="primary",
                    use_container_width=True,
                )
    if confirmed:
        current = build_confirmed_component(
            st.session_state.component, st.session_state.current_material,
            st.session_state.thickness_value, st.session_state.thickness_unit,
            st.session_state.food_contact)
        errors = validate_confirmation(current)
        if errors:
            st.session_state.confirmation_errors = errors
        else:
            st.session_state.pop("confirmation_errors", None)
            st.session_state.confirmed = current
            st.session_state.candidate_overrides = {}
            try:
                st.session_state.analysis = run_analysis(current)
                st.session_state.pop("analysis_error", None)
                st.session_state.workspace_step = 2
                st.rerun()
            except Exception:
                logging.exception("Analysis failed")
                st.session_state.analysis_error = "Analysis could not be completed."
    for error in st.session_state.get("confirmation_errors", []):
        st.error(error)
    if "analysis_error" in st.session_state:
        st.error(st.session_state.analysis_error)
    if "analysis" not in st.session_state:
        return
