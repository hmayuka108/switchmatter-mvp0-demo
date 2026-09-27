"""Streamlit rendering for screening, overrides, and scoring results."""
from html import escape
import logging
import streamlit as st
from .candidate_overrides import missing_field_specs, run_analysis_with_overrides
from .data_loader import load_alternative_materials, load_regulations
from .ui_results import prepare_screening, screening_summary
from .ui_scoring import incomplete_eligible, prepare_scoring
from .ui_safety import analysis_error_message, scoring_empty_message


def _candidate_label(candidate):
    name = candidate.get("candidate_name") or candidate["candidate_id"]
    return f"{name} | {candidate['status']}"


def _candidate_rows(candidates, selected_id):
    rows = []
    for candidate in candidates:
        candidate_id = escape(str(candidate["candidate_id"]))
        name = escape(str(candidate.get("candidate_name") or candidate_id))
        material = escape(str(candidate.get("material") or "Unknown"))
        status = escape(str(candidate["status"]))
        status_class = status.lower()
        selected = " sm-candidate-row--selected" if candidate["candidate_id"] == selected_id else ""
        rows.append(
            f"""
            <div class="sm-candidate-row{selected}">
              <div>
                <p class="sm-candidate-row__name">{name}</p>
                <p class="sm-candidate-row__meta">{candidate_id} | {material}</p>
              </div>
              <span class="sm-status-badge sm-status-badge--{status_class}">{status}</span>
            </div>
            """
        )
    return "".join(rows)


def _rule_rows(candidate):
    rows = []
    for rule in candidate["rule_details"]:
        rule_id = escape(str(rule["Rule ID"]))
        name = escape(str(rule.get("Rule name") or rule_id))
        reason = escape(str(rule.get("Reason") or ""))
        result = str(rule["Result"])
        result_label = escape(result.replace("_", " "))
        result_class = escape(result.lower())
        rows.append(
            f"""
            <div class="sm-rule-row">
              <div>
                <p class="sm-rule-row__name">{rule_id} | {name}</p>
                <p class="sm-rule-row__reason">{reason}</p>
              </div>
              <span class="sm-rule-result sm-rule-result--{result_class}">{result_label}</span>
            </div>
            """
        )
    return "".join(rows)


def _potential_rows(candidates, selected_id):
    rows = []
    for candidate in candidates:
        candidate_id = escape(str(candidate["candidate_id"]))
        name = escape(str(candidate.get("candidate_name") or candidate_id))
        material = escape(str(candidate.get("material") or "Unknown"))
        unknown_count = len(candidate["unknown_rule_ids"])
        item_label = "item" if unknown_count == 1 else "items"
        selected = (
            " sm-candidate-row--selected"
            if candidate["candidate_id"] == selected_id else ""
        )
        rows.append(
            f"""
            <div class="sm-candidate-row{selected}">
              <div>
                <p class="sm-candidate-row__name">{name}</p>
                <p class="sm-candidate-row__meta">{candidate_id} | {material}</p>
              </div>
              <div class="sm-evidence-count">
                <span class="sm-status-badge sm-status-badge--potential">Potential</span>
                <span>{unknown_count} missing {item_label}</span>
              </div>
            </div>
            """
        )
    return "".join(rows)


def show_override_form(candidate, regulations):
    specs = missing_field_specs(candidate["missing_fields"], regulations)
    overrides = st.session_state.setdefault("candidate_overrides", {})
    existing = overrides.get(candidate["candidate_id"], {})
    st.markdown("**Missing Evidence**")
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
        submitted = st.form_submit_button(
            "Apply Evidence & Re-screen →",
            type="primary",
            use_container_width=True,
        )
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
            updated_analysis = run_analysis_with_overrides(
                st.session_state.confirmed, overrides
            )
            st.session_state.analysis = updated_analysis
            st.session_state.pop("analysis_error", None)
            if updated_analysis["screening"].get("potential"):
                st.session_state.workspace_step = 3
            elif updated_analysis.get("ranking"):
                st.session_state.workspace_step = 4
            else:
                st.session_state.workspace_step = 3
            st.rerun()
        except Exception:
            logging.exception("Candidate re-screening failed")
            st.session_state.analysis_error = "Candidate re-screening could not be completed."


