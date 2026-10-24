"""Backend boundaries; prices and coverage never come from model weights."""

from decimal import Decimal
from typing import Protocol

from . import data
from .domain import Car, Conversation, Offer
from .models import TextIndex


class FAQService(Protocol):
    def answer(self, *, question: str, conversation: Conversation) -> str:
        """Retrieve an approved general or product FAQ using embeddings.

        Optionally rerank matches. Return clarification/handoff text on a poor
        match; do not substitute an unrelated answer. No generated policy claims.
        """
        ...


class InsuranceService(Protocol):
    def compare(self, *, car: Car, preferences: tuple[str, ...]) -> tuple[Offer, ...]:
        """Validate car values, fetch eligible live offers, rank by customer needs.

        The three car fields are the chatbot's initial required inputs. The real
        backend owns product-specific underwriting and any further requirements.
        """
        ...

    def checkout(self, *, offer_id: str) -> str:
        """Return a secure purchase-flow URL for a current offer.

        The backend validates offer validity and collects remaining details,
        insurance type, consent and payment. This call does not issue a policy.
        """
        ...


class ExampleFAQ:
    """Retrieval over illustrative FAQ content, not production-approved advice."""

    def __init__(self) -> None:
        self.index = TextIndex([question for question, answer in data.FAQS])

    def answer(self, *, question: str, conversation: Conversation) -> str:
        index, score = self.index.search(question)
        if score < 0.30:
            return "برای این سؤال پاسخ مطمئنی در اطلاعات نمونه ندارم؛ لطفاً با پشتیبانی مطرح کنید."
        return data.FAQS[index][1]


class ExampleInsurance:
    """Fictional quotes and nonfunctional checkout links. No money moves."""

    def compare(self, *, car: Car, preferences: tuple[str, ...]) -> tuple[Offer, ...]:
        if car.model not in {"peugeot_206", "peugeot_207", "pride"}:
            raise ValueError("Unsupported demo car model")
        if car.year is None or not 1300 <= car.year <= 1405:
            raise ValueError("Demo expects a Solar Hijri year between 1300 and 1405")
        if car.fuel_type not in {"petrol", "diesel", "dual", "electric"}:
            raise ValueError("Unsupported demo fuel type")
        # A visible fake pricing formula, not an actuarial or insurer quote.
        base = Decimal(7000000) + (1405 - car.year) * Decimal(100000)
        offers = (
            Offer("offer_a", "بیمه شرکت الف", base, "تومان", "پوشش نمونه پایه"),
            Offer("offer_b", "بیمه شرکت ب", base + Decimal(700000), "تومان", "پوشش نمونه بیشتر"),
        )
        return (
            tuple(sorted(offers, key=lambda offer: offer.premium))
            if "lowest_premium" in preferences
            else offers
        )

    def checkout(self, *, offer_id: str) -> str:
        if offer_id not in {"offer_a", "offer_b"}:
            raise ValueError("Unknown demo offer")
        return f"https://insurance.example/checkout/{offer_id}"
