import datetime
from decimal import Decimal

from django.db import models
from django.dispatch import receiver
from django.urls import reverse

from av_account.models import Person, AvUser
from av_utils.utils import TimeStampedModel


class Return(TimeStampedModel):
    user = models.ForeignKey(AvUser, null=False)
    year = models.SmallIntegerField(null=False)
    is_dependent = models.NullBooleanField(null=True)
    county = models.CharField(max_length=128, blank=True)

    SINGLE = 'SINGLE'
    MARRIED_JOINT = 'MARRIED_JOINT'
    MARRIED_SEPARATE = 'MARRIED_SEPARATE'
    HEAD = 'HEAD'
    WIDOW = 'WIDOW'
    FILING_STATUS_CHOICES = (
        (SINGLE, "Single"),
        (MARRIED_JOINT, "Married, filing jointly"),
        (MARRIED_SEPARATE, "Married, filing separately"),
        (HEAD, "Head of household"),
        (WIDOW, "Widow"),
    )
    filing_status = models.CharField(max_length=32, choices=FILING_STATUS_CHOICES, null=True)

    DRAFT = 'DRAFT'
    REVIEW = 'REVIEW'
    COMPLETE = 'COMPLETE'
    READY = 'READY'
    FILED = 'FILED'
    RETURN_STATUS_CHOICES = (
        (DRAFT, "Information Submitted"),   # return data being edited
        (REVIEW, "Under CPA Review"),       # ready for CPA review
        (COMPLETE, "Completed"),            # CPA has completed return
        (READY, "Ready to file"),           # user agreed to e-file
        (FILED, "Filed"),                   # CPA has e-filed
    )
    return_status = models.CharField(max_length=32, choices=RETURN_STATUS_CHOICES, default=DRAFT)
    original_return_status = None

    class Meta:
        unique_together = ("user", "year")

    def __init__(self, *args, **kwargs):
        super(Return, self).__init__(*args, **kwargs)
        self.original_return_status = self.return_status

    def __str__(self):
        return "{} {} ({}) {}".format(self.user.first_name, self.user.last_name, self.user.email, self.year)

    def is_frozen(self):
        return self.return_status != self.DRAFT

    @classmethod
    def year_choices(cls):
        now = datetime.date.today().year
        return [(r, r) for r in range(now - 10, now + 1)]


class Spouse(Person):
    tax_return = models.OneToOneField(Return, null=True, on_delete=models.CASCADE)

    def get_stream_name(self):
        return 'spouse named {}'.format(self.__str__())

    def get_stream_url(self):
        return reverse('client-detail-return-spouse', args=[self.tax_return.user.email, self.tax_return.year])


class Dependent(Person):
    tax_return = models.ForeignKey(Return, null=True, on_delete=models.CASCADE)

    DAUGHTER = 'DAUGHTER'
    SON = 'SON'
    AUNT = 'AUNT'
    BROTHER = 'BROTHER'
    FOSTER_CHILD = 'FOSTER_CHILD'
    GRANDCHILD = 'GRANDCHILD'
    GRANDPARENT = 'GRANDPARENT'
    HALF_BROTHER = 'HALF_BROTHER'
    HALF_SISTER = 'HALF_SISTER'
    NEPHEW = 'NEPHEW'
    NIECE = 'NIECE'
    NONE = 'NONE'
    OTHER = 'OTHER'
    PARENT = 'PARENT'
    SISTER = 'SISTER'
    STEPBROTHER = 'STEPBROTHER'
    STEPCHILD = 'STEPCHILD'
    STEPSISTER = 'STEPSISTER'
    UNCLE = 'UNCLE'

    RELATIONSHIP_CHOICES = (
        (DAUGHTER, "Daughter"),
        (SON, "Son"),
        (AUNT, "Aunt"),
        (BROTHER, "Brother"),
        (FOSTER_CHILD, "Foster Child"),
        (GRANDCHILD, "Grandchild"),
        (GRANDPARENT, "Grandparent"),
        (HALF_BROTHER, "Half Brother"),
        (HALF_SISTER, "Half Sister"),
        (NEPHEW, "Nephew"),
        (NIECE, "Niece"),
        (NONE, "None"),
        (OTHER, "Other"),
        (PARENT, "Parent"),
        (SISTER, "Sister"),
        (STEPBROTHER, "Stepbrother"),
        (STEPCHILD, "Stepchild"),
        (STEPSISTER, "Stepsister"),
        (UNCLE, "Uncle"),
    )
    relationship = models.CharField(max_length=32, choices=RELATIONSHIP_CHOICES, null=True)

    def get_stream_name(self):
        return 'dependent named {}'.format(self.__str__())

    def get_stream_url(self):
        return reverse('client-detail-return-dependents', args=[self.tax_return.user.email, self.tax_return.year])


class Expense(TimeStampedModel):
    tax_return = models.ForeignKey(Return, null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    type = models.CharField(max_length=32)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("tax_return", "type")

    def __str__(self):
        return "{} ${}".format(self.type, self.amount)

    def get_stream_name(self):
        return "expense {} for ${}".format(self.type, self.amount)

    def get_stream_url(self):
        return reverse('client-detail-return-expenses', args=[self.tax_return.user.email, self.tax_return.year])


class CommonExpenses(TimeStampedModel):
    tax_return = models.ForeignKey(Return, null=True, on_delete=models.CASCADE)

    medical_expenses = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    real_estate_taxes = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    mortgage_interest = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    tax_preparation_fees = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    union_dues = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    subscriptions = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    professional_dues = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    telephone = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    investment_management_fees = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    job_hunting_costs = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    travel = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    entertainment = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    supplies = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    transportation = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))
    charitable_contributions = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.0'))

