import io
import logging
import re

try:
    from google.cloud import language_v1
except ImportError:
    language_v1 = None
try:
    import sentence_transformers
except ImportError:
    sentence_transformers = None
try:
    import spellchecker
except ImportError:
    spellchecker = None


from daaily.score.models import BalancedScore, ScoreSummary, ScoreWeight


class Client:
    def __init__(
        self, type: str | None = None, weights: list[ScoreWeight] | None = None
    ):
        """
        Initialize the Client instance which provides various scoring methods.

        Parameters:
            type (str, optional): A label or identifier for the client, e.g. "Product".
            weights (list[ScoreWeight], optional): A list of ScoreWeight objects
                defining the scoring criteria and their respective weights.

        Raises:
            ImportError: If any of the required extra dependencies
                (google-cloud-language, sentence-transformers, spellchecker)
                are not installed.
        """
        self.weights = weights
        self.type = type
        self._sum = round(sum([w.weight for w in weights or []]), 6)
        if not self._sum == 1:
            logging.warning(
                f"{self.type} score weights do not sum up to 1.0, sum is {self._sum} "
                + "instead of 1.0"
            )

        if language_v1 is None or sentence_transformers is None or spellchecker is None:
            raise ImportError(
                "Some extra dependency is not installed.\n"
                "Please add extra dependency like so:\n\n"
                "#egg=daaily[score]\n"
            )

        self._lang_client = language_v1.LanguageServiceClient()
        self._sentence_transformer_model = sentence_transformers.SentenceTransformer(
            "bert-base-nli-mean-tokens"
        )
        self._spell = spellchecker.SpellChecker()

    def re_encode(self, text: str) -> str:
        """
        Re-encode the text with the proper encoding.

        Texts need re-encoding because it comes from different sources and might have
        different encodings, such as raw MongoDB data.

        Issue: https://github.com/googleapis/google-cloud-python/issues/11381

        Parameters:
            text (str): The text to re-encode.

        Returns:
            str: The re-encoded text.
        """
        bytes_object = io.BytesIO(text.encode("utf-8"))
        text_io = io.TextIOWrapper(bytes_object, encoding="utf-8-sig")
        return text_io.read().strip()

    def _grammar_check(self, text: str, language_iso: str) -> tuple[float, list[str]]:
        """
        Perform a grammar check on the provided text using Google's NL API.

        Analyzes the syntax of the text and identifies grammar issues based on
        part-of-speech tags (e.g., X or CONJ). The grammar score is calculated as:

            grammar_score = 1 - (number_of_grammar_issues / total_tokens)

        If there are no tokens in the response, the score is 0.

        Parameters:
            text (str): The text to check for grammar issues.
            language_iso (str): The ISO code for the language of the text.

        Returns:
            tuple[float, list[str]]:
                - float: The grammar score (ranging from 0 to 1).
                - list[str]: A list of identified grammar issue lemmas.
        """
        text = self.re_encode(text)
        document = language_v1.Document(  # type: ignore
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT,  # type: ignore
            language=language_iso,
        )
        response = self._lang_client.analyze_syntax(
            document=document,
            encoding_type=language_v1.EncodingType.UTF8,  # type: ignore
        )
        grammar_issues = []
        for token in response.tokens:
            if token.part_of_speech.tag in (
                language_v1.PartOfSpeech.Tag.X,  # type: ignore
                language_v1.PartOfSpeech.Tag.CONJ,  # type: ignore
            ):
                grammar_issues.append(token.lemma)
        score = (
            1 - len(grammar_issues) / len(response.tokens)
            if len(response.tokens) > 0
            else 0
        )
        return score, grammar_issues

    def _calculate_balanced_richness(
        self, text: str, target_length=100, alpha=0.6, beta=0.4
    ) -> BalancedScore:
        """
        Calculate a balanced score for text based on vocabulary richness and length.

        Parameters:
            text (str): The input text.
            target_length (int): Desired target length for the text.
            alpha (float): Weight for richness in the score.
            beta (float): Weight for length in the score.

        Returns:
            float: Balanced score for the text.
        """
        words = text.split()
        total_words = len(words)
        unique_words = len({word.lower().strip(".,!?\"'()[]") for word in words})
        richness = unique_words / total_words if total_words > 0 else 0.0
        length_factor = min(1.0, total_words / target_length)
        return BalancedScore(richness, length_factor, alpha, beta)

    def _calculate_flesch_reading_ease(self, text: str) -> float:
        """
        How It Works:
        Sentence Count: Splits the text into sentences using common punctuation (.,!,?).
        Word Count: Identifies words using regex (\\w+).
        Syllable Count: Counts syllables per word by checking vowels and handling edge
        cases like trailing "e".

        Flesch Formula:
        Flesch Score = 206.835-(1.015 x Words per Sentence)-(84.6 x Syllables per Word)

        Calculate the Flesch Reading Ease score for the given text.
        Higher scores indicate easier readability.

        Parameters:
            text (str): The text to analyze.

        Returns:
            float: Flesch Reading Ease score.
        """
        # Count sentences
        sentences = re.split(r"[.!?]", text)
        num_sentences = len([s for s in sentences if s.strip()])
        # Count words
        words = re.findall(r"\w+", text)
        num_words = len(words)

        # Count syllables
        def count_syllables(word: str) -> int:
            word = word.lower()
            vowels = "aeiouy"
            num_syllables = 0
            prev_char_was_vowel = False
            for char in word:
                if char in vowels:
                    if not prev_char_was_vowel:
                        num_syllables += 1
                    prev_char_was_vowel = True
                else:
                    prev_char_was_vowel = False
            if word.endswith("e"):
                num_syllables = max(1, num_syllables - 1)
            return max(1, num_syllables)

        num_syllables = sum(count_syllables(word) for word in words)
        # Flesch Reading Ease formula
        if num_sentences == 0 or num_words == 0:
            return 0.0  # Avoid division by zero
        flesch_score = (
            206.835
            - (1.015 * (num_words / num_sentences))
            - (84.6 * (num_syllables / num_words))
        )
        return round(flesch_score, 2)

    def _semantic_similarity_check(
        self, text: str, topics: dict[str, tuple[str, float]]
    ) -> tuple[float, dict[str, float]]:
        from sentence_transformers import util

        """
        Check the semantic similarity of the text to defined topic descriptions.
        Not working as expected. The scores are very small, needs investigation how
        this lib is working

        Parameters:
            text (str): The text to analyze.
            topics (dict): A dictionary of topics and their descriptions.

        Returns:
            dict: A dictionary showing similarity scores for each topic.
        """
        scores = {}
        score = 0
        for topic, data in topics.items():
            description = data[0]
            weight = data[1]
            embeddings = self._sentence_transformer_model.encode(
                [text, description], show_progress_bar=False
            )
            similarity = util.cos_sim(embeddings[0], embeddings[1])
            scores[topic] = (
                float(similarity.item()) * weight
            )  # Convert tensor to Python float
            score += max(scores[topic], 0)
        return score, scores

    def _calculate_spelling_score(self, text: str) -> tuple[float, int]:
        """
        Calculate a spelling score for the input text.

        Parameters:
            text (str): The input text to evaluate.

        Returns:
            dict: A score for spelling
        """
        # Tokenize the text into words
        words = text.split()
        total_words = len(words)
        if total_words == 0:
            return 0, 0
        misspelled = self._spell.unknown(words)
        spelling_errors = len(misspelled)
        # Scores
        spelling_score = max(0, 100 - (spelling_errors / total_words * 100))
        return spelling_score, spelling_errors

    def score(self, data) -> ScoreSummary:
        """
        Compute an overall score for the provided data based on defined weights and
        corresponding scoring methods.

        Iterates through each defined ScoreWeight and looks for a scoring function
        in this class named `score_<field_name>`. If found, that function is called
        with the corresponding data. The results are collected into a ScoreSummary
        object, which is then finalized by calculating the total score.

        Parameters:
            data (dict): The data dictionary that contains values associated with each
                field_name in the weights. These values are passed to the respective
                scoring methods.

        Returns:
            ScoreSummary: A summary object that contains individual scoring results and
            the cumulative score.

        Raises:
            ValueError: If no weights are defined for the score.
        """
        score_summary = ScoreSummary([])
        if not self.weights:
            raise ValueError("No weights defined for the score")
        for w in self.weights:
            if w.field_name == "_":  # skip the _ key
                continue
            score_func = f"score_{w.field_name}"
            if hasattr(self, score_func):
                score_results = getattr(self, score_func)(
                    w.field_name, w.weight, data.get(w.field_name), data
                )
                score_summary.score_results.append(score_results)
            else:
                logging.warning(
                    f"No score function found for {w.field_name} in {self.type} score"
                )
        score_summary.calculate_sum_score()
        return score_summary
