import pytest
from receipts.models import Receipt, 項目リスト, PDF番号
from datetime import date

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture
def create_sample_data():
    """Fixture to create 項目リスト PDF番号 for Receipt model"""
    item = 項目リスト.objects.create(項目コード='001', 項目印字名='消耗品')
    pdf_number = PDF番号.objects.create(PDF_num='A-001', upload='imgimg.jpg', processed=False)
    return item, pdf_number

@pytest.mark.django_db
def test_create_receipt(create_sample_data):
    """Test creation Receipt model"""
    item, pdf_number = create_sample_data

    Receipt.objects.create(
        日付 = "2024-09-30",
        項目コード = item,
        価格 = 3500,
        登録番号 = '71345889878',
        備考 = 'This is the note',
        PDF番号 = pdf_number,
    )

    output = Receipt.objects.get(id=1)

    assert output.日付 == date(2024, 9, 30)
    assert output.項目コード == item
    assert output.価格 == 3500
    assert output.登録番号 == 71345889878
    assert output.備考 == 'This is the note'
    assert output.PDF番号 == pdf_number

@pytest.mark.django_db
def test_default_values(create_sample_data):
    """Test default values on Receipt"""
    item, pdf_number = create_sample_data

    receipt = Receipt.objects.create(
        日付 = "2024-09-30",
        項目コード = item,
        備考 = 'This is the note',
        PDF番号 = pdf_number,
    )

    assert receipt.価格 == 0
    assert receipt.登録番号 == 0

@pytest.mark.django_db
def test_foreign_key_relationship(create_sample_data):
    """Test the foreign key relationshi@"""
    item, pdf_number = create_sample_data

    receipt = Receipt.objects.create(
        日付 = "2024-09-30",
        項目コード = item,
        備考 = 'This is the note',
        PDF番号 = pdf_number,
    )

    assert receipt.項目コード.項目コード == '001'
    assert receipt.PDF番号.PDF_num == 'A-001'

@pytest.mark.django_db
def test_receipt_delete(create_sample_data):
    """Test that deleting a Receipt cascades correctly"""
    item, pdf_number = create_sample_data

    receipt = Receipt.objects.create(
        日付 = "2024-09-30",
        項目コード = item,
        価格 = 3500,
        登録番号 = '71345889878',
        備考 = 'This is the note',
        PDF番号 = pdf_number,
    )

    item_for_test = 項目リスト.objects.get(項目コード='001')

    item_for_test.delete()

    with pytest.raises(Receipt.DoesNotExist):
        Receipt.objects.get(id=1)




