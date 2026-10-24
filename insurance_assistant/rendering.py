"""Approved wording and live comparison data; no text generation."""

from .domain import Offer

QUESTIONS = {
    "year": "سال ساخت خودرو چیست؟",
    "model": "مدل خودرو چیست؟",
    "fuel_type": "نوع سوخت خودرو چیست؟",
}
CLARIFICATION = "لطفاً کمی بیشتر توضیح دهید تا بهتر راهنمایی‌تان کنم."


def render_offers(offers: tuple[Offer, ...]) -> str:
    if not offers:
        return "برای این مشخصات پیشنهادی پیدا نشد."
    rows = [f"{offer.title}: {offer.premium} {offer.currency}؛ {offer.coverage_summary}" for offer in offers]
    return "\n".join([*rows, "برای ادامه خرید، پیشنهاد موردنظرتان را مشخص کنید."])
