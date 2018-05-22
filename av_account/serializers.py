from rest_framework import serializers

from av_account.models import AvUser, Address


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AvUser
        fields = ('url', 'first_name', 'last_name', 'middle_name', 'dob', 'ssn', 'email', 'phone',)
        read_only_fields = ('email',)
        extra_kwargs = {"dob": {"error_messages": {"invalid": "Date has wrong format."}}}


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user',)

    def save(self):
        user = self.context['request'].user
        return super(AddressSerializer, self).save(user=user)
