from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Contact


class ContactTestCase(TestCase):

    def test_new_contact(self):
        data = {
            'email': 'x@a.com',
            'name': 'x x',
            'subject': 'hi',
            'message': 'there',
        }

        self.client.post(reverse('contact'), data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(data['subject'], mail.outbox[0].body)
        self.assertIn(data['message'], mail.outbox[0].body)

        contact = Contact.objects.get(email=data['email'])
        self.assertEqual(contact.name, data['name'])