def show_screening_workspace(groups, summary, regulations):
    candidates = groups["eligible"] + groups["potential"] + groups["excluded"]
    total = len(candidates)
    st.html(
        f"""
        <div class="sm-screening-filters" aria-label="Candidate status summary">
          <span class="sm-screening-filter sm-screening-filter--active">All <span class="sm-screening-filter__count">{total}</span></span>
          <span class="sm-screening-filter">Eligible <span class="sm-screening-filter__count">{summary['eligible']}</span></span>
          <span class="sm-screening-filter">Potential <span class="sm-screening-filter__count">{summary['potential']}</span></span>
          <span class="sm-screening-filter">Excluded <span class="sm-screening-filter__count">{summary['excluded']}</span></span>
        </div>
        """
    )
    if not candidates:
        st.info("No candidates are available for regulation screening.")
        return

    candidate_by_id = {candidate["candidate_id"]: candidate for candidate in candidates}
    list_column, detail_column = st.columns([0.9, 1.4], gap="medium")
    with list_column:
        with st.container(border=True):
            st.markdown(
                '<p class="sm-section-kicker">Candidates</p>'
                '<h2 class="sm-section-title">Screening outcomes</h2>'
                '<p class="sm-section-copy">Select a candidate to review its rule evaluation.</p>',
                unsafe_allow_html=True,
            )
            selected_id = st.selectbox(
                "Candidate details",
                list(candidate_by_id),
                format_func=lambda candidate_id: _candidate_label(candidate_by_id[candidate_id]),
                label_visibility="collapsed",
            )
            st.html(
                f'<div class="sm-candidate-list">'
                f'{_candidate_rows(candidates, selected_id)}</div>'
            )

    candidate = candidate_by_id[selected_id]
    candidate_id = escape(str(candidate["candidate_id"]))
    candidate_name = escape(str(candidate.get("candidate_name") or candidate_id))
    status = escape(str(candidate["status"]))
    status_class = status.lower()
    with detail_column:
        with st.container(border=True):
            st.html(
                f"""
                <div class="sm-detail-heading">
                  <div>
                    <p class="sm-detail-heading__id">{candidate_id}</p>
                    <h2 class="sm-detail-heading__name">{candidate_name}</h2>
                  </div>
                  <span class="sm-status-badge sm-status-badge--{status_class}">{status}</span>
                </div>
                <p class="sm-section-kicker">Rule evaluation</p>
                <div class="sm-rule-list">{_rule_rows(candidate)}</div>
                """
            )
            if candidate["status"] == "Potential":
                st.warning(
                    "More information is required before this candidate can proceed "
                    "to scoring. Potential does not mean regulation failure."
                )
                st.caption(
                    "UNKNOWN rules: "
                    + (", ".join(candidate["unknown_rule_ids"]) or "None")
                )
                st.caption(
                    "Missing fields: "
                    + (", ".join(candidate["missing_fields"]) or "Not identified")
                )


