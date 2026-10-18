"""State-driven Streamlit workflow for Functional Envelope through legal verdict."""
import hashlib
import logging
from pathlib import Path

import streamlit as st

from .bom import COMPONENT_TYPES, bom_for_sku, component_from_pdf_text, import_bom_xlsx, new_component, set_component_property
from .envelope import empty_envelope, load_registry, set_value, tier_completeness
from .excel_intake import import_envelope_xlsx
from .legal_gates import evaluate_legal_gates
from .pdf_extractor import extract_text_bytes
from .persistence import PipelineStore
from .ui_safety import extraction_error_message, reset_analysis_state
from .ui_theme import apply_theme, configure_page
from .verdict import build_verdict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORE = PipelineStore(PROJECT_ROOT / ".switchmatter_data" / "pipeline.json")
FORM_KEYS = ()
SKU_PLACEHOLDER = "Select a saved SKU"


def clear_document_state():
    for key in ("parsed", "extraction_error", "verdict"):
        st.session_state.pop(key, None)


def load_upload(pdf_bytes):
    text = extract_text_bytes(pdf_bytes)
    if not text.strip():
        raise RuntimeError("No extractable text")
    return {"extracted_text": text, "confirmation_required": True}


def accept_upload(uploaded):
    data = uploaded.getvalue()
    identity = hashlib.sha256(data).hexdigest()
    if identity == st.session_state.get("upload_identity"):
        return
    clear_document_state()
    st.session_state.upload_identity = identity
    try:
        st.session_state.parsed = load_upload(data)
    except Exception as exc:
        logging.exception("PDF extraction failed")
        st.session_state.extraction_error = extraction_error_message(exc)


def _legacy_main():
    configure_page()
    apply_theme()
    st.title("SwitchMatter packaging compliance pipeline")
    st.caption("Functional Envelope → Component BOM → Legal Gates → KEEP / HOLD / REMOVE")
    if st.sidebar.button("Start new analysis"):
        reset_analysis_state(st.session_state)
        st.rerun()
    data = STORE.load()
    saved_skus = sorted(data["envelopes"])
    sku_choice = st.sidebar.selectbox("Saved SKU", ["Create new", *saved_skus])
    new_sku = st.sidebar.text_input("New SKU ID", placeholder="SKU-001") if sku_choice == "Create new" else sku_choice
    sku_id = new_sku.strip()
    if not sku_id:
        st.info("Create or select a SKU to begin.")
        return
    if st.session_state.get("active_sku") != sku_id:
        st.session_state.active_sku = sku_id
        st.session_state.envelope = data["envelopes"].get(sku_id, empty_envelope(sku_id))
        st.session_state.components = bom_for_sku(data["components"], sku_id)
        st.session_state.pop("verdict", None)
    tabs = st.tabs(["1 Functional Envelope", "2 Component BOM", "3 Legal Gates", "4 Verdict"])
    with tabs[0]: _show_envelope(sku_id)
    with tabs[1]: _show_bom(sku_id)
    with tabs[2]: _show_gates()
    with tabs[3]: _show_verdict()


def load_sku(store, state, sku_id):
    """Load one persisted SKU without retaining another SKU's analysis state."""
    sku_id = str(sku_id).strip()
    data = store.load()
    if not sku_id or sku_id not in data["envelopes"]:
        raise KeyError(f"Saved SKU does not exist: {sku_id}")
    state["active_sku"] = sku_id
    state["envelope"] = data["envelopes"][sku_id]
    state["components"] = bom_for_sku(data["components"], sku_id)
    for key in ("verdict", "excel_import", "bom_unmapped", "upload_identity", "parsed", "extraction_error"):
        state.pop(key, None)
    return state["envelope"]


