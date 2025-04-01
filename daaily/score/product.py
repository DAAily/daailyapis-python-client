from daaily.enums import Language
from daaily.score.client import Client
from daaily.score.constants import PRODUCT_WEIGHTS, TEXT_SIMILARITY_TOPICS
from daaily.score.models import (
    ScoreResult,
    ScoreResultDetails,
    ScoreResultIssues,
    ScoreWeight,
)
from daaily.score.utils import compute_score


class Product(Client):
    def __init__(self, score_weights: dict | None = None):
        score_weights = score_weights or PRODUCT_WEIGHTS
        weights = [
            ScoreWeight(field_name=key, weight=score_weights[key])
            for key in score_weights
        ]
        super().__init__(type="Product", weights=weights)

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

    def score_article_number(
        self, field_name: str, weight: float, article_number: str, _: dict
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if article_number else 0
        )

    def score_launch_date(
        self, field_name: str, weight: float, launch_date: str, _: dict
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if launch_date else 0
        )

    def score_design_year(
        self, field_name: str, weight: float, design_year: int, _: dict
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if design_year else 0
        )

    def score_designer_names(
        self, field_name: str, weight: float, designer_names: list[str], _
    ) -> ScoreResult:
        _len = len(designer_names or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_images(
        self, field_name: str, weight: float, images: list[dict], _
    ) -> ScoreResult:
        _len = len(images or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 3)
        )

    def score_family_id(
        self, field_name: str, weight: float, family_id: int, _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if family_id else 0
        )

    def score_family_name(
        self, field_name: str, weight: float, family_name: int, _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if family_name else 0
        )

    def score_group_ids(
        self, field_name: str, weight: float, group_ids: list[int], _
    ) -> ScoreResult:
        _len = len(group_ids or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_materials(
        self, field_name: str, weight: float, materials: list[dict], _
    ) -> ScoreResult:
        _len = len(materials or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 0)
        )

    def score_attributes(
        self, field_name: str, weight: float, attributes: list[dict], _
    ) -> ScoreResult:
        _len = len(attributes or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 3)
        )

    def score_collection_ids(
        self, field_name: str, weight: float, collection_ids: list[int], _
    ) -> ScoreResult:
        _len = len(collection_ids or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_collection_names(
        self, field_name: str, weight: float, collection_names: list[str], _
    ) -> ScoreResult:
        _len = len(collection_names or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_master_variant_name(
        self, field_name: str, weight: float, master_variant_name: str, _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if master_variant_name else 0
        )

    def score_category(
        self, field_name: str, weight: float, category: str, _
    ) -> ScoreResult:
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if category else 0
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
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_prices(
        self, field_name: str, weight: float, prices: list[dict], _
    ) -> ScoreResult:
        _len = len(prices or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_pdfs(
        self, field_name: str, weight: float, pdf: list[dict], _
    ) -> ScoreResult:
        _len = len(pdf or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_cads(self, field_name: str, weight: float, cads, _) -> ScoreResult:
        _len = len(cads or [])
        return ScoreResult(
            field_name=field_name, weight=weight, score=compute_score(_len, 1)
        )

    def score_text(
        self, field_name: str, weight: float, text: str, language: Language, _
    ) -> ScoreResult:
        if not text or len(text) < 10:
            text_issue = None
            if not text:
                text_issue = f"{field_name}==None"
            else:
                text_issue = f"{field_name} to short {len(text)} < 10"
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                issues=ScoreResultIssues(text=text_issue),
            )
        balanced_score = self._calculate_balanced_richness(
            text, target_length=150, alpha=0.5, beta=0.5
        )
        completeness_score, completeness_scores = self._semantic_similarity_check(
            text, TEXT_SIMILARITY_TOPICS
        )
        completeness = completeness_score * balanced_score.richness
        flesch = round(min(self._calculate_flesch_reading_ease(text) / 100, 1), 2)
        spelling_score, spelling_errors = self._calculate_spelling_score(text)
        spelling_score = round(min(spelling_score / 100, 1), 2)
        grammar_score, grammar_issues = self._grammar_check(
            text=text, language_iso=Language(language).value
        )
        score_result = ScoreResult(
            field_name=field_name,
            weight=weight,
            score=completeness * flesch * spelling_score,
            details=ScoreResultDetails(
                richness=balanced_score.richness,
                completeness=completeness_scores,
                length_factor=balanced_score.length_factor,
                flesch=flesch,
                grammar=grammar_score,
                spelling=spelling_score,
            ),
            issues=ScoreResultIssues(spelling=spelling_errors, grammar=grammar_issues),
        )
        return score_result
