from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BalancedScore:
    def __init__(self, richness, length_factor, alpha: float, beta: float):
        self.richness = richness
        self.length_factor = length_factor
        self.alpha = alpha
        self.beta = beta

    def calculate_balanced_score(self):
        return (self.alpha * self.richness) * (self.beta * self.length_factor)


@dataclass
class ScoreWeight(Serializable):
    field_name: str
    weight: float


@dataclass
class ScoreResultIssues(Serializable):
    spelling: int | None = None
    grammar: list[str] | None = None
    text: str | None = None


@dataclass
class ScoreResultDetails(Serializable):
    richness: float
    completeness: dict[str, float]
    length_factor: float
    flesch: float
    grammar: float
    spelling: float


@dataclass
class ScoreResult(Serializable):
    field_name: str
    details: ScoreResultDetails | None = None
    issues: ScoreResultIssues | None = None
    score: float = 0.0
    weight: float = 0.0


@dataclass
class ScoreSummary(Serializable):
    score_results: list[ScoreResult]
    sum_score: float = 0.0

    def calcuate_sum_score(self):
        for score in self.score_results:
            self.sum_score += score.score * score.weight
