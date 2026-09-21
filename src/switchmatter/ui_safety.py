"""UI-only validation, safe messages, and session reset helpers."""
from .confirmation_boundary import PipelineError
from .pdf_extractor import PDFExtractionError

ANALYSIS_KEYS = {
    "upload_identity", "parsed", "analysis", "confirmed", "extraction_error",
    "analysis_error", "confirmation_errors", "candidate_overrides", "component",
    "current_material", "thickness_value", "thickness_unit", "food_contact",
}


def extraction_error_message(error):
    if isinstance(error, PipelineError):
        return ("No extractable text was found in this PDF. Image-only or scanned PDFs "
                "are not supported because MVP0 does not use OCR.")
    if isinstance(error, PDFExtractionError):
        return "This PDF could not be read. Please upload a valid text-embedded PDF."
    return "The PDF could not be processed. Please try another valid text-embedded PDF."


def missing_parsed_fields(current):
    return [field for field in ("component", "current_material", "thickness", "food_contact")
            if current.get(field) is None]


def validate_confirmation(current):
    errors = []
    if current.get("component") is None:
        errors.append("Component must be selected before analysis can run.")
    thickness = current.get("thickness")
    if thickness is not None:
        value = thickness.get("value") if isinstance(thickness, dict) else None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append("Thickness must be a valid number or left Unknown.")
        elif value < 0:
            errors.append("Thickness must not be negative.")
    return errors


def analysis_error_message(result):
    reason = result.get("reason", "")
    if reason.startswith("No candidates for component"):
        return "No alternative material candidates are available for this component."
    if reason == "Component confirmation is required.":
        return "Component must be selected before analysis can run."
    return "Analysis could not be completed with the confirmed data."


def scoring_empty_message(screening, ranking):
    if ranking:
        return None
    eligible = len(screening.get("eligible", []))
    potential = len(screening.get("potential", []))
    if eligible:
        return "Eligible candidates exist, but their scoring data is incomplete."
    if potential:
        return ("No candidates are currently eligible for scoring. Additional information "
                "may allow some Potential candidates to proceed.")
    return "No candidates are currently eligible for scoring."


def reset_analysis_state(state):
    version = state.get("upload_widget_version", 0) + 1
    for key in list(state):
        if key in ANALYSIS_KEYS or str(key).startswith(("override::", "pdf_upload_")):
            state.pop(key, None)
    state["upload_widget_version"] = version
