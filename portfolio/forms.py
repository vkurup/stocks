from django import forms

class BuyForm(forms.Form):
    date = forms.DateField()
    security = forms.CharField(max_length=10)
    shares = forms.DecimalField()
    price = forms.DecimalField()
    commission = forms.DecimalField()

class DepositForm(forms.Form):
    date = forms.DateField()
    amount = forms.DecimalField()
