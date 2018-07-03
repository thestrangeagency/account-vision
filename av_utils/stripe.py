from collections import namedtuple

Customer = namedtuple('Customer', 'id subscriptions')
Items = namedtuple('Items', 'data')
Subscription = namedtuple('Subscription', 'id plan')
Plan = namedtuple('Plan', 'id metadata')
MetaData = namedtuple('MetaData', 'name support max_cpa max_client')