def create_sku(store, state, sku_id):
    """Create, persist, and activate an empty Functional Envelope."""
    sku_id = str(sku_id).strip()
    if not sku_id:
        raise ValueError("Enter a New SKU ID before creating the SKU.")
    if sku_id in store.load()["envelopes"]:
        raise ValueError(f"SKU {sku_id} already exists. Select it from Saved SKU.")
    envelope = empty_envelope(sku_id)
    store.save_envelope(envelope)
    state["active_sku"] = sku_id
    state["envelope"] = envelope
    state["components"] = []
    for key in ("verdict", "excel_import", "bom_unmapped", "upload_identity", "parsed", "extraction_error"):
        state.pop(key, None)
    return envelope


def _clear_sku_widget_state(state):
    """Clear per-SKU widget values from a callback before widgets are recreated."""
    exact = {"envelope_xlsx", "bom_unmapped"}
    prefixes = ("env::", "confirm::", "unknown::", "bom::", "bom-confirm::",
                "bom-unknown::", "supplier_file_")
    for key in list(state):
        if key in exact or str(key).startswith(prefixes):
            state.pop(key, None)


def _start_new_analysis_callback():
    reset_analysis_state(st.session_state)
    _clear_sku_widget_state(st.session_state)


def _select_saved_sku_callback():
    selected = st.session_state.get("sku_selector", SKU_PLACEHOLDER)
    if selected == SKU_PLACEHOLDER or selected == st.session_state.get("active_sku"):
        return
    _clear_sku_widget_state(st.session_state)
    load_sku(STORE, st.session_state, selected)
    st.session_state.pop("sku_error", None)


def _create_sku_callback():
    """Create from widget state; callbacks may safely reset widget-associated keys."""
    try:
        _clear_sku_widget_state(st.session_state)
        create_sku(STORE, st.session_state, st.session_state.get("new_sku_id", ""))
        st.session_state["new_sku_id"] = ""
        st.session_state["sku_selector"] = SKU_PLACEHOLDER
        st.session_state.pop("sku_error", None)
    except ValueError as exc:
        st.session_state["sku_error"] = str(exc)


def main():
    configure_page()
    apply_theme()
    st.title("SwitchMatter packaging compliance pipeline")
    st.caption("Functional Envelope → Component BOM → Legal Gates → KEEP / HOLD / REMOVE")
    st.sidebar.markdown("## SwitchMatter")
    st.sidebar.caption("Create a packaging analysis or continue a saved SKU.")
    st.sidebar.button("Start new analysis", on_click=_start_new_analysis_callback)

    data = STORE.load()
    saved_skus = sorted(data["envelopes"])
    selected = st.sidebar.selectbox(
        "Saved SKU", [SKU_PLACEHOLDER, *saved_skus], key="sku_selector",
        help="Choose an existing analysis and load its saved envelope and component BOM.",
        on_change=_select_saved_sku_callback,
    )

    st.sidebar.markdown("### Create a new SKU")
    st.sidebar.text_input("New SKU ID", placeholder="Example: SKU-001", key="new_sku_id")
    st.sidebar.button("Create SKU", type="primary", use_container_width=True,
                      on_click=_create_sku_callback)
    if st.session_state.get("sku_error"):
        st.sidebar.error(st.session_state.sku_error)

    sku_id = st.session_state.get("active_sku")
    if not sku_id:
        _show_getting_started(bool(saved_skus))
        return
    st.markdown(f"**Active SKU:** `{sku_id}`")
    tabs = st.tabs(["1 Functional Envelope", "2 Component BOM", "3 Legal Gates", "4 Verdict"])
    with tabs[0]: _show_envelope(sku_id)
    with tabs[1]: _show_bom(sku_id)
    with tabs[2]: _show_gates()
    with tabs[3]: _show_verdict()


