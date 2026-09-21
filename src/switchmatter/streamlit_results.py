"""Streamlit rendering for screening, overrides, and scoring results."""
import logging
import streamlit as st
from .candidate_overrides import missing_field_specs, run_analysis_with_overrides
from .data_loader import load_alternative_materials, load_regulations
from .ui_results import prepare_screening, screening_summary
from .ui_scoring import incomplete_eligible, prepare_scoring, ranking_summary
from .ui_safety import analysis_error_message, scoring_empty_message


def show_rule_details(candidate):
    with st.expander("Rule-level details"):
        st.dataframe(candidate["rule_details"], use_container_width=True, hide_index=True)


def show_override_form(candidate, regulations):
    specs = missing_field_specs(candidate["missing_fields"], regulations)
    overrides = st.session_state.setdefault("candidate_overrides", {})
    existing = overrides.get(candidate["candidate_id"], {})
    st.markdown("**Provide missing information**")
    with st.form(f"override-form::{candidate['candidate_id']}"):
        controls = []
        for spec in specs:
            field = spec["field"]
            key = f"override::{candidate['candidate_id']}::{field}"
            previous = existing.get(field)
            if spec["input_type"] == "number":
                value = st.number_input(field, value=None if previous is None else float(previous),
                                        placeholder="Unknown", key=key)
            else:
                options = ("Unknown", "Yes", "No")
                selected = "Unknown" if previous is None else ("Yes" if previous else "No")
                value = st.selectbox(field, options, index=options.index(selected), key=key)
            controls.append((spec, value))
        submitted = st.form_submit_button("Re-screen Candidate")
    if submitted:
        supplied = {}
        for spec, value in controls:
            if spec["input_type"] == "number" and value is not None:
                supplied[spec["field"]] = value
            elif spec["input_type"] == "boolean" and value != "Unknown":
                supplied[spec["field"]] = value == "Yes"
        candidate_values = dict(existing)
        candidate_values.update(supplied)
        if candidate_values:
            overrides[candidate["candidate_id"]] = candidate_values
        try:
            st.session_state.analysis = run_analysis_with_overrides(
                st.session_state.confirmed, overrides)
            st.session_state.pop("analysis_error", None)
            st.rerun()
        except Exception:
            logging.exception("Candidate re-screening failed")
            st.session_state.analysis_error = "Candidate re-screening could not be completed."


def show_candidate_group(title, candidates, kind, regulations):
    st.subheader(title)
    if not candidates:
        st.info("No candidates in this status.")
        return
    for candidate in candidates:
        st.markdown(f"**{candidate['candidate_id']} — {candidate['candidate_name']}**")
        st.caption(f"Material: {candidate['material']}")
        if kind == "eligible":
            st.success("Status: Eligible")
        elif kind == "potential":
            st.warning("Status: Potential")
            st.info("More information is required before this candidate can proceed to scoring. "
                    "Potential does not mean regulation failure.")
            st.write("UNKNOWN rules:", ", ".join(candidate["unknown_rule_ids"]) or "None")
            st.write("Missing fields:", ", ".join(candidate["missing_fields"]) or "Not identified")
            show_override_form(candidate, regulations)
        else:
            st.error("Status: Excluded — this candidate does not proceed to scoring.")
            failed = [row for row in candidate["rule_details"] if row["Result"] == "FAIL"]
            st.write("FAIL rules:", ", ".join(candidate["fail_rule_ids"]) or "None")
            st.table(failed)
        show_rule_details(candidate)
        st.divider()


def show_scoring(result, candidates):
    st.header("4. Scoring & Ranking")
    st.caption("Only Eligible candidates proceed to scoring and ranking.")
    details = prepare_scoring(result["ranking"], candidates)
    if details:
        st.dataframe(ranking_summary(details), use_container_width=True, hide_index=True)
    else:
        st.info(scoring_empty_message(result["screening"], result["ranking"]))
    for item in details:
        with st.expander(f"Rank {item['rank']}: {item['candidate_id']} — {item['material']}"):
            st.subheader("Regulation Status")
            st.success(item["regulation_status"])
            st.subheader("Cost")
            cost = item["cost"]
            st.table([
                {"Input / output": "Component Volume", "Value": cost.get("volume_cm3"), "Unit": "cm³"},
                {"Input / output": "Candidate Density", "Value": cost.get("density_g_cm3"), "Unit": "g/cm³"},
                {"Input / output": "Calculated Mass", "Value": cost.get("mass_g"), "Unit": "g"},
                {"Input / output": "Price per gram", "Value": cost.get("price_per_g_eur"), "Unit": "EUR/g"},
                {"Input / output": "Current Material Cost", "Value": cost.get("current_material_cost_eur"), "Unit": "EUR"},
                {"Input / output": "Candidate Material Cost", "Value": cost.get("material_cost_eur"), "Unit": "EUR"},
            ])
            st.metric("Cost Score", item["cost_score"])
            st.caption("Cost Score = 5 + 5 × (Current Cost − Candidate Cost) / Current Cost "
                       "(then clipped to 0–10). Values come from the scoring engine.")
            st.subheader("Properties")
            st.dataframe(item["properties"], use_container_width=True, hide_index=True)
            st.metric("Properties Score", item["properties_score"])
            st.caption("Properties Score = average of property scores. Value comes from the engine.")
            st.subheader("Final Score")
            left, middle, right = st.columns(3)
            left.metric("Cost Score (50%)", item["cost_score"])
            middle.metric("Properties Score (50%)", item["properties_score"])
            right.metric("Final Score", item["display_score"])
            st.caption("Final Score = 0.5 × Cost Score + 0.5 × Properties Score. "
                       "Ranking uses the existing full-precision Final Score.")
    for item in incomplete_eligible(result["screening"], candidates):
        st.warning(f"Scoring incomplete: {item['candidate_id']} — {item['candidate_name']}")
        st.write(item["reason"])
        if item["missing_properties"]:
            st.write("Missing properties:", ", ".join(item["missing_properties"]))


def show_results(result):
    if result["analysis_status"] != "COMPLETE":
        st.error(analysis_error_message(result))
        return
    regulations, candidates = load_regulations(), load_alternative_materials()
    groups = prepare_screening(result["screening"], candidates, regulations)
    st.header("3. Regulation Screening")
    summary = screening_summary(groups)
    eligible, potential, excluded = st.columns(3)
    eligible.metric("Eligible", summary["eligible"])
    potential.metric("Potential", summary["potential"])
    excluded.metric("Excluded", summary["excluded"])
    if summary["eligible"] == 0:
        st.info("No candidates are currently eligible for scoring.")
    if summary["potential"]:
        st.info("Additional information may allow some Potential candidates to proceed. "
                "Potential does not mean regulation failure.")
    show_candidate_group("Eligible Candidates", groups["eligible"], "eligible", regulations)
    show_candidate_group("Potential Candidates", groups["potential"], "potential", regulations)
    show_candidate_group("Excluded Candidates", groups["excluded"], "excluded", regulations)
    show_scoring(result, candidates)
