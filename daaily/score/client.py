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


from abc import ABC, abstractmethod

from daaily.enums import Language
from daaily.score.models import BalancedScore, ScoreResult, ScoreSummary, ScoreWeight


class Client(ABC):
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
        """
        Count the number of syllables in a word with language-specific rules.

        This function implements a sophisticated syllable counting algorithm that
        accounts for language-specific phonetic patterns:

        1. Language-specific character sets:
        - Different vowel sets for each language (including accented characters)
        - Language-specific diphthongs (vowel combinations that count as one syllable)

        2. Syllable counting process:
        - Iterates through the word character by character
        - Checks for diphthongs first (two-character vowel combinations)
        - If not a diphthong, checks if the current character is a vowel
        - Avoids double-counting consecutive vowels
        - Handles special cases like silent 'e' in English

        3. End-of-word rules:
        - English: Silent 'e' at the end reduces syllable count by 1
        - French: Silent 'e', 'es', or 'ent' at the end reduces syllable count by 1

        4. Minimum syllables:
        - Ensures every word has at least 1 syllable, even if no vowels are detected

        The algorithm works by tracking vowel transitions (consonant->vowel) rather than
        simply counting vowels, which provides more accurate syllable counts
        across languages.

        Parameters:
            word (str): The word to analyze
            lang (Language): The language of the word

        Returns:
            int: The number of syllables in the word (minimum 1)
        """
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
        Calculate the Flesch Reading Ease score with language-specific adaptations.

        This function implements a multilingual Flesch Reading Ease calculator that:

        1. Segments text into sentences:
        - Uses language-specific sentence terminators (adds ¡¿ for Spanish)
        - Counts non-empty sentences only

        2. Tokenizes text into words:
        - Handles compound words in German by splitting on hyphens
        - Uses appropriate word boundary patterns for each language

        3. Counts syllables:
        - Uses language-specific syllable counting rules via count_text_syllables()
        - Accounts for diphthongs, accented vowels, and special cases

        4. Applies language-specific Flesch formulas
        (https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests):
        - English (original): 206.835 - (1.015 x words/sentence) -
          (84.6 x syllables/word)
        - German (Amstad): 180 - (1.0 x words/sentence) - (58.5 x syllables/word)
        - Italian: 217 - (1.3 x words/sentence) - (60.0 x syllables/word)
        - French: 207 - (1.015 x words/sentence) - (73.6 x syllables/word)
        - Spanish: 206.835 - (1.02 x words/sentence) - (60.0 x syllables/word)

        5. Normalizes the result:
        - Ensures score is within 0-100 range
        - Rounds to 2 decimal places

        The resulting score indicates text readability (higher = easier to read).

        Parameters:
            text (str): The text to analyze
            language (Language): The language of the text

        Returns:
            float: The adjusted Flesch Reading Ease score (0-100)
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
        Evaluate how well a text matches predefined topics using semantic similarity.
        
        This function uses transformer-based sentence embeddings to measure the 
        semantic relationship between product text and topic descriptions. 
        
        The process works as follows:
        
        1. Embedding generation:
        - Converts both the input text and each topic description into numerical vectors
        - Uses a pre-trained sentence transformer model
        - Creates embeddings that capture semantic meaning beyond keywords
        
        2. Similarity calculation:
        - Computes cosine similarity between text and topic embeddings
        - Ranges from -1 (completely dissimilar) to 1 (identical meaning)
        - Ensures non-negative by applying max(0, similarity)
        
        3. Weighted scoring:
        - Each topic has an importance weight (e.g., material: 0.3, usage: 0.3)
        - Multiplies raw similarity by topic weight
        - Aggregates weighted scores into a total completeness score
        
        This approach enables detecting semantic matches even when exact keywords 
        aren't present. For example, "crafted from oak" would match a "materials" 
        topic even without the word "material" being present.
        
        Parameters:
            text (str): The product text to analyze
            topics (dict): Dictionary mapping topic names to 
            (description, weight) tuples
            
        Returns:
            tuple: (total_score, {topic_name: weighted_score, ...})
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
        Calculate spelling accuracy for a text in a specific language.

        This function analyzes text for spelling errors using
        language-specific dictionaries.

        The implementation:

        1. Text tokenization:
        - Uses a universal Unicode-aware pattern to identify words
        - Excludes numbers, punctuation, and special characters
        - Filters out very short words (length 1) to reduce false positives

        2. Dictionary-based spell checking:
        - Uses language-specific dictionaries stored as compressed JSON files
        - Loads the appropriate dictionary based on the language parameter
        - Identifies words not found in the dictionary as potential misspellings

        3. Score calculation:
        - Calculates the percentage of correctly spelled words
        - Score = 100 - (error_count / total_words * 100)
        - Returns both the score and the count of misspellings

        The spell checker uses local dictionaries to ensure consistent results.

        Parameters:
            text (str): The text to analyze for spelling errors
            language (Language): The language of the text

        Returns:
            tuple: (spelling_score (0-100), misspelled_word_count)
        """
        # Universal pattern to split by on non-alphanumeric and non-accented characters
        words = re.findall(r"\b[^\s\d\W]+\b", text, re.UNICODE)
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

    @abstractmethod
    def score_text(
        self, field_name: str, weight: float, text: str, language: Language, data: dict
    ) -> ScoreResult:
        """Method that must be implemented by subclasses"""
        pass

    def score(self, data) -> ScoreSummary:
        """
        Calculate a comprehensive product score based on multiple weighted factors.

        This orchestration function coordinates the scoring process by:

        1. Weight-based scoring:
        - Uses the weights defined for each specific entity
        - Each field is scored independently by specialized scoring functions
        - Weighted scores are combined for a final product score

        2. Scoring function discovery and dispatch:
        - Dynamically finds scoring methods using naming convention: score_<field_name>
        - Handles text fields specially via the score_text abstract method
        - Skips any fields with missing scoring functions

        3. Language handling for text fields:
        - Parses language code from field name (e.g., text_en → 'en')
        - Validates language support

        4. Result aggregation:
        - Collects individual field scores into a ScoreSummary
        - Calculates final weighted sum of all scores

        This approach allows for modular scoring where fields can be added or
        removed without changing the core scoring logic.

        Parameters:
            data (dict): Product data dictionary with fields matching weight keys

        Returns:
            ScoreSummary: Complete scoring results with overall and
            field-specific scores

        Raises:
            ValueError: If no weights are defined for scoring
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
                score_results = self.score_text(
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
