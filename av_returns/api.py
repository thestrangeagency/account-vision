from rest_framework import viewsets, permissions

from av_returns.serializers import *


class ReturnViewSet(viewsets.ModelViewSet):
    # despite dynamic queryset, leaving queryset here for automatic api basename
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    model = Return
    http_method_names = ['post', 'get', 'patch']

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class SpouseViewSet(viewsets.ModelViewSet):
    queryset = Spouse.objects.all()
    serializer_class = SpouseSerializer
    model = Spouse
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return self.model.objects.filter(tax_return__user=self.request.user)


class DependentViewSet(viewsets.ModelViewSet):
    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer
    model = Dependent
    http_method_names = ['get', 'patch', 'post']

    def get_queryset(self):
        year = self.kwargs['year']
        return self.model.objects.filter(tax_return__user=self.request.user, tax_return__year=year)

    def get_serializer_context(self):
        context = super(DependentViewSet, self).get_serializer_context()
        context['year'] = self.kwargs['year']
        return context


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    model = Expense
    http_method_names = ['get', 'patch', 'post', 'delete']

    def get_queryset(self):
        year = self.kwargs['year']
        return self.model.objects.filter(tax_return__user=self.request.user, tax_return__year=year)

    def get_serializer_context(self):
        context = super(ExpenseViewSet, self).get_serializer_context()
        context['year'] = self.kwargs['year']
        return context


class CommonExpenseViewSet(viewsets.ModelViewSet):
    queryset = CommonExpenses.objects.all()
    serializer_class = CommonExpenseSerializer
    model = CommonExpenses
    http_method_names = ['get', 'patch', 'head']

    def get_queryset(self):
        year = self.kwargs['year']
        return self.model.objects.filter(tax_return__user=self.request.user, tax_return__year=year)

    def get_serializer_context(self):
        context = super(CommonExpenseViewSet, self).get_serializer_context()
        context['year'] = self.kwargs['year']
        return context