def _show_getting_started(has_saved_skus):
    st.header("Start a packaging compliance analysis")
    st.write(
        "Each analysis belongs to a SKU. Create a new SKU in the sidebar, or select a saved SKU "
        "to continue an existing analysis. Nothing is evaluated until you explicitly confirm data."
    )
    st.markdown(
        """
1. **Create or select a SKU** in the sidebar.
2. **Complete the Functional Envelope** manually or import a brand workbook.
3. **Build the Component BOM** from supplier PDFs, a BOM workbook, or manual entries.
4. **Run Legal Gates** and review the evidence-based KEEP, HOLD, or REMOVE verdict.
        """
    )
    if has_saved_skus:
        st.info("Saved analyses are available. Choose one from Saved SKU in the sidebar.")
    else:
        st.info("No SKUs have been saved yet. Enter a New SKU ID and click Create SKU.")


def _show_envelope(sku_id):
    registry, envelope = load_registry(), st.session_state.envelope
    st.header("Step 0 Functional Envelope")
    st.warning(registry["metadata"]["scope_note"])
    workbook = st.file_uploader("Import brand product information", type=["xlsx"], key="envelope_xlsx")
    if workbook and st.button("Import workbook"):
        try:
            result = import_envelope_xlsx(workbook.getvalue(), sku_id, registry)
            st.session_state.envelope, st.session_state.excel_import = result["envelope"], result
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    for tier in ("T1", "T2", "T3", "T4"):
        definitions = [field for field in registry["fields"] if field["tier"] == tier]
        if definitions:
            with st.expander(f"{tier} fields", expanded=tier == "T1"):
                for definition in definitions: _field_editor(envelope, definition)
    st.dataframe([{"tier": tier, **value} for tier, value in tier_completeness(envelope, registry).items()], hide_index=True)
    if st.button("Save Functional Envelope", type="primary"):
        STORE.save_envelope(envelope); st.success("Envelope saved. Partial and unknown values were preserved.")
    imported = st.session_state.get("excel_import")
    if imported:
        st.caption(f"Unmapped workbook cells: {len(imported['unmapped'])}; conflicts requiring review: {len(imported['conflicts'])}")


def _field_editor(envelope, definition):
    key, current = definition["field_key"], envelope["values"][definition["field_key"]]
    cols = st.columns([2, 2, 1, 1])
    cols[0].markdown(f"**{definition['label']}**  \n{current['status']} · {current.get('source_ref') or 'manual'}")
    if definition["data_type"] == "boolean":
        choices, default = ["Unknown", "Yes", "No"], 0 if current["value"] is None else (1 if current["value"] else 2)
        raw = cols[1].selectbox(definition["label"], choices, index=default, key=f"env::{key}", label_visibility="collapsed")
        value = None if raw == "Unknown" else raw == "Yes"
    elif definition["data_type"] == "number":
        value = cols[1].number_input(definition["label"], value=current["value"], key=f"env::{key}", label_visibility="collapsed")
    else:
        existing = ", ".join(current["value"]) if isinstance(current["value"], list) else (current["value"] or "")
        raw = cols[1].text_input(definition["label"], value=existing, key=f"env::{key}", label_visibility="collapsed")
        value = [item.strip() for item in raw.split(",") if item.strip()] if definition["data_type"] == "list" else (raw or None)
    if cols[2].button("Confirm", key=f"confirm::{key}"):
        set_value(envelope, key, value, unit=definition.get("unit"), status="confirmed", source_type="user", entered_by="streamlit_user", confirmed_by="streamlit_user", registry=load_registry()); st.rerun()
    if cols[3].button("Unknown", key=f"unknown::{key}"):
        set_value(envelope, key, None, status="unknown", source_type="user", entered_by="streamlit_user", confirmed_by="streamlit_user", registry=load_registry()); st.rerun()


