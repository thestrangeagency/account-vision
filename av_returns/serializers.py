from django.urls import reverse
from rest_framework import serializers

from av_returns.models import Return, Spouse, Dependent, Expense, CommonExpenses
from av_utils.utils import get_object_or_None


class ReturnSerializer(serializers.HyperlinkedModelSerializer):
    spouse = serializers.HyperlinkedRelatedField(many=False, view_name='spouse-detail', read_only=True)

    class Meta:
        model = Return
        fields = ('url', 'year', 'filing_status', 'spouse', 'is_dependent', 'is_first_time', 'has_health', 'county')
        read_only_fields = ('year',)

    def create(self, validated_data):

        existing_return = get_object_or_None(Return, user=self.context['request'].user, year=Return.default_year())

        if existing_return is None:
            return super(ReturnSerializer, self).create(validated_data=validated_data)
        else:
            existing_return.filing_status = validated_data.get('filing_status', None)
            existing_return.is_dependent = validated_data.get('is_dependent', False)
            existing_return.is_first_time = validated_data.get('is_first_time', False)
            existing_return.save()
            return existing_return

    def save(self):
        user = self.context['request'].user
        return super(ReturnSerializer, self).save(user=user)


class SpouseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Spouse
        fields = ('url', 'first_name', 'last_name', 'middle_name', 'dob', 'ssn', 'tax_return')
        read_only_fields = ('tax_return',)


class DependentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('make_url')

    class Meta:
        model = Dependent
        fields = ('id', 'url', 'first_name', 'last_name', 'middle_name', 'dob', 'ssn', 'relationship', 'tax_return')
        read_only_fields = ('tax_return',)

    def save(self):
        year = self.context["year"]
        tax_return = Return.objects.get(user=self.context['request'].user, year=year)
        return super(DependentSerializer, self).save(tax_return=tax_return)

    def make_url(self, obj):
        kwargs = {
            'year': obj.tax_return.year,
            'pk': obj.id,
        }
        url = reverse('dependent-detail', kwargs=kwargs)
        return self.context['request'].build_absolute_uri(url)


class ExpenseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('make_url')

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ('tax_return',)

    def save(self):
        year = self.context["year"]
        tax_return = Return.objects.get(user=self.context['request'].user, year=year)
        return super(ExpenseSerializer, self).save(tax_return=tax_return)

    def make_url(self, obj):
        kwargs = {
            'year': obj.tax_return.year,
            'pk': obj.id,
        }
        url = reverse('expense-detail', kwargs=kwargs)
        return self.context['request'].build_absolute_uri(url)

    def validate_type(self, value):
        year = self.context["year"]
        tax_return = Return.objects.get(user=self.context['request'].user, year=year)
        # ensure year and type are unique together
        # UniqueTogetherValidator doesn't work because it expects tax_return from POST
        if self.instance:
            count = Expense.objects.exclude(pk=self.instance.pk).filter(tax_return=tax_return, type=value).count()
        else:
            count = Expense.objects.filter(tax_return=tax_return, type=value).count()
        if count > 0:
            raise serializers.ValidationError("An expense of this type already exists")
        return value


class CommonExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommonExpenses
        read_only_fields = ('tax_return',)
        exclude = ('date_created', 'date_modified', 'tax_return')

    def save(self):
        year = self.context["year"]
        tax_return = Return.objects.get(user=self.context['request'].user, year=year)
        return super(CommonExpenseSerializer, self).save(tax_return=tax_return)
