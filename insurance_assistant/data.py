"""Tiny reviewed demo dataset; replace with representative user conversations."""

# User text, intent label. These are examples, not exact-match input rules.
INTENT_EXAMPLES = [
    ("سلام", "greet"),
    ("سلام وقت بخیر", "greet"),
    ("درود", "greet"),
    ("میخوام برای ماشینم بیمه بخرم", "buy"),
    ("برای پژو ۲۰۶ مدل ۱۴۰۰ بیمه میخوام ارزون باشه", "buy"),
    ("میخوام قیمت بیمه خودرو رو مقایسه کنم", "buy"),
    ("بیمه ماشین لازم دارم", "buy"),
    ("فرانشیز یعنی چی؟", "question"),
    ("فرانشیز چیست", "question"),
    ("بیمه بدنه با شخص ثالث چه فرقی دارد؟", "question"),
    ("بیمه شخص ثالث چیست؟", "question"),
    ("درباره بیمه بدنه توضیح بده", "question"),
    ("سال ساخت ۱۴۰۰", "provide_details"),
    ("مدل ماشینم پژو ۲۰۶ هست", "provide_details"),
    ("ماشینم بنزینیه", "provide_details"),
    ("نوع سوخت گازوئیلی است", "provide_details"),
    ("دوگانه سوز", "provide_details"),
    ("اشتباه گفتم سالش ۱۳۹۹ هست", "provide_details"),
    ("همون شرکت الف رو ادامه بده", "confirm"),
    ("پیشنهاد شرکت ب رو انتخاب میکنم", "confirm"),
    ("با بیمه شرکت الف ادامه میدم", "confirm"),
]

# intent, buying, first missing car field, action label.
# The policy learns nearest labeled state; there is no if/else dialogue tree.
POLICY_EXAMPLES = [
    ("greet", False, "year", "greet"),
    ("greet", True, "fuel_type", "greet"),
    ("question", False, "year", "answer"),
    ("question", True, "year", "answer"),
    ("question", True, "model", "answer"),
    ("question", True, "fuel_type", "answer"),
    ("question", True, None, "answer"),
    ("buy", True, "year", "ask"),
    ("buy", True, "model", "ask"),
    ("buy", True, "fuel_type", "ask"),
    ("buy", True, None, "compare"),
    ("provide_details", True, "year", "ask"),
    ("provide_details", True, "model", "ask"),
    ("provide_details", True, "fuel_type", "ask"),
    ("provide_details", True, None, "compare"),
    ("provide_details", False, "year", "clarify"),
    ("confirm", True, None, "checkout"),
]

# Illustrative content, not an insurer-approved knowledge base.
FAQS = [
    (
        "فرانشیز یعنی چی؟ فرانشیز چیست؟",
        "فرانشیز سهم بیمه‌گذار از خسارت است؛ جزئیات آن به شرایط بیمه‌نامه بستگی دارد.",
    ),
    (
        "بیمه شخص ثالث چیست؟",
        "بیمه شخص ثالث برای جبران خسارت واردشده به اشخاص ثالث، در حدود تعهدات بیمه‌نامه است.",
    ),
    (
        "بیمه بدنه چیست؟ تفاوت بیمه بدنه و شخص ثالث",
        "بیمه بدنه مربوط به پوشش خسارت‌های خود خودرو طبق شرایط قرارداد است؛ شخص ثالث مربوط به خسارت اشخاص ثالث است.",
    ),
]
