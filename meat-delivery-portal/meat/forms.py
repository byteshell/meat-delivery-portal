from django import forms
from .models import Meat

class MeatForm(forms.ModelForm):
    class Meta:
        model = Meat
        fields = ['meat_type', 'quantity', 'price']
