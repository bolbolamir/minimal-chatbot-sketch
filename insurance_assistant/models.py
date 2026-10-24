"""Small executable ML baseline: text-vector retrieval and nearest-state policy."""

import math
import re
from collections import Counter
from typing import Protocol

from . import data
from .domain import Action, ActionKind, CarUpdates, Conversation, Intent, Understanding


def normalize(text: str) -> str:
    table = str.maketrans("يكة۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "یکه01234567890123456789")
    return " ".join(text.translate(table).replace("\u200c", " ").split()).lower()


class TextIndex:
    """Fit TF-IDF character vectors; cosine search tolerates some spelling variation.

    This is a lexical baseline, not a pretrained semantic embedding model.
    Similarities are retrieval scores, not calibrated probabilities.
    """

    def __init__(self, texts: list[str]) -> None:
        counts = [self._counts(text) for text in texts]
        frequency = Counter(token for count in counts for token in count)
        self.idf = {token: math.log((1 + len(texts)) / (1 + n)) + 1 for token, n in frequency.items()}
        self.unknown_idf = math.log(1 + len(texts)) + 1
        self.vectors = [self._vector(count) for count in counts]

    @staticmethod
    def _counts(text: str) -> Counter[str]:
        text = normalize(text)
        return Counter(text[i : i + n] for n in (2, 3, 4) for i in range(len(text) - n + 1))

    def _vector(self, counts: Counter[str]) -> dict[str, float]:
        vector = {token: count * self.idf.get(token, self.unknown_idf) for token, count in counts.items()}
        length = math.sqrt(sum(value * value for value in vector.values())) or 1
        return {token: value / length for token, value in vector.items()}

    def search(self, text: str) -> tuple[int, float]:
        query = self._vector(self._counts(text))
        scores = [
            sum(value * candidate.get(token, 0) for token, value in query.items())
            for candidate in self.vectors
        ]
        index = max(range(len(scores)), key=scores.__getitem__)
        return index, scores[index]


class UnderstandingModel(Protocol):
    def predict(self, *, text: str, conversation: Conversation) -> Understanding: ...


class ActionModel(Protocol):
    def predict(self, *, meaning: Understanding, conversation: Conversation) -> Action: ...


class ExampleUnderstanding:
    """Learn intents from examples; parse a deliberately small vehicle vocabulary.

    Replace the slot parser with trained entity extraction for production.
    Demo years are Solar Hijri, and car models come from a tiny alias catalog.
    """

    def __init__(self) -> None:
        self.index = TextIndex([text for text, intent in data.INTENT_EXAMPLES])

    def predict(self, *, text: str, conversation: Conversation) -> Understanding:
        normalized = normalize(text)
        index, score = self.index.search(normalized)
        intent = Intent(data.INTENT_EXAMPLES[index][1])
        updates: CarUpdates = {}
        year = re.search(r"(?<!\d)(1[34]\d{2})(?!\d)", normalized)
        if year:
            updates["year"] = int(year.group())
        for alias, model in (("پژو 206", "peugeot_206"), ("پژو 207", "peugeot_207"), ("پراید", "pride")):
            if alias in normalized:
                updates["model"] = model
        for alias, fuel in (
            ("بنزین", "petrol"),
            ("گازوئیل", "diesel"),
            ("دوگانه", "dual"),
            ("برقی", "electric"),
        ):
            if alias in normalized:
                updates["fuel_type"] = fuel
        preferences = ("lowest_premium",) if any(word in normalized for word in ("ارزون", "ارزان")) else None
        # Low lexical similarity and negated slot assertions need clarification.
        uncertain = score < 0.20 or (bool(updates) and "نیست" in normalized)
        selected = [
            offer.id
            for offer in conversation.offers
            if normalize(offer.title.removeprefix("بیمه ")) in normalized
        ]
        return Understanding(
            intents=(intent,),
            car_updates=updates,
            preferences=preferences,
            question=text if intent == Intent.QUESTION else None,
            # Ambiguous references do not select an offer.
            selected_offer_id=selected[0] if len(selected) == 1 else None,
            uncertain=uncertain,
        )


class ExamplePolicy:
    """1-nearest-neighbor classification over labeled conversation states.

    Intent has greater distance weight than state fields. Example labels, rather
    than a hardcoded dialogue tree, decide the action. This is not calibrated.
    """

    def predict(self, *, meaning: Understanding, conversation: Conversation) -> Action:
        intent = meaning.intents[0].value
        missing = conversation.car.missing_field()
        neighbor = min(
            data.POLICY_EXAMPLES,
            key=lambda row: 3 * (row[0] != intent) + (row[1] != conversation.buying) + (row[2] != missing),
        )
        kind = ActionKind(neighbor[3])
        return Action(
            kind=kind,
            field=missing if kind == ActionKind.ASK else None,
            offer_id=meaning.selected_offer_id if kind == ActionKind.CHECKOUT else None,
        )