def _show_bom(sku_id):
    st.header("Step 1 Component BOM")
    uploaded = st.file_uploader("Upload supplier PDF or BOM workbook", type=["pdf", "xlsx"], key=f"supplier_file_{st.session_state.get('upload_widget_version', 0)}")
    if uploaded and st.button("Extract supplier file"):
        try:
            if uploaded.name.lower().endswith(".xlsx"):
                result = import_bom_xlsx(uploaded.getvalue(), sku_id); st.session_state.components.extend(result["components"]); st.session_state.bom_unmapped = result["unmapped"]; st.rerun()
            else:
                parsed = load_upload(uploaded.getvalue())
                result = component_from_pdf_text(parsed["extracted_text"], sku_id, hashlib.sha256(uploaded.getvalue()).hexdigest()[:12], uploaded.name)
                if result["component"] is None: st.warning(result["reason"])
                else: st.session_state.components.append(result["component"]); st.rerun()
        except Exception as exc:
            logging.exception("Supplier PDF extraction failed"); st.error(extraction_error_message(exc))
    component_type = st.selectbox("Add component manually", COMPONENT_TYPES)
    if st.button("Add component"):
        st.session_state.components.append(new_component(sku_id, component_type)); st.rerun()
    for component in st.session_state.components:
        with st.expander(f"{component['component_type']} · {component['component_id']}", expanded=True):
            for key, item in component["properties"].items():
                cols = st.columns([2, 2, 1, 1]); cols[0].write(f"{key} — {item['status']}")
                raw = cols[1].text_input(key, value="" if item["value"] is None else str(item["value"]), key=f"bom::{component['component_id']}::{key}", label_visibility="collapsed")
                if cols[2].button("Confirm", key=f"bom-confirm::{component['component_id']}::{key}"):
                    value = float(raw) if key in {"mass_g", "density_g_cm3", "thickness_mm"} and raw else (raw or None)
                    unit = {"mass_g": "g", "density_g_cm3": "g/cm3", "thickness_mm": "mm"}.get(key)
                    set_component_property(component, key, value, unit=unit, status="confirmed", source_type="user", confirmed_by="streamlit_user"); st.rerun()
                if cols[3].button("Unknown", key=f"bom-unknown::{component['component_id']}::{key}"):
                    set_component_property(component, key, None, status="unknown", source_type="user", confirmed_by="streamlit_user"); st.rerun()
    if st.session_state.get("bom_unmapped"): st.caption(f"Unmapped BOM cells: {len(st.session_state.bom_unmapped)}")
    if st.button("Save Component BOM", type="primary"):
        STORE.save_components(sku_id, st.session_state.components); st.success("BOM saved with evidence and history.")


def _show_gates():
    st.header("Step 2 Legal Gates")
    missing = tier_completeness(st.session_state.envelope)["T1"]["missing"]
    if missing: st.warning("Missing or unconfirmed T1 envelope fields: " + ", ".join(missing))
    if not st.session_state.components: st.warning("Add at least one component before evaluation.")
    if st.button("Run Legal Gates", disabled=not st.session_state.components):
        st.session_state.verdict = build_verdict(evaluate_legal_gates(st.session_state.envelope, st.session_state.components), st.session_state.components)
    if st.session_state.get("verdict"): st.dataframe(st.session_state.verdict["rule_results"], hide_index=True)


def _show_verdict():
    st.header("Step 3 Verdict")
    verdict = st.session_state.get("verdict")
    if not verdict: st.info("Run Legal Gates to produce a traceable verdict."); return
    {"KEEP": st.success, "HOLD": st.warning, "REMOVE": st.error}[verdict["verdict"]](f"SKU verdict: {verdict['verdict']}")
    st.write("Component verdicts", {key: value["verdict"] for key, value in verdict["components"].items()})
    if verdict["reasons_for_hold"]: st.write("Reasons for HOLD", verdict["reasons_for_hold"])
    if verdict["reasons_for_remove"]: st.write("Reasons for REMOVE", verdict["reasons_for_remove"])
    if verdict["missing_information"]: st.write("Next evidence needed", verdict["missing_information"])
    st.caption(f"Evaluated {verdict['evaluation_timestamp']} using rule registry {verdict['rule_registry_version']}")
