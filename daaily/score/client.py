import io
import logging
import os
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


from daaily.enums import Language
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
        # https://www.sbert.net/docs/sentence_transformer/pretrained_models.html#semantic-similarity-models
        self._sentence_transformer_model = sentence_transformers.SentenceTransformer(
            "distiluse-base-multilingual-cased-v1"
        )
        self._spellchecker = spellchecker

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

    def _grammar_check(self, text: str, language: Language) -> tuple[float, list[str]]:
        """
        Perform a grammar check on the provided text using Google's NL API.

        Analyzes the syntax of the text and identifies grammar issues based on
        part-of-speech tags (e.g., X or CONJ). The grammar score is calculated as:

            grammar_score = 1 - (number_of_grammar_issues / total_tokens)

        If there are no tokens in the response, the score is 0.

        Parameters:
            text (str): The text to check for grammar issues.
            language (Language): The language of the text.

        Returns:
            tuple[float, list[str]]:
                - float: The grammar score (ranging from 0 to 1).
                - list[str]: A list of identified grammar issue lemmas.
        """
        text = self.re_encode(text)
        document = language_v1.Document(  # type: ignore
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT,  # type: ignore
            language=Language(language).value,
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

    def count_text_syllables(self, word: str, lang: Language) -> int:  # noqa: C901
        word = word.lower()
        if lang == Language.DE:
            vowels = "aeiouyäöü"
            diphthongs = ["ei", "ie", "eu", "äu", "au"]
        elif lang == Language.ES:
            vowels = "aeiouyáéíóúü"
            diphthongs = [
                "ai",
                "ei",
                "oi",
                "ui",
                "ia",
                "ie",
                "io",
                "iu",
                "ua",
                "ue",
                "uo",
            ]
        elif lang == Language.FR:
            vowels = "aeiouyéèêëàâîïôùûüÿç"
            diphthongs = ["ai", "ei", "oi", "ou", "au", "eu"]
        elif lang == Language.IT:
            vowels = "aeiouyàèéìíòóùú"
            diphthongs = ["ai", "ei", "oi", "ui", "ia", "ie", "io", "iu"]
        else:  # Default to English
            vowels = "aeiouy"
            diphthongs = [
                "ai",
                "ay",
                "ea",
                "ee",
                "ei",
                "ey",
                "ie",
                "oa",
                "oe",
                "oi",
                "oo",
                "ou",
                "oy",
                "ui",
                "uy",
            ]
        num_syllables = 0
        prev_char_was_vowel = False
        i = 0
        while i < len(word):
            # Check for diphthongs (count as one syllable)
            is_diphthong = False
            if i < len(word) - 1:
                potential_diphthong = word[i : i + 2]
                if potential_diphthong in diphthongs:
                    if (
                        not prev_char_was_vowel
                    ):  # Avoid counting overlapping vowels twice
                        num_syllables += 1
                    prev_char_was_vowel = True
                    is_diphthong = True
                    i += 2
                    continue
            # If not a diphthong, check single letters
            if not is_diphthong:
                if word[i] in vowels:
                    if not prev_char_was_vowel:
                        num_syllables += 1
                    prev_char_was_vowel = True
                else:
                    prev_char_was_vowel = False
                i += 1
        # Language-specific end-of-word rules
        if lang == Language.EN and word.endswith("e"):
            num_syllables = max(1, num_syllables - 1)
        elif lang == Language.FR and (
            word.endswith("e") or word.endswith("es") or word.endswith("ent")
        ):
            # In French, final 'e', 'es', 'ent' are often silent
            num_syllables = max(1, num_syllables - 1)
        return max(1, num_syllables)

    def _calculate_flesch_reading_ease(self, text: str, language: Language) -> float:
        """
        Calculate the Flesch Reading Ease score for the given text with
        language-specific adaptations. Higher scores indicate easier readability.

        The original Flesch formula is optimized for English. This implementation
        includes language-specific adjustments for German, Spanish, French, and Italian.

        Parameters:
            text (str): The text to analyze.
            language (Language): The language of the text.

        Returns:
            float: Adjusted Flesch Reading Ease score.
        """
        sentence_terminators = r"[.!?]"
        if language == Language.ES:
            sentence_terminators = r"[.!?¡¿]"
        sentences = re.split(sentence_terminators, text)
        num_sentences = len([s for s in sentences if s.strip()])
        if language == Language.DE:
            # German has compound words that should be counted differently
            # This simple approach splits compound words with hyphens
            text_for_word_count = text.replace("-", " ")
            words = re.findall(r"\w+", text_for_word_count)
        else:
            words = re.findall(r"\w+", text)
        num_words = len(words)
        num_syllables = sum(self.count_text_syllables(word, language) for word in words)
        if num_sentences == 0 or num_words == 0:
            return 0.0
        words_per_sentence = num_words / num_sentences
        syllables_per_word = num_syllables / num_words
        # Base Flesch calculation
        flesch_score = (
            206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        )
        if language == Language.DE:
            # German typically scores lower due to longer words and sentences
            # The Flesch formula for German actually requires different coefficients
            # Amstad's adaptation for German:
            # 180 - (1 * words_per_sentence) - (58.5 * syllables_per_word)
            flesch_score = (
                180 - (1.0 * words_per_sentence) - (58.5 * syllables_per_word)
            )
        elif language == Language.IT:
            # Tends to have more syllables per word than English
            flesch_score = (
                217 - (1.3 * words_per_sentence) - (60.0 * syllables_per_word)
            )
        elif language == Language.FR:
            flesch_score = (
                207 - (1.015 * words_per_sentence) - (73.6 * syllables_per_word)
            )
        elif language == Language.ES:
            flesch_score = (
                206.835 - (1.02 * words_per_sentence) - (60.0 * syllables_per_word)
            )
        flesch_score = max(0, min(100, flesch_score))
        return round(flesch_score, 2)

    def _semantic_similarity_check(
        self, text: str, topics: dict[str, tuple[str, float]]
    ) -> tuple[float, dict[str, float]]:
        from sentence_transformers import util

        """
        Check the semantic similarity of the text to defined topic descriptions.
        
        Parameters:
            text (str): The text to analyze.
            topics (dict): A dictionary of topics and their descriptions.

        Returns:
            tuple: (overall_score, dictionary showing similarity scores for each topic)
        """
        scores = {}
        total_score = 0
        for topic, data in topics.items():
            description = data[0]
            weight = data[1]
            embeddings = self._sentence_transformer_model.encode(
                [text, description], show_progress_bar=False
            )
            similarity = util.cos_sim(embeddings[0], embeddings[1])
            raw_similarity = float(similarity.item())
            positive_similarity = max(0, raw_similarity)
            scores[topic] = positive_similarity * weight
            total_score += scores[topic]
        return total_score, scores

    def _calculate_spelling_score(
        self, text: str, language: Language
    ) -> tuple[float, int]:
        """
        Calculate a spelling score for the input text with improved tokenization
        for different languages.

        Parameters:
            text (str): The input text to evaluate.
            language (Language): The language of the text.

        Returns:
            tuple: A score for spelling (0-100) and the number of misspelled words
        """
        if language == Language.DE:
            word_pattern = r"\b[a-zA-ZäöüÄÖÜß]+\b"
        elif language == Language.IT:
            word_pattern = r"\b[a-zA-ZàèéìíòóùúÀÈÉÌÍÒÓÙÚ]+\b"
        elif language == Language.FR:
            word_pattern = r"\b[a-zA-ZàâæçéèêëîïôœùûüÿÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ]+\b"
        elif language == Language.ES:
            word_pattern = r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b"
        else:
            word_pattern = r"\b[a-zA-Z]+\b"
        words = re.findall(word_pattern, text)
        words = [word for word in words if len(word) > 1 and not word.isdigit()]
        words = [word for word in words if word]
        total_words = len(words)
        if total_words == 0:
            return 0, 0
        spell_client = self._spellchecker.SpellChecker(
            language=language.value,
            local_dictionary=os.path.join(
                os.path.dirname(__file__),
                f"resources/spellchecker/{language.value}.json.gz",
            ),
            case_sensitive=False,
        )
        misspelled = spell_client.unknown(words)
        spelling_errors = len(misspelled)
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

        There is a special case for text fields, where the scoring function
        `score_text` is called. This function handles the text scoring logic,
        including language detection and semantic similarity checks.

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
            if w.field_name.startswith("text_"):
                language_raw = w.field_name.split("_")[1]
                try:
                    language = Language(language_raw)
                except ValueError:
                    logging.warning(
                        f"Language {language_raw} not supported, skipping text score"
                    )
                    continue
                score_results = self.score_text(  # type: ignore
                    w.field_name, w.weight, data.get(w.field_name), language, data
                )
                score_summary.score_results.append(score_results)
            else:
                score_func = f"score_{w.field_name}"
                if hasattr(self, score_func):
                    score_results = getattr(self, score_func)(
                        w.field_name, w.weight, data.get(w.field_name), data
                    )
                    score_summary.score_results.append(score_results)
                else:
                    logging.warning(
                        "No score function found for "
                        + f"{w.field_name} in {self.type} score"
                    )
        score_summary.calculate_sum_score()
        return score_summary
