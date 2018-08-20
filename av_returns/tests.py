from django.db import IntegrityError
from django.test import TestCase
from django.urls.base import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from av_account.models import AvUser
from av_utils.utils import get_object_or_None
from .models import Return, Spouse, Dependent, Expense, CommonExpenses


class ReturnsTestCase(TestCase):

    def setUp(self):
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password='password',
        )
        self.user.is_verified = True
        self.user.is_email_verified = True
        self.user.is_onboard = True
        self.user.is_paid = True
        self.user.phone = '(310) 666-3912'
        self.user.save()

        self.year = 1984
        self.my_return = Return(
            user=self.user,
            year=self.year,
        )
        self.my_return.save()

        self.spouse = Spouse(
            tax_return=self.my_return,
        )
        self.spouse.save()

    def login(self):
        self.client.login(
            username=self.user.email,
            password='password'
        )
        self.client.get(reverse('force_trust'))

    def test_unique(self):
        another_return = Return(
            user=self.user,
            year=self.year,
        )
        try:
            another_return.save()
            self.fail("Return uniqueness not enforced")
        except IntegrityError as ex:
            # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            # message = template.format(type(ex).__name__, ex.args)
            # print(message)
            pass

    def test_detail_anon(self):
        url = reverse('return', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_detail(self):
        self.login()
        url = reverse('return', args=[self.year])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_not_verified(self):
        self.user.is_verified = False
        self.user.is_2fa = True
        self.user.save()

        self.login()
        url = reverse('return', args=[self.year])
        response = self.client.get(url)
        self.assertRedirects(response, "{}?next={}".format(reverse('trust'), url), status_code=302)

    def test_not_verified_email(self):
        self.user.is_email_verified = False
        self.user.save()

        self.login()
        url = reverse('return', args=[self.year])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('email_verify'), status_code=302)


    def test_spouse(self):
        url = reverse('spouse', args=[self.year])
        self.login()

        data = {
            'first_name': 'Betty',
            'ssn': '123121234',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        tax_return = self.my_return
        spouse = Spouse.objects.filter(tax_return=tax_return).first()
        self.assertEqual(spouse.first_name, data['first_name'])
        self.assertEqual(spouse.ssn, data['ssn'])

    def test_dependents(self):
        url = reverse('dependents', args=[self.year])
        self.login()

        # using a formset, so need management data
        data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 9,
            'form-0-first_name': 'Zeke',
            'form-0-ssn': '123121234',
            'form-0-relationship': 'SON',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        tax_return = self.my_return
        dependent = Dependent.objects.filter(tax_return=tax_return).first()
        self.assertEqual(dependent.first_name, data['form-0-first_name'])
        self.assertEqual(dependent.ssn, data['form-0-ssn'])

    def test_expenses_anon(self):
        url = reverse('expense-list', args=[self.year])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expenses(self):
        url = reverse('expense-list', args=[self.year])
        self.login()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expenses_add(self):
        url = reverse('expense-list', args=[self.year])
        self.login()

        data = {
            'amount': 5,
            'type': 'dues'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expense = Expense.objects.get(tax_return=self.my_return)
        self.assertEqual(expense.amount, data['amount'])


class ExpenseAPITestCase(APITestCase):

    def setUp(self):
        self.password = 'password'
        
        self.user = AvUser.objects.create_user(
            email='test@example.com',
            password=self.password,
        )
        self.user.save()

        self.year = 1984
        self.my_return = Return(
            user=self.user,
            year=self.year,
        )
        self.my_return.save()

        self.common_expense = get_object_or_None(CommonExpenses, tax_return=self.my_return)

    def login(self):
        self.client.login(
            username=self.user.email,
            password=self.password
        )
        self.client.get(reverse('force_trust'))

    def test_protected(self):
        url = reverse('commonexpenses-list', args=[self.year])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_update(self):
    #     url = reverse('commonexpenses-detail', args=[self.year, self.common_expense.id])
    #     data = {
    #         'union_dues': 5,
    #     }
    #
    #     self.client.login(username=self.user.email, password='password')
    #
    #     response = self.client.patch(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     common_expenses = CommonExpenses.objects.get(tax_return=self.my_return)
    #     self.assertEqual(common_expenses.union_dues, data['union_dues'])
    #
    # def test_update_other(self):
    #     """
    #     ensure cannot overwrite another user's expenses
    #     """
    #
    #     new_user = AvUser.objects.create_user(
    #         email='test2@example.com',
    #         password='password',
    #     )
    #     new_user.save()
    #
    #     new_return = Return(
    #         user=new_user,
    #         year=self.year,
    #     )
    #     new_return.save()
    #
    #     self.client.login(username=new_user.email, password='password')
    #
    #     url = reverse('commonexpenses-detail', args=[self.year, self.common_expense])
    #     data = {
    #         'union_dues': 5,
    #     }
    #
    #     response = self.client.patch(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #
    #     new_common_expense = CommonExpenses.objects.get(tax_return=new_return)
    #
    #     url = reverse('commonexpenses-detail', args=[self.year, new_common_expense.id])
    #     response = self.client.patch(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_custom(self):
        url = reverse('expense-list', args=[self.year])
        data = {
            'type': 'pen',
            'amount': '3.50',
        }

        self.login()

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expense = Expense.objects.get(tax_return=self.my_return)
        self.assertEqual(expense.type, 'pen')
        self.assertEqual(expense.amount, 3.5)

    def test_update_custom(self):
        # create
        url = reverse('expense-list', args=[self.year])
        data = {
            'type': 'pen',
            'amount': '3',
        }

        self.login()

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expense = Expense.objects.get(tax_return=self.my_return)
        self.assertEqual(expense.type, 'pen')
        self.assertEqual(expense.amount, 3)

        # update amount
        url = reverse('expense-detail', args=[self.year, expense.id])
        data = {
            'type': 'pen',
            'amount': '4',
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expense = Expense.objects.get(tax_return=self.my_return)
        self.assertEqual(expense.amount, 4)

        # update type
        data = {
            'type': 'pencil',
        }

        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expense = Expense.objects.get(tax_return=self.my_return)
        self.assertEqual(expense.type, 'pencil')

        # create new with type conflict
        url = reverse('expense-list', args=[self.year])
        data = {
            'type': 'pencil',
            'amount': '3',
        }

        self.client.post(url, data)
        # TODO these don't do anything, remove them and actually test for the error
        self.assertRaises(ValidationError)

        # create new
        data = {
            'type': 'book',
            'amount': '3',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update old with type conflict
        url = reverse('expense-detail', args=[self.year, expense.id])
        data = {
            'type': 'book',
        }

        self.client.patch(url, data)
        self.assertRaises(ValidationError)
