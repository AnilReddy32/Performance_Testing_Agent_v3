from decimal import Decimal, ROUND_HALF_UP

from security_agent.models.assessment import SecurityAssessment
from security_agent.models.response import SecurityStatus


def calculate_security_score(
    assessments: list[SecurityAssessment],
) -> str:
    """
    Calculate an overall security score from completed assessments.

    Rules:
    - No assessments -> N/A
    - Any WARNING -> N/A
    - Any invalid/missing score -> N/A
    - Otherwise, calculate the arithmetic mean of assessment scores.
    """

    if not assessments:
        return "N/A"

    if any(
        assessment.result == SecurityStatus.WARNING
        for assessment in assessments
    ):
        return "N/A"

    scores: list[Decimal] = []

    for assessment in assessments:
        score = assessment.security_score.strip()

        if score.upper() == "N/A":
            return "N/A"

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