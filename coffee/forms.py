from django.forms import ModelForm

from coffee.models import ContentOrder


class OrderForm(ModelForm):
    class Meta:
        model = ContentOrder
        fields = ['coffee']
