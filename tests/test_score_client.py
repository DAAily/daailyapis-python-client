import unittest

from daaily.score import Product as ProductScore
from daaily.score import ScoreResultDetails, ScoreSummary


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
        self.assertIsNone(score_summary.score_results[0].issues)
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
        print(text_en_detail.flesch)
        self.assertEqual(text_en_detail.flesch, 1.0)
        self.assertEqual(text_en_detail.grammar, 1.0)

    def test_text_completeness(self):
        product = {
            "text_en": """The Grand Repos wing chair by Antonio Citterio offers 
                exceptional comfort for people at home and in luxury offices, 
                particularly when paired with the Ottoman. The synchronised mechanism
                concealed beneath the upholstery supports the user at every angle of
                inclination and can be locked in any position. Once the user is
                comfortably reclined, the Ottoman provides a soft foot rest for
                ultimate relaxation. You can get it in many types of fabrics and
                leather. The Grand Repos range from 2 meters to 3 meters in
                length, and the Grand Repos 2.5 meters is the most popular choice.
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
        mat = text_en_detail.completeness.get("material")
        usage = text_en_detail.completeness.get("usage")
        audience = text_en_detail.completeness.get("audience")
        dimension = text_en_detail.completeness.get("dimensions")
        if not mat or not usage or not audience or not dimension:
            self.fail("Completeness not found")
        self.assertGreater(mat, 0.001)
        self.assertGreater(usage, 0.01)
        self.assertGreater(audience, 0.0006)
        self.assertGreater(dimension, 0.01)

    def test_attributes_score(self):
        product = {
            "attributes": [
                {"name": "dimension_hight", "value": 100},
                {"name": "dimension_width", "value": 200},
                {"name": "dimension_length", "value": 300},
            ]
        }

        score_summary = self.product_score.score(product)
        atrributes_result = None
        for result in score_summary.score_results:
            print(f"Test Result: {result}")
            if result.field_name == "attributes":
                atrributes_result = result
                break
        if atrributes_result is None:
            self.fail("No details found")
        self.assertGreater(atrributes_result.score, 0.7)

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
                {"file_type": "image/jpeg"},
                {"file_type": "image/png"},
                {"file_type": "image/jpg"},
                {"file_type": "image/gif"},
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
        self.assertGreater(image_result.score, 0.99)
