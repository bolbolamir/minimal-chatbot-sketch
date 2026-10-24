"""Main flow: understand -> update state -> predict action -> call service -> reply."""

from dataclasses import replace

from . import rendering
from .domain import Action, ActionKind, Conversation, Intent, Message, Turn, Understanding
from .models import ActionModel, UnderstandingModel
from .services import FAQService, InsuranceService


class Assistant:
    def __init__(
        self,
        *,
        understanding: UnderstandingModel,
        policy: ActionModel,
        faq: FAQService,
        insurance: InsuranceService,
    ) -> None:
        self.understanding = understanding
        self.policy = policy
        self.faq = faq
        self.insurance = insurance

    def reply(self, *, text: str, conversation: Conversation) -> str:
        return self.turn(text=text, conversation=conversation).response

    def turn(self, *, text: str, conversation: Conversation) -> Turn:
        meaning = self.understanding.predict(text=text, conversation=conversation)
        action = None
        if meaning.uncertain:
            response = rendering.CLARIFICATION
        else:
            car = replace(conversation.car, **meaning.car_updates)
            preferences = conversation.preferences if meaning.preferences is None else meaning.preferences
            if car != conversation.car or preferences != conversation.preferences:
                conversation.offers = ()
            conversation.car = car
            conversation.preferences = preferences
            conversation.buying |= Intent.BUY in meaning.intents

            action = self.policy.predict(meaning=meaning, conversation=conversation)
            response = self._execute(action=action, meaning=meaning, conversation=conversation)

        conversation.history.extend((Message("user", text), Message("assistant", response)))
        conversation.history = conversation.history[-8:]
        return Turn(meaning=meaning, action=action, response=response)

    def _execute(self, *, action: Action, meaning: Understanding, conversation: Conversation) -> str:
        match action.kind:
            case ActionKind.GREET:
                return "سلام! می‌توانم به سؤال‌های بیمه‌ای پاسخ بدهم یا برای خرید بیمه خودرو کمک کنم."
            case ActionKind.ANSWER:
                if meaning.question is None:
                    return rendering.CLARIFICATION
                return self.faq.answer(question=meaning.question, conversation=conversation)
            case ActionKind.ASK:
                return rendering.QUESTIONS.get(action.field or "", rendering.CLARIFICATION)
            case ActionKind.COMPARE | ActionKind.CHECKOUT:
                # Required inputs are a business precondition, not a dialogue policy.
                missing = conversation.car.missing_field()
                if missing is not None:
                    return rendering.QUESTIONS[missing]
                if action.kind == ActionKind.COMPARE:
                    conversation.offers = self.insurance.compare(
                        car=conversation.car, preferences=conversation.preferences
                    )
                    return rendering.render_offers(conversation.offers)
                if Intent.CONFIRM not in meaning.intents:
                    return "برای ادامه خرید، پیشنهاد موردنظرتان را مشخص کنید."
                if action.offer_id is None or not any(
                    offer.id == action.offer_id for offer in conversation.offers
                ):
                    return "لطفاً یکی از پیشنهادهای فعلی را برای ادامه خرید انتخاب کنید."
                url = self.insurance.checkout(offer_id=action.offer_id)
                return f"برای تکمیل اطلاعات و ادامه خرید از این لینک استفاده کنید: {url}"
            case _:
                return rendering.CLARIFICATION
