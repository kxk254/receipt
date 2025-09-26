from django.test import TestCase
from receipts.forms import ReceiptFormSet
from receipts.models import 項目リスト, PDF番号
import pytest
from ocr_v1 import settings

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocr_v1.settings')
# django.setup()

@pytest.mark.django_db  # Ensure that database transactions are handled
class TestReceiptFormSet:

    @pytest.fixture(autouse=True)
    def setUp(self):
        # Set up data for the test
        self.項目コード = 項目リスト.objects.create(項目コード='001', 項目短縮名='Test Item')  # Assuming 'name' is a field on 項目リスト
        self.PDF番号1 = PDF番号.objects.create(id=1, PDF_num='5')  # Assuming 'number' is a field on PDF番号

    def test_receipt_formset_validity(self):
        # Prepare the data dictionary for the formset
        data = {
            'form-TOTAL_FORMS': 1,  #The total number of forms in the formset
            'form-INITIAL_FORMS': 0,  #The number of forms that were initially rendered
            'form-MIN_NUM_FORMS': 0,  #optional
            'form-MAX_NUM_FORMS': 1000,  #optional
            'form-0-日付': '2024-09-01',
            'form-0-項目コード': self.項目コード.項目コード,
            'form-0-価格': 0,
            'form-0-登録番号': 0,
            'form-0-備考': 'test this',
            'form-0-PDF番号': self.PDF番号1.id,
            # 'form-0-id': 1,
        }
        
        # Create a ReceiptFormSet instance with the data
        formset = ReceiptFormSet(data)

        # Check if the formset is valid
        assert formset.is_valid(), "Formset is invalid."

        # Print form errors to understand the failure reason, if any
        if not formset.is_valid():
            for i, form in enumerate(formset):
                print(f"Form {i} errors: {form.errors}")

        # Assert that formset is valid (repetition for clarity in pytest)
        assert formset.is_valid(), "Formset is invalid."


        