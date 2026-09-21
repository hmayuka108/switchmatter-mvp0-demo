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
    st.title("SwitchMatter MVP0")
    st.caption("Upload → Review and confirm → Regulation Screening → Scoring & Ranking")
    if st.button("Start New Analysis"):
        reset_analysis_state(st.session_state)
        st.rerun()
    st.header("1. Upload PDF")
    version = st.session_state.get("upload_widget_version", 0)
    uploaded = st.file_uploader("Upload PDF", type=["pdf"], key=f"pdf_upload_{version}")
    if uploaded is None:
        st.info("Upload a text-embedded PDF to begin. Image-only PDFs require OCR and are not supported.")
        return
    accept_upload(uploaded)
    if "extraction_error" in st.session_state:
        st.error(st.session_state.extraction_error)
        return
    st.header("2. Review Extracted Data")
    missing = missing_parsed_fields(st.session_state.parsed["current_component"])
    if missing:
        st.warning("Parser could not determine: " + ", ".join(missing) +
                   ". These values remain Unknown and may be edited below.")
    with st.form("confirmation_form"):
        st.selectbox("Component", COMPONENT_OPTIONS, key="component",
                     format_func=lambda value: value or "Unknown / Missing")
        st.text_input("Current Material", key="current_material", placeholder="Unknown / Missing")
        st.number_input("Thickness", min_value=0.0, value=None, key="thickness_value",
                        placeholder="Unknown / Missing")
        st.text_input("Thickness Unit", key="thickness_unit", placeholder="Unknown / Missing")
        st.selectbox("Food Contact", FOOD_CONTACT_OPTIONS, key="food_contact")
        confirmed = st.form_submit_button("Confirm and Continue", type="primary")
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
            except Exception:
                logging.exception("Analysis failed")
                st.session_state.analysis_error = "Analysis could not be completed."
    for error in st.session_state.get("confirmation_errors", []):
        st.error(error)
    if "analysis_error" in st.session_state:
        st.error(st.session_state.analysis_error)
    if "analysis" not in st.session_state:
        st.info("Complete the required confirmation fields, then select Confirm and Continue.")
        return
    show_results(st.session_state.analysis)
