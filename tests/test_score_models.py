import daaily.score.models


class TestScoreModels:
    def test_constructor(self):
        pass

    def test_model_serilizable(self):
        score_weight = daaily.score.models.ScoreWeight("field_name", 0.0)
        assert score_weight.to_dict() == {"field_name": "field_name", "weight": 0.0}
        score_issues = daaily.score.models.ScoreResultIssues(1, ["grammar"], "text")
        assert score_issues.to_dict() == {
            "spelling": 1,
            "grammar": ["grammar"],
            "text": "text",
        }
        score_details = daaily.score.models.ScoreResultDetails(
            1.0, {"completeness": 1.0}, 1.0, 1.0, 1.0, 1.0
        )
        assert score_details.to_dict() == {
            "richness": 1.0,
            "completeness": {"completeness": 1.0},
            "length_factor": 1.0,
            "flesch": 1.0,
            "grammar": 1.0,
            "spelling": 1.0,
        }
        score_result = daaily.score.models.ScoreResult(
            "field_name", score_details, score_issues, 1.0, 0.0
        )
        assert score_result.to_dict() == {
            "field_name": "field_name",
            "details": {
                "richness": 1.0,
                "completeness": {"completeness": 1.0},
                "length_factor": 1.0,
                "flesch": 1.0,
                "grammar": 1.0,
                "spelling": 1.0,
            },
            "issues": {"spelling": 1, "grammar": ["grammar"], "text": "text"},
            "score": 1.0,
            "weight": 0.0,
        }
        score_summary = daaily.score.models.ScoreSummary([score_result], 1.0)
        assert score_summary.to_dict() == {
            "score_results": [
                {
                    "field_name": "field_name",
                    "details": {
                        "richness": 1.0,
                        "completeness": {"completeness": 1.0},
                        "length_factor": 1.0,
                        "flesch": 1.0,
                        "grammar": 1.0,
                        "spelling": 1.0,
                    },
                    "issues": {"spelling": 1, "grammar": ["grammar"], "text": "text"},
                    "score": 1.0,
                    "weight": 0.0,
                }
            ],
            "sum_score": 1.0,
        }
