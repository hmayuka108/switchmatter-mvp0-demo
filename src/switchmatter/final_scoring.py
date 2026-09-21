"""Final Score pipeline."""
from .cost_scoring import score_component_candidates
from .final_math import combine, final_score as calculate_final_score
from .properties_scoring import score_component_properties
from .regulation_engine import screen_component_candidates

combine_scoring_results = combine


def score_and_rank_component(current):
    return combine(screen_component_candidates(current),
                   score_component_candidates(current),
                   score_component_properties(current))
