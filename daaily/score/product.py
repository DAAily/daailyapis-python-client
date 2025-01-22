from daaily.score.client import Client
from daaily.score.constants import PRODUCT_WEIGHTS, TEXT_SIMILARITY_TOPICS
from daaily.score.models import (
    ScoreResult,
    ScoreResultDetails,
    ScoreResultIssues,
    ScoreWeight,
)


class Product(Client):
    def __init__(self):
        Client.__init__(
            self,
            type="Product",
            weights=[
                ScoreWeight(field_name=key, weight=PRODUCT_WEIGHTS[key])
                for key in PRODUCT_WEIGHTS
            ],
        )

    def score_internal_number(
        self, field_name: str, weight: float, _, record: dict
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1
            if record.get("internal_number") or record.get("article_number")
            else 0,
        )

    def score_images(
        self, field_name: str, weight: float, images: list[dict], _
    ) -> ScoreResult:
        _len = len(images or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 3 else 0 if _len == 0 else 0.8,
        )

    def score_family_id(
        self, field_name: str, weight: float, family_id: int, _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if family_id else 0
        )

    def score_group_ids(
        self, field_name: str, weight: float, group_ids: list[int], _
    ) -> ScoreResult:
        _len = len(group_ids or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 1 else 0 if _len == 0 else 0.8,
        )

    def score_materials(
        self, field_name: str, weight: float, materials: list[dict], _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if len(materials or []) > 0 else 0,
        )

    def score_attributes(
        self, field_name: str, weight: float, attributes: list[dict], _
    ) -> ScoreResult:
        _len = len(attributes or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 3 else 0 if _len == 0 else 0.8,
        )

    def score_collection_ids(
        self, field_name: str, weight: float, collection_ids: list[int], _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if len(collection_ids or []) > 1 else 0,
        )

    def score_3D(self, field_name: str, weight: float, _, record) -> ScoreResult:
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if record.get("pcon_config") or record.get("emersya_config") else 0,
        )

    def score_dimensions(
        self, field_name: str, weight: float, _, record
    ) -> ScoreResult:
        attributes = record.get("attributes") or []
        _len = len(
            [
                attribute["name"]
                for attribute in attributes
                if "dimension" in attribute["name"]
            ]
        )
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 1 else 0 if _len == 0 else 0.8,
        )

    def score_prices(
        self, field_name: str, weight: float, prices: list[dict], _
    ) -> ScoreResult:
        _len = len(prices or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 1 else 0 if _len == 0 else 0.8,
        )

    def score_pdfs(
        self, field_name: str, weight: float, pdf: list[dict], _
    ) -> ScoreResult:
        _len = len(pdf or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 1 else 0 if _len == 0 else 0.8,
        )

    def score_cads(self, field_name: str, weight: float, cads, _) -> ScoreResult:
        _len = len(cads or [])
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=1 if _len > 1 else 0 if _len == 0 else 0.8,
        )

    def score_text_en(
        self, field_name: str, weight: float, text_en: str, _
    ) -> ScoreResult:
        if not text_en or len(text_en) < 10:
            text_issue = None
            if not text_en:
                text_issue = "text_en==None"
            else:
                text_issue = f"text_en to short {len(text_en)} < 10"
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                issues=ScoreResultIssues(text=text_issue),
            )
        balanced_score = self._calculate_balanced_richness(
            text_en, target_length=150, alpha=0.5, beta=0.5
        )
        completeness_score, completness_scores = self._semantic_similarity_check(
            text_en, TEXT_SIMILARITY_TOPICS
        )
        completeness = completeness_score * balanced_score.richness
        flesch = round(min(self._calculate_flesch_reading_ease(text_en) / 100, 1), 2)
        spelling_score, spelling_errors = self._calculate_spelling_score(text_en)
        spelling_score = round(min(spelling_score / 100, 1), 2)
        grammar_score, grammar_issues = self._grammar_check(text_en)
        score_result = ScoreResult(
            field_name=field_name,
            weight=weight,
            score=completeness * flesch * spelling_score,
            details=ScoreResultDetails(
                richness=balanced_score.richness,
                completeness=completness_scores,
                length_factor=balanced_score.length_factor,
                flesch=flesch,
                grammar=grammar_score,
                spelling=spelling_score,
            ),
            issues=ScoreResultIssues(spelling=spelling_errors, grammar=grammar_issues),
        )
        return score_result
