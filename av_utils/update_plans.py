import stripe

from av_core import settings

# update plan values
# run me like this:
# python manage.py shell < av_utils/update_plans.py


stripe.api_key = settings.STRIPE_SECRET_KEY
plans = settings.STRIPE_PLANS

p = stripe.Plan.retrieve(plans['yearly']['a'])
p.metadata = {
    "name": "Proprietor",
    "support": "email",
    "max_cpa": 1,
    "max_client": 100,
}
p.save()
p = stripe.Plan.retrieve(plans['monthly']['a'])
p.metadata = {
    "name": "Proprietor",
    "support": "email",
    "max_cpa": 1,
    "max_client": 100,
}
p.save()

p = stripe.Plan.retrieve(plans['yearly']['b'])
p.metadata = {
    "name": "Practice",
    "support": "email",
    "max_cpa": 5,
    "max_client": 1000,
}
p.save()
p = stripe.Plan.retrieve(plans['monthly']['b'])
p.metadata = {
    "name": "Practice",
    "support": "email",
    "max_cpa": 5,
    "max_client": 1000,
}
p.save()

p = stripe.Plan.retrieve(plans['yearly']['c'])
p.metadata = {
    "name": "Firm",
    "support": "email and phone",
    "max_cpa": 15,
    "max_client": 3000,
}
p.save()
p = stripe.Plan.retrieve(plans['monthly']['c'])
p.metadata = {
    "name": "Firm",
    "support": "email and phone",
    "max_cpa": 15,
    "max_client": 3000,
}
p.save()
