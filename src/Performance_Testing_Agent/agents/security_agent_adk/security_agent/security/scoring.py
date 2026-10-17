from decimal import Decimal, ROUND_HALF_UP

from security_agent.models.assessment import SecurityAssessment


def calculate_security_score(
    assessments: list[SecurityAssessment],
) -> str:
    """
    Calculate an overall security score from completed assessments.

    Rules:
    - No assessments -> N/A
    - Ignore N/A scores, which represent controls without a numeric score.
    - Include numeric scores even when that control's status is WARNING.
    - Return N/A only when no valid numeric assessment score is available.
    """

    if not assessments:
        return "N/A"

    scores: list[Decimal] = []

    for assessment in assessments:
        score = assessment.security_score.strip()

        if score.upper() == "N/A":
            continue

        if not score.endswith("%"):
            return "N/A"

        try:
            numeric_score = Decimal(score[:-1])
        except Exception:
            return "N/A"

        if not 0 <= numeric_score <= 100:
            return "N/A"

        scores.append(numeric_score)

    if not scores:
        return "N/A"

    overall_score = sum(scores) / Decimal(len(scores))

    rounded_score = overall_score.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if rounded_score == rounded_score.to_integral():
        return f"{int(rounded_score)}%"

    return f"{rounded_score}%"


def calculate_control_result_score(
    control_results: list[dict],
) -> tuple[str, str]:
    """Average evidence-based scores for assessed controls and report basis.

    Unassessed controls and assessed controls without a numeric score are
    excluded. Overall WARNING/FAIL status is calculated separately.
    """
    assessed = [
        item for item in control_results
        if isinstance(item, dict) and item.get("assessment_status") == "assessed"
    ]
    scores: list[tuple[str, Decimal, str]] = []
    for item in assessed:
        raw_score = item.get("security_score")
        if not isinstance(raw_score, str) or not raw_score.strip().endswith("%"):
            continue
        try:
            score = Decimal(raw_score.strip()[:-1])
        except Exception:
            continue
        if Decimal("0") <= score <= Decimal("100"):
            scores.append((str(item.get("control", "control")), score,
                           str(item.get("security_score_basis", ""))))

    if not scores:
        return "N/A", "No assessed control returned a numeric validator score."

    average = (sum(score for _, score, _ in scores) / Decimal(len(scores))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    score_text = f"{int(average)}%" if average == average.to_integral() else f"{average}%"
    scored_controls = "; ".join(
        f"{control}={int(score) if score == score.to_integral() else score}%"
        + (f" ({basis})" if basis else "")
        for control, score, basis in scores
    )
    basis = (
        f"Mean of {len(scores)} scored assessed control(s): {scored_controls}. "
        f"{len(assessed) - len(scores)} assessed control(s) without numeric scores "
        "and all unassessed controls are excluded; overall status is reported separately."
    )
    return score_text, basis