def show_evidence_workspace(potential_candidates, regulations):
    st.markdown(
        """
        <div class="sm-step-header">
          <div class="sm-step-header__number">03</div>
          <div class="sm-step-header__content">
            <p class="sm-step-header__eyebrow">Step 3 of 4</p>
            <h1 class="sm-step-header__title">Resolve Evidence</h1>
            <p class="sm-step-header__subtitle">
              Complete missing information for Potential candidates.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not potential_candidates:
        with st.container(border=True):
            st.html(
                """
                <div class="sm-resolved-state">
                  <span class="sm-resolved-state__icon">✓</span>
                  <div>
                    <h2>Evidence resolution complete</h2>
                    <p>No Potential candidates remain.</p>
                    <p>Eligible candidates can proceed to Material Ranking.</p>
                  </div>
                </div>
                """
            )
        return

    candidate_by_id = {
        candidate["candidate_id"]: candidate
        for candidate in potential_candidates
    }
    list_column, form_column = st.columns([0.9, 1.4], gap="medium")
    with list_column:
        with st.container(border=True):
            st.markdown(
                '<p class="sm-section-kicker">Potential candidates</p>'
                '<h2 class="sm-section-title">Evidence required</h2>'
                '<p class="sm-section-copy">Select a candidate to complete its missing information.</p>',
                unsafe_allow_html=True,
            )
            selected_id = st.selectbox(
                "Potential candidate",
                list(candidate_by_id),
                format_func=lambda candidate_id: _candidate_label(
                    candidate_by_id[candidate_id]
                ),
                label_visibility="collapsed",
            )
            st.html(
                f'<div class="sm-candidate-list">'
                f'{_potential_rows(potential_candidates, selected_id)}</div>'
            )

    candidate = candidate_by_id[selected_id]
    candidate_id = escape(str(candidate["candidate_id"]))
    candidate_name = escape(
        str(candidate.get("candidate_name") or candidate_id)
    )
    unknown_candidate = {
        "rule_details": [
            rule for rule in candidate["rule_details"]
            if rule["Result"] == "UNKNOWN"
        ]
    }
    with form_column:
        with st.container(border=True):
            st.html(
                f"""
                <div class="sm-detail-heading">
                  <div>
                    <p class="sm-detail-heading__id">{candidate_id}</p>
                    <h2 class="sm-detail-heading__name">{candidate_name}</h2>
                  </div>
                  <span class="sm-status-badge sm-status-badge--potential">Potential</span>
                </div>
                <p class="sm-section-kicker">Missing Evidence</p>
                <div class="sm-rule-list">{_rule_rows(unknown_candidate)}</div>
                """
            )
            show_override_form(candidate, regulations)


def _score_text(value):
    return "—" if value is None else f"{value:.2f}"


def _ranking_rows(details, selected_id):
    rows = []
    for item in details:
        candidate_id = escape(str(item["candidate_id"]))
        candidate_name = escape(
            str(item.get("candidate_name") or candidate_id)
        )
        material = escape(str(item.get("material") or "Unknown"))
        selected = (
            " sm-ranking-row--selected"
            if item["candidate_id"] == selected_id else ""
        )
        rows.append(
            f"""
            <div class="sm-ranking-row{selected}">
              <span class="sm-ranking-row__rank">{escape(str(item['rank']))}</span>
              <span class="sm-ranking-row__candidate">
                <strong>{candidate_name}</strong>
                <small>{candidate_id}</small>
              </span>
              <span>{material}</span>
              <span>{_score_text(item['cost_score'])}</span>
              <span>{_score_text(item['properties_score'])}</span>
              <strong class="sm-ranking-row__final">{_score_text(item['display_score'])}</strong>
            </div>
            """
        )
    return "".join(rows)


def show_scoring(result, candidates):
    st.markdown(
        """
        <div class="sm-step-header">
          <div class="sm-step-header__number">04</div>
          <div class="sm-step-header__content">
            <p class="sm-step-header__eyebrow">Step 4 of 4</p>
            <h1 class="sm-step-header__title">Material Ranking</h1>
            <p class="sm-step-header__subtitle">
              Compare Eligible candidates using Cost and Properties performance.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    details = prepare_scoring(result["ranking"], candidates)
    if not details:
        st.info(scoring_empty_message(result["screening"], result["ranking"]))
    else:
        by_id = {item["candidate_id"]: item for item in details}
        selected_id = st.selectbox(
            "Ranked candidate details",
            list(by_id),
            format_func=lambda candidate_id: (
                f"Rank {by_id[candidate_id]['rank']} | "
                f"{by_id[candidate_id]['candidate_name']}"
            ),
            label_visibility="collapsed",
        )
        st.html(
            f"""
            <div class="sm-ranking-table">
              <div class="sm-ranking-row sm-ranking-row--header">
                <span>Rank</span><span>Candidate</span><span>Material</span>
                <span>Cost Score</span><span>Properties Score</span><span>Final Score</span>
              </div>
              {_ranking_rows(details, selected_id)}
            </div>
            """
        )

        selected = by_id[selected_id]
        candidate_id = escape(str(selected["candidate_id"]))
        candidate_name = escape(
            str(selected.get("candidate_name") or candidate_id)
        )
        material = escape(str(selected.get("material") or "Unknown"))
        with st.container(border=True):
            st.html(
                f"""
                <div class="sm-ranking-detail">
                  <div>
                    <p class="sm-detail-heading__id">Rank {escape(str(selected['rank']))} | {candidate_id}</p>
                    <h2 class="sm-detail-heading__name">{candidate_name}</h2>
                    <p class="sm-ranking-detail__material">{material}</p>
                  </div>
                  <div class="sm-score-card sm-score-card--final">
                    <span>Final Score</span>
                    <strong>{_score_text(selected['display_score'])}</strong>
                  </div>
                  <div class="sm-score-card">
                    <span>Cost Score</span>
                    <strong>{_score_text(selected['cost_score'])}</strong>
                  </div>
                  <div class="sm-score-card">
                    <span>Properties Score</span>
                    <strong>{_score_text(selected['properties_score'])}</strong>
                  </div>
                </div>
                <p class="sm-score-helper">
                  Final Score = 50% Cost Score + 50% Properties Score.
                  Ranking uses the backend full-precision Final Score.
                </p>
                """
            )
            with st.expander("Cost details"):
                cost = selected["cost"]
                st.table([
                    {"Input / output": "Component Volume", "Value": cost.get("volume_cm3"), "Unit": "cm³"},
                    {"Input / output": "Candidate Density", "Value": cost.get("density_g_cm3"), "Unit": "g/cm³"},
                    {"Input / output": "Calculated Mass", "Value": cost.get("mass_g"), "Unit": "g"},
                    {"Input / output": "Price per gram", "Value": cost.get("price_per_g_eur"), "Unit": "EUR/g"},
                    {"Input / output": "Current Material Cost", "Value": cost.get("current_material_cost_eur"), "Unit": "EUR"},
                    {"Input / output": "Candidate Material Cost", "Value": cost.get("material_cost_eur"), "Unit": "EUR"},
                ])
                st.caption(
                    "Cost Score values and supporting calculations come from "
                    "the existing scoring engine."
                )
            with st.expander("Property details"):
                st.dataframe(
                    selected["properties"],
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(
                    "Properties Score is supplied by the existing scoring engine."
                )

    potential_count = len(result["screening"].get("potential", []))
    excluded_count = len(result["screening"].get("excluded", []))
    if potential_count or excluded_count:
        st.html(
            f"""
            <div class="sm-not-scored">
              <strong>Not scored</strong>
              <span>Potential: {potential_count}</span>
              <span>Excluded: {excluded_count}</span>
            </div>
            """
        )
    for item in incomplete_eligible(result["screening"], candidates):
        st.warning(
            f"Scoring incomplete: {item['candidate_id']} — "
            f"{item['candidate_name']}"
        )
        st.write(item["reason"])
        if item["missing_properties"]:
            st.write(
                "Missing properties:", ", ".join(item["missing_properties"])
            )


def show_results(result, workspace_step):
    if result["analysis_status"] != "COMPLETE":
        st.error(analysis_error_message(result))
        return
    regulations, candidates = load_regulations(), load_alternative_materials()
    groups = prepare_screening(result["screening"], candidates, regulations)
    summary = screening_summary(groups)
    if workspace_step == 2:
        st.markdown(
            """
            <div class="sm-step-header">
              <div class="sm-step-header__number">02</div>
              <div class="sm-step-header__content">
                <p class="sm-step-header__eyebrow">Step 2 of 4</p>
                <h1 class="sm-step-header__title">Regulation Screening</h1>
                <p class="sm-step-header__subtitle">
                  Review candidate outcomes from the regulation screening.
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        show_screening_workspace(groups, summary, regulations)
        if groups["potential"]:
            if st.button(
                "Resolve Missing Evidence →",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.workspace_step = 3
                st.rerun()
        elif result.get("ranking"):
            if st.button(
                "View Material Ranking →",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.workspace_step = 4
                st.rerun()
    elif workspace_step == 3:
        show_evidence_workspace(groups["potential"], regulations)
    elif workspace_step == 4:
        show_scoring(result, candidates)
