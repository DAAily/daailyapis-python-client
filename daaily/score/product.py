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
        """
        Score product images based on quality, variety, and completeness.

        This function evaluates a product's images based on three key image types,
        with each contributing differently to the final score:

        - pro-b: Main image (50% of score) - Critical product representation
        - pro-g: Gallery images (30% of score) - Additional views/angles
        - pro-d: Dimension image (20% of score) - Technical specifications visualization

        Scoring methodology:
        1. Main images: 0.5 points maximum (0.5 per image, capped at 1 image)
        2. Gallery images: 0.3 points maximum (0.06 per image, capped at 5 images)
        3. Dimension images: 0.2 points maximum (0.2 per image, capped at 1 image)
        4. Quality penalty: -0.05 points per low-resolution image

        A perfect score of 1.0 requires:
        - At least 1 main image (pro-b)
        - At least 5 gallery images (pro-g)
        - At least 1 dimension image (pro-d)
        - No low-resolution images

        The function also generates diagnostic information in the result details:
        - Completeness: Shows scores for each image type (normalized to 0-1 range)
        - Richness: Represents overall image quality after penalty adjustments
        - Length factor: Raw count of online images

        Parameters:
            field_name: Name of the field being scored
            weight: Weight of this field in the overall product score
            images: List of image dictionaries containing 'status' and
            'image_usages' keys
            _: Unused parameter (product record)

        Returns:
            ScoreResult: Score result (0-1 scale) with details and any issues found

        Issues reported:
            - Missing any of the three key image types
            - Presence of low-resolution images
            - No online images available
        """
        if not images:
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                score=0.0,
                issues=ScoreResultIssues(text="No images available"),
            )
        online_images = [image for image in images if image.get("status") == "online"]
        if not online_images:
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                score=0.0,
                issues=ScoreResultIssues(text="No online images available"),
            )
        pro_b_images = [
            image
            for image in online_images
            if any(usage == "pro-b" for usage in image.get("image_usages", []) or [])
        ]
        pro_g_images = [
            image
            for image in online_images
            if any(usage == "pro-g" for usage in image.get("image_usages", []) or [])
        ]
        pro_d_images = [
            image
            for image in online_images
            if any(usage == "pro-d" for usage in image.get("image_usages", []) or [])
        ]
        num_pro_b = len(pro_b_images)
        num_pro_g = len(pro_g_images)
        num_pro_d = len(pro_d_images)
        # Main image (pro-b) - Most important (max 0.5)
        main_image_score = min(0.5, num_pro_b * 0.5)
        # Gallery images (pro-g) - Score increases with more images, up to 5 (max 0.3)
        gallery_score = min(0.3, num_pro_g * 0.06)
        # Dimension image (pro-d) - Technical information (max 0.2)
        dimension_score = min(0.2, num_pro_d * 0.2)
        # Calculate total image score (0-1 range)
        total_score = main_image_score + gallery_score + dimension_score
        # Check image quality (detect any flagged low-quality images)
        low_quality_images = [
            image
            for image in online_images
            if image.get("image_error") in ["low_resolution"]
        ]
        # Penalize for low-quality images
        quality_penalty = len(low_quality_images) * 0.05
        adjusted_score = max(0, total_score - quality_penalty)
        issues_text = []
        if not pro_b_images:
            issues_text.append("Missing main product image (pro-b)")
        if not pro_g_images:
            issues_text.append("Missing gallery images (pro-g)")
        if not pro_d_images:
            issues_text.append("Missing dimension image (pro-d)")
        if low_quality_images:
            issues_text.append(f"Found {len(low_quality_images)} low quality images")
        issues_string = "; ".join(issues_text) if issues_text else None
        # - richness: represents overall image quality (0-1)
        # - completeness: represents coverage of different image types
        # - length_factor: represents the quantity of images relative to optimal
        # - flesch, grammar, spelling: not applicable to images, set to 0.0
        image_completeness = {
            "main_image": main_image_score / 0.5 if num_pro_b > 0 else 0.0,
            "gallery_images": gallery_score / 0.3 if num_pro_g > 0 else 0.0,
            "dimension_image": dimension_score / 0.2 if num_pro_d > 0 else 0.0,
            "image_quality": 1.0 - (quality_penalty * 2),
        }
        # Calculate richness as overall quality factor
        image_richness = max(0.0, 1.0 - (quality_penalty * 2))
        details = ScoreResultDetails(
            richness=image_richness,
            completeness=image_completeness,
            length_factor=len(online_images),
            flesch=0.0,
            grammar=0.0,
            spelling=0.0,
        )
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=adjusted_score,
            issues=ScoreResultIssues(text=issues_string) if issues_string else None,
            details=details,
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

    def score_attributes(  # noqa: C901
        self, field_name: str, weight: float, attributes: list[dict], _
    ) -> ScoreResult:
        """
        Score product attributes based on diversity across attribute types,
        with emphasis on material, dimension, and feature attributes.

        This function evaluates a product's attributes based on two key factors:
        1. Attribute type diversity (variety of different attribute categories)
        2. Presence of critical attribute types (material, dimension, feature)

        Scoring methodology (total 1.0 maximum):
        - Attribute diversity: 60% of score (0.6 points)
        * Score increases based on how many different attribute types are present
        * Maximum score for having 7 or more different attribute types

        - Critical attribute types: 30% of score (0.3 points)
        * Material attributes: 0.1 points if any present
        * Dimension attributes: 0.1 points if any present
        * Feature attributes: 0.1 points if any present

        - Primary dimensions bonus: 10% of score (0.1 points)
        * Height dimension: 0.033 points
        * Width dimension: 0.033 points
        * Length/depth/breadth dimension: 0.033 points

        The function categorizes attributes by examining the attribute name
        (e.g., "material_frame" would be categorized as "material").

        Parameters:
            field_name: Name of the field being scored
            weight: Weight of this field in the overall product score
            attributes: List of attribute dictionaries with 'name' and 'value' keys
            _: Unused parameter (product record)

        Returns:
            ScoreResult: Score result (0-1 scale) with details and any issues found
        """
        if not attributes:
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                score=0.0,
                issues=ScoreResultIssues(text="No attributes available"),
            )
        attribute_types = [
            "base",
            "category",
            "certification",
            "color",
            "dimension",
            "feature",
            "material",
        ]
        attribute_groups = {attr_type: [] for attr_type in attribute_types}
        uncategorized = []
        for attr in attributes:
            attr_name = attr.get("name", "").lower()
            attr_type = None
            for type_name in attribute_types:
                if attr_name.startswith(f"{type_name}_") or attr_name == type_name:
                    attr_type = type_name
                    break
            if attr_type:
                attribute_groups[attr_type].append(attr)
            else:
                uncategorized.append(attr)
        attribute_counts = {
            attr_type: len(attrs) for attr_type, attrs in attribute_groups.items()
        }
        # Check for primary dimensions (height, width, length/depth/breadth)
        dimension_attrs = attribute_groups["dimension"]
        has_height = any(
            attr.get("name", "").lower().endswith("_height")
            or "height" in attr.get("name", "").lower()
            for attr in dimension_attrs
        )
        has_width = any(
            attr.get("name", "").lower().endswith("_width")
            or "width" in attr.get("name", "").lower()
            for attr in dimension_attrs
        )
        has_length = any(
            attr.get("name", "").lower().endswith(("_length", "_depth", "_breadth"))
            or any(
                term in attr.get("name", "").lower()
                for term in ["length", "depth", "breadth"]
            )
            for attr in dimension_attrs
        )
        # Count how many different attribute types are present
        attr_types_present = sum(1 for count in attribute_counts.values() if count > 0)
        # Prioritize diversity of attribute types (60% of the score)
        # Maximum possible types is 7 (after combining color/colour)
        max_types = 7
        diversity_score = min(0.6, (attr_types_present / max_types) * 0.6)
        # Prioritize the three most important types: material, dimension,
        # feature (30% of the score)
        # Each is worth 10% of the total score if present
        priority_score = 0.0
        priority_weights = {"material": 0.1, "dimension": 0.1, "feature": 0.1}
        for attr_type, priority_weight in priority_weights.items():
            if attribute_counts[attr_type] > 0:
                priority_score += priority_weight
        # Bonus for having all three primary dimensions (10% of the score)
        dimension_completeness = sum([has_height, has_width, has_length])
        dimension_bonus = (dimension_completeness / 3) * 0.1
        # Calculate total score (0-1 range)
        total_score = diversity_score + priority_score + dimension_bonus
        # Prepare issues reporting
        issues_text = []
        # Check for missing important attribute types
        important_types = ["material", "dimension", "feature"]
        missing_important = [
            attr_type
            for attr_type in important_types
            if attribute_counts[attr_type] == 0
        ]
        if missing_important:
            issues_text.append(
                f"Missing important attribute types: {', '.join(missing_important)}"
            )
        # Check for missing primary dimensions
        if attribute_counts["dimension"] > 0 and dimension_completeness < 3:
            missing_dimensions = []
            if not has_height:
                missing_dimensions.append("height")
            if not has_width:
                missing_dimensions.append("width")
            if not has_length:
                missing_dimensions.append("length/depth/breadth")
            issues_text.append(
                f"Missing primary dimensions: {', '.join(missing_dimensions)}"
            )
        issues_string = "; ".join(issues_text) if issues_text else None
        completeness_details = {
            attr_type: 1.0 if attribute_counts[attr_type] > 0 else 0.0
            for attr_type in attribute_types
            if attr_type != "colour"  # Skip 'colour' as it's merged with 'color'
        }
        # Add dimension completeness specifically
        completeness_details["primary_dimensions"] = dimension_completeness / 3
        # Calculate overall richness based on attribute diversity
        richness = attr_types_present / max_types
        # Calculate length factor as proportion of attribute types present
        length_factor = attr_types_present / max_types
        details = ScoreResultDetails(
            richness=richness,
            completeness=completeness_details,
            length_factor=length_factor,
            flesch=0.0,
            grammar=0.0,
            spelling=0.0,
        )
        return ScoreResult(
            field_name=field_name,
            weight=weight,
            score=total_score,
            issues=ScoreResultIssues(text=issues_string) if issues_string else None,
            details=details,
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

    def score_live_link(
        self, field_name: str, weight: float, live_link: dict, _
    ) -> ScoreResult:
        if not live_link:
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                score=0.0,
                issues=ScoreResultIssues(text="No live link available"),
            )
        return ScoreResult(
            field_name=field_name, weight=weight, score=1 if live_link else 0
        )

    def score_text(
        self, field_name: str, weight: float, text: str, language: Language, _
    ) -> ScoreResult:
        """
        Score product text descriptions based on content quality, readability,
        and linguistic correctness.

        This function evaluates text descriptions across multiple dimensions to
        determine how well they represent the product. The scoring combines content
        relevance, readability, spelling, and grammar to provide a comprehensive
        assessment of text quality.

        Scoring methodology (total 1.0 maximum):
        - Content quality: 60% of score
        * Measures how well the text covers relevant topics defined in
        TEXT_SIMILARITY_TOPICS
        * Weighted by text richness (vocabulary diversity and structure)

        - Readability: 20% of score
        * Uses language-specific Flesch reading ease score
        * Adjusted and normalized to 0-1 scale

        - Formal correctness: 20% of score
        * Spelling: 10% (0.5 * 20%) - percentage of correctly spelled words
        * Grammar: 10% (0.5 * 20%) - quality of grammatical structure

        Topic evaluation criteria are defined in TEXT_SIMILARITY_TOPICS for each
        language and typically include:
        - Benefits and advantages of the product
        - Design philosophy and concept
        - User experience and feel
        - Product context and relation to environments

        Parameters:
            field_name: Name of the field being scored (e.g., "text_en", "text_de")
            weight: Weight of this field in the overall product score
            text: The product description text to evaluate
            language: Language enum indicating which language the text is in
            _: Unused parameter (product record)

        Returns:
            ScoreResult: Score result (0-1 scale) with detailed component scores
            and any issues found
        """
        if not text or len(text) < 10:
            text_issue = None
            if not text:
                text_issue = f"{field_name}==None"
            else:
                text_issue = f"{field_name} too short {len(text)} < 10"
            return ScoreResult(
                field_name=field_name,
                weight=weight,
                issues=ScoreResultIssues(text=text_issue),
            )
        balanced_score = self._calculate_balanced_richness(
            text, target_length=150, alpha=0.5, beta=0.5
        )
        language_similarity_topics = TEXT_SIMILARITY_TOPICS.get(language)
        if not language_similarity_topics:
            raise ValueError(
                f"Language {language} not supported for semantic similarity check. "
                f"Please add it. "
                f"Supported languages are: {list(TEXT_SIMILARITY_TOPICS.keys())}"
            )
        completeness_score, completeness_scores = self._semantic_similarity_check(
            text, language_similarity_topics
        )
        completeness = completeness_score * balanced_score.richness
        flesch = round(
            min(self._calculate_flesch_reading_ease(text, language) / 100, 1), 2
        )
        spelling_score, spelling_errors = self._calculate_spelling_score(text, language)
        spelling_score = round(min(spelling_score / 100, 1), 2)
        grammar_score, grammar_issues = self._grammar_check(
            text=text, language=language
        )
        completeness_weight = 0.6
        flesch_weight = 0.2
        formal_weight = 0.2
        score = (
            (completeness * completeness_weight)
            + (flesch * flesch_weight)
            + (spelling_score * formal_weight * 0.5)
            + (grammar_score * formal_weight * 0.5)
        )
        score_result = ScoreResult(
            field_name=field_name,
            weight=weight,
            score=score,
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
