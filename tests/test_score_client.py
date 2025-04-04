import unittest

from daaily.score import Product as ProductScore
from daaily.score import ScoreResultDetails, ScoreSummary
from daaily.score.models import ScoreResultIssues


class TestScores(unittest.TestCase):
    def setUp(self):
        self.product_score = ProductScore()

    def test_init(self):
        self.assertIsNotNone(self.product_score)
        self.assertEqual(self.product_score.type, "Product")
        self.assertEqual(self.product_score._sum, 1.0)

    def test_score_structure(self):
        product = {"text_en": "This is a test product"}
        score_summary = self.product_score.score(product)

        self.assertIsInstance(score_summary, ScoreSummary)
        self.assertGreater(score_summary.sum_score, 0.0)
        self.assertLessEqual(score_summary.sum_score, 1.0)
        self.assertIsInstance(score_summary.score_results[0].issues, ScoreResultIssues)
        self.assertIsNone(score_summary.score_results[0].details)

        assert "text_en" in [
            result.field_name for result in score_summary.score_results
        ]
        text_en_detail = None
        for result in score_summary.score_results:
            if result.field_name == "text_en":
                text_en_detail = result.details
                break
        if text_en_detail is None:
            self.fail("No details found")
        self.assertIsInstance(text_en_detail, ScoreResultDetails)
        self.assertIsInstance(text_en_detail.completeness, dict)
        self.assertIsInstance(text_en_detail.flesch, float)
        self.assertIsInstance(text_en_detail.richness, float)
        self.assertIsInstance(text_en_detail.grammar, float)
        self.assertEqual(text_en_detail.spelling, 1.0)
        self.assertEqual(text_en_detail.flesch, 1.0)
        self.assertEqual(text_en_detail.grammar, 1.0)

    def test_text_completeness(self):
        product = {
            "text_en": """The Grand Repos wing chair by Antonio Citterio offers 
        exceptional comfort and ergonomic support, solving the common problem
        of discomfort during extended sitting periods. Its synchronized mechanism
        concealed beneath the upholstery represents a breakthrough in seating design,
        supporting the user at every angle of inclination and locking in any position.
        
        Citterio's design philosophy combines timeless elegance with functional 
        innovation, creating a piece that serves as both a statement of luxury and a 
        tool for wellbeing. The designer's intent was to reimagine relaxation through 
        a modernist lens, challenging conventional notions of what a wing chair 
        could be.
        
        The experience of using the Grand Repos is transformative - once seated, the 
        user feels immediately embraced and supported. When paired with the Ottoman, 
        the chair creates a peaceful sanctuary that enhances any space with its 
        sophisticated presence. The plush upholstery available in various fabrics and 
        leather options provides a tactile quality that invites touch and promotes 
        relaxation.
        
        The Grand Repos fits perfectly in both residential settings and luxury office 
        environments, complementing contemporary interior design trends while serving 
        as an anchor piece. Its range of sizes - from 2 to 3 meters in length - allows 
        for versatile placement, with the 2.5-meter version being the most popular 
        choice for open-concept living spaces where it creates dialogue with 
        surrounding furniture while maintaining its commanding presence.
        """
        }
        score_summary = self.product_score.score(product)
        text_en_detail = None
        for result in score_summary.score_results:
            if result.field_name == "text_en":
                text_en_detail = result.details
                break
        if text_en_detail is None:
            self.fail("No details found")
        self.assertIsInstance(text_en_detail.completeness, dict)
        benefits = text_en_detail.completeness.get("benefits")
        design_concept = text_en_detail.completeness.get("design_concept")
        experience = text_en_detail.completeness.get("experience")
        context = text_en_detail.completeness.get("context")
        if not benefits or not design_concept or not experience or not context:
            self.fail("Completeness not found")
        self.assertGreater(benefits, 0.02)
        self.assertGreater(design_concept, 0.04)
        self.assertGreater(experience, 0.03)
        self.assertGreater(context, 0.003)

    def test_attributes_score(self):
        product = {
            "attributes": [
                {"name": "dimension_hight", "value": 100},
                {"name": "dimension_width", "value": 200},
                {"name": "dimension_length", "value": 300},
            ]
        }

        score_summary = self.product_score.score(product)
        attributes_result = None
        for result in score_summary.score_results:
            if result.field_name == "attributes":
                attributes_result = result
                break
        if attributes_result is None:
            self.fail("No details found")
        self.assertGreater(attributes_result.score, 0.2)

    def test_prices_score(self):
        product = {
            "prices": [
                {"ammount": 1000, "currency": "EUR"},
                {"ammount": 1250, "currency": "USD"},
            ],
        }

        score_summary = self.product_score.score(product)
        price_result = None
        for result in score_summary.score_results:
            if result.field_name == "prices":
                price_result = result
                break
        if price_result is None:
            self.fail("No details found")
        self.assertGreater(price_result.score, 0.99)

    def test_images_score(self):
        product = {
            "images": [
                {
                    "file_type": "image/jpeg",
                    "status": "online",
                    "image_usages": ["pro-b"],
                },
                {
                    "file_type": "image/png",
                    "status": "online",
                    "image_usages": ["pro-g"],
                },
                {
                    "file_type": "image/jpg",
                    "status": "online",
                    "image_usages": ["pro-g"],
                },
                {
                    "file_type": "image/gif",
                    "status": "online",
                    "image_usages": ["pro-d"],
                },
            ],
        }
        score_summary = self.product_score.score(product)
        image_result = None
        for result in score_summary.score_results:
            if result.field_name == "images":
                image_result = result
                break
        if image_result is None:
            self.fail("No details found")
        self.assertGreater(image_result.score, 0.8)
