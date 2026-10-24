"""Run: python main.py [--demo] [--trace]. Standard library only."""

import argparse
import json
import sys
from dataclasses import asdict

from insurance_assistant.assistant import Assistant
from insurance_assistant.domain import Conversation
from insurance_assistant.models import ExamplePolicy, ExampleUnderstanding
from insurance_assistant.services import ExampleFAQ, ExampleInsurance

DEMO_MESSAGES = (
    "سلام",
    "برای پژو ۲۰۶ مدل ۱۴۰۰ بیمه میخوام ارزون باشه",
    "فرانشیز یعنی چی؟",
    "ماشینم بنزینیه",
    "همون شرکت الف رو ادامه بده",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Insurance assistant: a small ML demo")
    parser.add_argument("--demo", action="store_true", help="Run sample inputs through actual predictors")
    parser.add_argument("--trace", action="store_true", help="Show understanding, action and state")
    args = parser.parse_args()
    assistant = Assistant(
        understanding=ExampleUnderstanding(),
        policy=ExamplePolicy(),
        faq=ExampleFAQ(),
        insurance=ExampleInsurance(),
    )
    conversation = Conversation()
    messages = iter(DEMO_MESSAGES) if args.demo else iter(lambda: input("شما: "), "exit")
    sys.stdout.write("نسخه نمایشی؛ اطلاعات و قیمت‌ها نمونه‌اند و لینک خرید واقعی نیست.\n")
    try:
        for text in messages:
            if args.demo:
                sys.stdout.write(f"شما: {text}\n")
            turn = assistant.turn(text=text, conversation=conversation)
            sys.stdout.write(f"دستیار: {turn.response}\n\n")
            if args.trace:
                trace = {
                    "meaning": asdict(turn.meaning),
                    "action": asdict(turn.action) if turn.action else None,
                    "state": asdict(conversation),
                }
                sys.stdout.write(json.dumps(trace, ensure_ascii=False, indent=2, default=str) + "\n")
    except (EOFError, KeyboardInterrupt):
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
