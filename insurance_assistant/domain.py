"""Data exchanged between understanding, policy and insurance services."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import TypedDict


class Intent(StrEnum):
    GREET = "greet"
    QUESTION = "question"
    BUY = "buy"
    PROVIDE_DETAILS = "provide_details"
    CONFIRM = "confirm"


class ActionKind(StrEnum):
    GREET = "greet"
    ANSWER = "answer"
    ASK = "ask"
    COMPARE = "compare"
    CHECKOUT = "checkout"
    CLARIFY = "clarify"


class CarUpdates(TypedDict, total=False):
    year: int | None
    model: str | None
    fuel_type: str | None


@dataclass(frozen=True, slots=True)
class Car:
    year: int | None = None
    model: str | None = None
    fuel_type: str | None = None

    def missing_field(self) -> str | None:
        for name in ("year", "model", "fuel_type"):
            if getattr(self, name) is None:
                return name
        return None


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    text: str


@dataclass(frozen=True, slots=True)
class Offer:
    id: str
    title: str
    premium: Decimal
    currency: str
    coverage_summary: str


@dataclass(slots=True)
class Conversation:
    car: Car = field(default_factory=Car)
    buying: bool = False
    preferences: tuple[str, ...] = ()
    offers: tuple[Offer, ...] = ()
    history: list[Message] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Understanding:
    intents: tuple[Intent, ...]
    car_updates: CarUpdates = field(default_factory=CarUpdates)
    preferences: tuple[str, ...] | None = None
    question: str | None = None
    selected_offer_id: str | None = None
    uncertain: bool = False


@dataclass(frozen=True, slots=True)
class Action:
    kind: ActionKind
    field: str | None = None
    offer_id: str | None = None


@dataclass(frozen=True, slots=True)
class Turn:
    meaning: Understanding
    action: Action | None
    response: str
