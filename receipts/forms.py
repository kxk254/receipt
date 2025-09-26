
from django import forms
from .models import Receipt, PDF番号, 項目リスト
from django.forms import modelformset_factory

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class PDFNumForm(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput) 
    
    class Meta:
        model = PDF番号
        fields = '__all__'  # Or specify the fields you want
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Example condition: Add 'bg-gray' class to PDF_num field if processed is True (or other condition)
        if self.instance.processed:  # Check if the instance is processed
            self.fields['PDF_num'].widget.attrs['class'] = 'bg-gray'


PDFNumFormSet = modelformset_factory(PDF番号, form=PDFNumForm, extra=0, can_delete=True)


class ReceiptForm(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput) 
    
    class Meta:
        model = Receipt
        fields = '__all__'  # Or specify the fields you want

ReceiptFormSet = modelformset_factory(Receipt, form=ReceiptForm, extra=1, can_delete=True)

class ReceiptForm2(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput)
    日付 = forms.CharField(widget=forms.TextInput(attrs={'class': 'hover-td'}))
    価格 = forms.CharField(widget=forms.TextInput(attrs={'class': 'width100'}))
    PDF番号 = forms.ModelChoiceField(queryset=PDF番号.objects.all(), widget=forms.Select(attrs={'class': 'width50'}))
    
    class Meta:
        model = Receipt
        fields = '__all__'  # Or specify the fields you want


ReceiptFormSet_no_extra = modelformset_factory(Receipt, form=ReceiptForm2, extra=0, can_delete=True)