import os
import re
from typing import TYPE_CHECKING, Iterable, List, Sequence

import requests

try:
    from wordfreq import available_languages, zipf_frequency  # type: ignore
    WORDFREQ_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    WORDFREQ_AVAILABLE = False

    def available_languages():  # type: ignore
        return []

    def zipf_frequency(word: str, language: str, minimum: float = -100):  # type: ignore
        # Simulate missing frequency data
        raise ValueError("wordfreq not available")

if TYPE_CHECKING:  # Avoid circular imports during runtime
    from premium_keyword_tool import KeywordData


class KeywordLanguageValidator:
    """Validate keywords against language frequency lists and optional LanguageTool API."""

    def __init__(
        self,
        default_language: str = "nl",
        min_frequency: float = 1.5,
        min_valid_ratio: float = 0.6,
    ) -> None:
        self.default_language = default_language
        self.min_frequency = min_frequency
        self.min_valid_ratio = min_valid_ratio

        self.supported_languages = set(available_languages()) if WORDFREQ_AVAILABLE else set()
        # normalized variants for ease of lookup (e.g. nl -> nl, nl-latn -> nl)
        self.language_aliases = {lang.split("_")[0]: lang for lang in self.supported_languages}

        # Optional LanguageTool configuration
        self.use_languagetool = self._env_flag("LANGUAGETOOL_ENABLED")
        self.languagetool_url = os.getenv(
            "LANGUAGETOOL_API_URL",
            "https://api.languagetool.org/v2/check",
        )
        self._session = requests.Session() if self.use_languagetool else None

    @staticmethod
    def _env_flag(name: str) -> bool:
        value = os.getenv(name, "0").lower()
        return value not in ("0", "false", "no", "")

    def filter_keyword_objects(
        self,
        keyword_objects: Sequence["KeywordData"],
        language: str | None = None,
    ) -> List["KeywordData"]:
        """Return keyword objects that appear valid in the requested language."""
        if not keyword_objects:
            return []

        lang_code = self._normalize_language(language)

        accepted: List["KeywordData"] = []
        fallback_candidates: List["KeywordData"] = []

        for keyword_obj in keyword_objects:
            if self._is_probably_language(keyword_obj.keyword, lang_code):
                accepted.append(keyword_obj)
            else:
                fallback_candidates.append(keyword_obj)

        if self.use_languagetool and fallback_candidates:
            accepted.extend(self._filter_with_languagetool(fallback_candidates, lang_code))

        # Preserve ordering based on original search volume sorting
        seen = set()
        filtered: List["KeywordData"] = []
        for obj in keyword_objects:
            if obj in accepted and obj.keyword not in seen:
                filtered.append(obj)
                seen.add(obj.keyword)

        return filtered

    def _normalize_language(self, language: str | None) -> str:
        if not language:
            return self.default_language

        lang = language.replace("_", "-").lower()
        if lang in self.supported_languages:
            return lang

        # handle codes like nl-NL or fr_FR
        base = lang.split("-")[0]
        if base in self.supported_languages:
            return base

        if base in self.language_aliases:
            return self.language_aliases[base]

        return self.default_language

    def _is_probably_language(self, phrase: str, language: str) -> bool:
        """Use wordfreq frequency tables to determine if phrase looks like the language."""
        words = re.findall(r"[\w'-]+", phrase.lower())
        words = [w for w in words if len(w) > 1]
        if not words:
            return False

        if WORDFREQ_AVAILABLE and self.supported_languages:
            frequencies: List[float] = []
            for word in words:
                freq = self._lookup_frequency(word, language)
                frequencies.append(freq)

            valid = [freq for freq in frequencies if freq >= self.min_frequency]
            if not valid:
                return False

            ratio = len(valid) / len(frequencies)
            return ratio >= self.min_valid_ratio
        else:
            # Fallback heuristic without wordfreq: accept if most tokens are alphabetic
            alpha_tokens = [w for w in words if re.fullmatch(r"[a-zA-ZÀ-ÿ\-']+", w) is not None]
            return len(alpha_tokens) / len(words) >= 0.6

    def _lookup_frequency(self, word: str, language: str) -> float:
        if not WORDFREQ_AVAILABLE:
            return -100

        try:
            freq = zipf_frequency(word, language, minimum=-100)
        except ValueError:
            freq = -100

        if freq >= self.min_frequency or language == self.default_language:
            return freq

        # Try base language (e.g. nl for nl_latn)
        base = language.split("-")[0]
        if base and base != language:
            try:
                freq = max(freq, zipf_frequency(word, base, minimum=-100))
            except ValueError:
                pass

        return freq

    def _filter_with_languagetool(
        self,
        keyword_objects: Sequence["KeywordData"],
        language: str,
    ) -> List["KeywordData"]:
        if not keyword_objects or not self._session:
            return []

        text = "\n".join(obj.keyword for obj in keyword_objects)
        offsets: List[tuple[int, int]] = []
        position = 0
        for obj in keyword_objects:
            start = position
            end = position + len(obj.keyword)
            offsets.append((start, end))
            position = end + 1  # account for newline

        try:
            response = self._session.post(
                self.languagetool_url,
                data={
                    "language": language,
                    "text": text,
                    "enabledOnly": "false",
                },
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []

        matches = payload.get("matches", [])
        invalid_indices = set()
        for match in matches:
            rule = match.get("rule", {})
            issue_type = rule.get("issueType")
            rule_id = rule.get("id", "")
            if issue_type in {"misspelling", "typographical"} or rule_id.startswith("MORFOLOGIK_"):
                offset = match.get("offset")
                if offset is None:
                    continue
                for idx, (start, end) in enumerate(offsets):
                    if start <= offset < end:
                        invalid_indices.add(idx)
                        break

        return [obj for idx, obj in enumerate(keyword_objects) if idx not in invalid_indices]

    def filter_keywords(
        self,
        keywords: Iterable[str],
        language: str | None = None,
    ) -> List[str]:
        """Convenience wrapper for raw keyword strings."""
        lang_code = self._normalize_language(language)
        accepted = []
        for keyword in keywords:
            if self._is_probably_language(keyword, lang_code):
                accepted.append(keyword)
        return accepted
