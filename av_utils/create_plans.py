import stripe

from av_core import settings

# update plan values
# run me like this:
# python manage.py shell < av_utils/create_plans.py


stripe.api_key = settings.STRIPE_SECRET_KEY

stripe.Product.create(
    id="prod_av",
    name='Account Vision',
    type='service',
)

metadata_a = {
    "max_client": "100",
    "max_cpa": "1",
    "name": "Proprietor",
    "support": "email"
}

metadata_b = {
    "max_client": "500",
    "max_cpa": "5",
    "name": "Practice",
    "support": "email"
}

metadata_c = {
    "max_client": "1500",
    "max_cpa": "15",
    "name": "Firm",
    "support": "email and phone"
}

stripe.Plan.create(
    amount=36000,
    currency="usd",
    id="plan_ay",
    interval="year",
    metadata=metadata_a,
    nickname="A Yearly",
    product="prod_av",
    trial_period_days=14,
)

stripe.Plan.create(
    amount=3900,
    currency="usd",
    id="plan_am",
    interval="month",
    metadata=metadata_a,
    nickname="A Monthly",
    product="prod_av",
    trial_period_days=14,
)

stripe.Plan.create(
    amount=108000,
    currency="usd",
    id="plan_by",
    interval="year",
    metadata=metadata_b,
    nickname="B Yearly",
    product="prod_av",
    trial_period_days=14,
)
stripe.Plan.create(
    amount=11700,
    currency="usd",
    id="plan_bm",
    interval="month",
    metadata=metadata_b,
    nickname="B Monthly",
    product="prod_av",
    trial_period_days=14,
)

stripe.Plan.create(
    amount=180000,
    currency="usd",
    id="plan_cy",
    interval="year",
    metadata=metadata_c,
    nickname="C Yearly",
    product="prod_av",
    trial_period_days=14,
)

stripe.Plan.create(
    amount=19500,
    currency="usd",
    id="plan_cm",
    interval="month",
    metadata=metadata_c,
    nickname="C Monthly",
    product="prod_av",
    trial_period_days=14,
)
