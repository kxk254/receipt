import pytest
from receipts.models import Receipt, 項目リスト, PDF番号
from datetime import date
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from receipts.views import InputView
from django.forms.models import modelformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from dateutil.relativedelta import relativedelta

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture
def user():
    """Fixture to create a test user"""
    user_model = get_user_model()
    return user_model.objects.create_user(username='testuser', password='testpassword')

@pytest.fixture
def 項目リスト_instance():
    """Fixture to create a 項目リスト instance"""
    return 項目リスト.objects.create(項目コード='ITEM001', 項目印字名='test item')

@pytest.fixture
def pdf_instance():
    """Fixture to create a PDF instance."""
    return PDF番号.objects.create(PDF_num='PDF001', upload='upload_images/IMG_3530.jpg', processed=False)

@pytest.mark.django_db
@pytest.fixture
def valid_post_data(項目リスト_instance, pdf_instance):
    """Prepare valid formset data for the POST request"""
    return {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-日付':'2025-01-15',
        'form-0-項目コード':項目リスト_instance.項目コード,
        'form-0-価格':350000,
        'form-0-登録番号':71000000,
        'form-0-備考':'NOTE FOR test',
        'form-0-PDF番号':pdf_instance.id,
    }

@pytest.mark.django_db
@pytest.fixture
def setup_receipts(項目リスト_instance, pdf_instance):
    Receipt.objects.create(日付='2025-01-06', 項目コード=項目リスト_instance, 価格=2300, 登録番号=100, PDF番号=pdf_instance)
    Receipt.objects.create(日付='2024-09-05', 項目コード=項目リスト_instance, 価格=3300, 登録番号=400, PDF番号=pdf_instance)

"""MAIN VIEW"""
@pytest.mark.django_db
def test_main_view(client, user):
    client.login(username='testuser', password='testpassword')
    url = reverse('main')
    response = client.get(url)
    print("response content", response.content.decode())
    print("response templates", response.templates)
    assert response.status_code == 200
    assert 'receipts/main.html' in [t.name for t in response.templates]
    assert 'MAIN' in response.content.decode()


"""INPUT VIEW GET & POST"""
@pytest.mark.django_db
@patch('receipts.views.ocr_get')  # Mock the ocr_get function
@patch('receipts.views.get_initial_data')  # Mock the ocr_get function
def test_input_view_get(mock_ocr_get, mock_get_initial_data, client, user, 項目リスト_instance, pdf_instance):
    """Test the InputView GET request"""
    mock_ocr_get.return_value = [
        {'項目コード':'ITEM001', '価格':1000, '登録番号': 12345, '備考':'test note'}
    ]
    mock_get_initial_data.return_value = [
        {'日付':'2024-09-01','項目コード':'ITEM001', '価格':1000,
          '登録番号': 12345, '備考':'test note', 'PDF番号':'PDF001'}
    ]

    client.login(username='testuser', password='testpassword')
    url = reverse('input_view', args=[pdf_instance.id])

    response = client.get(url)

    assert response.status_code == 200

    assert 'options' in response.context
    assert 'selected_option' in response.context
    assert 'ocrs' in response.context
    assert 'image_path' in response.context
    assert 'passing_id' in response.context

    ocrs_formset = response.context['ocrs']
    assert len(ocrs_formset) == 2

    assert ocrs_formset.forms[0].initial == {'項目コード':'ITEM001', '価格':1000, '登録番号': 12345, '備考':'test note'}

    relative_image_path = r'upload_images\IMG_3530.jpg'
    expected_image_url = f'/media/{relative_image_path}'

    assert response.context['image_path'] == expected_image_url
    assert response.context['passing_id'] == pdf_instance.id


@pytest.mark.django_db
def test_input_view_post_not_authenticated(client):
    url = reverse('create_view')
    response = client.post(url, data={'form-TOTAL_FORMS': 0})

    assert response.status_code == 302
    assert response.url.startswith('/accounts/login/?next=')

@pytest.mark.django_db
def test_input_view_post_valid(valid_post_data, setup_receipts, client, user):
    client.login(username='testuser', password='testpassword')
    url = reverse('create_view')

    response = client.post(url, data=valid_post_data)

    assert response.status_code == 302 #a successful form save should result in a redirect
    assert response.url == reverse('list_up_view')

    assert Receipt.objects.count() == 3

@pytest.mark.django_db
def test_input_view_post_invalid_data(client, user, setup_receipts):
    client.login(username='testuser', password='testpassword')
    invalid_post_data = {
        'form-TOTAL_FORMS':'1',
        'form-INITIAL_FORMS':'0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-日付':'202501-15',
        'form-0-価格':350000,
        'image_path':'/media/upload_images\\IMG_3187_nXD3QlI.JPG',
    }
    url = reverse('create_view')
    response = client.post(url, data=invalid_post_data)

    assert response.status_code == 200  #back to the table title page
    print("decode /////", response.content.decode())
    assert 'This field is required.' in response.content.decode()
    assert 'Enter a valid date.' in response.content.decode()

    assert Receipt.objects.count() == 2

    
"""Main DROP Upload template"""
@pytest.mark.django_db
def test_main_view_drop_upload(client, user):
    client.login(username='testuser', password='testpassword')
    url = reverse('main-upload')
    response = client.get(url)
    print("response content", response.content.decode())
    print("response templates", response.templates)
    assert response.status_code == 200
    assert 'receipts/dropupload.html' in [t.name for t in response.templates]
    assert 'Upload Here' in response.content.decode()


"""File Upload View"""
@pytest.mark.django_db
def test_file_upload_view_post(client, user):
    client.login(username='testuser', password='testpassword')
    
    # Prepare a PDF file to upload
    pdf_file = SimpleUploadedFile(
        'test_pdf.pdf',
        b'%PDF-1.4 sample content here',
        content_type='application\\pdf',
    )

    # Prepare a non-PDF file to upload
    jpg_file = SimpleUploadedFile(
        'test_image.jpg',
        b'JPEG content here',
        content_type='image\\jpeg',
    )

    # Prepare the POST data
    data = {
        'file': [pdf_file, jpg_file]
    }

    url = reverse('upload-view')
    response = client.post(url, data, format='multipart')

    # Assert the status code of the response
    assert response.status_code == 200

    # Assert the appropriate template is used
    assert 'receipts/success.html' in [t.name for t in response.templates]

    print("first PDF", PDF番号.objects.get(id=1).upload)

    assert PDF番号.objects.all().count() == 2

"""LIST Up View Test"""
@pytest.mark.django_db
def test_list_up_view_get(client, user, pdf_instance):
    client.login(username='testuser', password='testpassword')
    url = reverse('list_up_view')

    response = client.get(url)

    assert response.status_code == 200

    assert 'formset' in response.context
    assert 'MEDIA_URL' in response.context

    assert 'receipts/list_up.html' in [t.name for t in response.templates]

    assert PDF番号.objects.all().count() == 1
    assert PDF番号.objects.get(id=1).PDF_num == 'PDF001'
    assert response.context['MEDIA_URL'] == '/media/'

@pytest.mark.django_db
def test_list_up_view_filter_post(client, user, pdf_instance):
    client.login(username='testuser', password='testpassword')
    url = reverse('list_up_view')

    post_data =  {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-id': 1,
        'form-0-PDF_num': 'PDF-001',
        'form-0-upload': 'upload_images/IMG_3530.jpg',
        'form-0-processed':False,
        'filtering': '0',
    }

    response = client.post(url, post_data)

    # Assert the status code of the response
    assert response.status_code == 200

    # Assert the appropriate template is used
    assert 'receipts/list_up.html' in [t.name for t in response.templates]
    assert PDF番号.objects.all().count() == 1
    assert PDF番号.objects.get(id=1).PDF_num == 'PDF001'


@pytest.mark.django_db
def test_list_up_view_delete(client, user, pdf_instance):
    client.login(username='testuser', password='testpassword')
    url = reverse('list_up_view')

    print("original count", PDF番号.objects.count())

    filedata = SimpleUploadedFile(
        'upload_images/IMG_3530.jpg',
        b'JPEG content here',
        content_type='image\\jpeg',
    )
    
    post_data =  {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '1',
        'form-MAX_NUM_FORMS': '1000',
        'form-0-id': pdf_instance.id,
        'form-0-PDF_num': 'PDF-001',
        'form-0-upload': filedata,
        'form-0-processed':False,
        'form-0-DELETE':'true',
        'filtering': '0',
        'delete': 'yes',
    }

    response = client.post(url, post_data)
    # Assert the status code of the response
    assert response.status_code == 200

    # Assert the appropriate template is used
    assert 'receipts/list_up.html' in [t.name for t in response.templates]
    assert PDF番号.objects.count() == 0

@pytest.mark.django_db
def test_jpeg_list_view_get(client, user, pdf_instance):
    client.login(username='testuser', password='testpassword')
    url = reverse('jpeg_all_list')

    response = client.get(url)

    assert response.status_code == 200

    assert 'formset' in response.context
    assert 'MEDIA_URL' in response.context

    assert 'receipts/jpeg_all_list.html' in [t.name for t in response.templates]

    assert PDF番号.objects.all().count() == 1
    assert PDF番号.objects.get(id=1).PDF_num == 'PDF001'
    assert response.context['MEDIA_URL'] == '/media/'

@pytest.mark.django_db
def test_jpeg_list_view_post(client, user, pdf_instance, setup_receipts):
    client.login(username='testuser', password='testpassword')
    url = reverse('jpeg_all_list')

    print("count before post", Receipt.objects.all().count())

    post_data =  {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-MAX_NUM_FORMS': '1000',
        'select_field':['1',],
        'form-0-日付':'2025-01-15',
        'form-0-項目コード':'ITEM001',  #Receipt.objects.filter(項目コード='ITEM001').first(),
        'form-0-登録番号':350000,
        'form-0-価格':350000,
        'form-0-備考':'NOTE ITEM SECOND',
        'form-0-PDF番号':PDF番号.objects.filter(id=1).first(),
        'image_path':'/media/upload_images\\IMG_3187_nXD3QlI.JPG',
        'save': 'True',
    }

    response = client.post(url, post_data)

    # Assert the status code of the response
    assert response.status_code == 200

    # Assert the appropriate template is used
    assert 'receipts/jpeg_all_list.html' in [t.name for t in response.templates]
    assert Receipt.objects.all().count() == 3
    assert Receipt.objects.get(id=3).備考 == 'NOTE ITEM SECOND'

    assert 'path_info' in response.context
    assert 'formset' in response.context
    assert 'object_list' in response.context
    assert 'MEDIA_URL' in response.context
    assert 'selected_pdf_id' in response.context
    assert response.context['selected_pdf_id'] == '1'

@pytest.mark.django_db
def test_sort_update_view_get(client, user, pdf_instance):
    client.login(username='testuser', password='testpassword')
    url = reverse('sortupdate_list')

    response = client.get(url)

    assert response.status_code == 200

    assert 'formset' in response.context
    assert 'MEDIA_URL' in response.context
    assert 'sort_start' in response.context
    assert response.context['sort_end'] == datetime.today().strftime('%Y-%m-%d')
    end = datetime.today() - relativedelta(months=6)
    assert response.context['sort_start'] == end.strftime('%Y-%m-%d')

    assert 'receipts/sortupdate.html' in [t.name for t in response.templates]

    assert PDF番号.objects.all().count() == 1
    assert PDF番号.objects.get(id=1).PDF_num == 'PDF001'
    assert response.context['MEDIA_URL'] == '/media/'

@pytest.mark.django_db
def test_sort_update_view_post(client, user, pdf_instance, setup_receipts):
    client.login(username='testuser', password='testpassword')
    url = reverse('sortupdate_list')

    print("count before post", Receipt.objects.all().count())

    post_data =  {
        'form-TOTAL_FORMS': '2',
        'form-INITIAL_FORMS': '2',
        'form-MAX_NUM_FORMS': '1000',
        'select_field':['1','2'],
        'form-0-id':'1',
        'form-0-日付':'2025-02-15',
        'form-0-項目コード':'ITEM001',  #Receipt.objects.filter(項目コード='ITEM001').first(),
        'form-0-登録番号':500,
        'form-0-価格':5500,
        'form-0-備考':'POST TEST',
        'form-0-PDF番号':PDF番号.objects.filter(id=1).first(),
        'image_path':'/media/upload_images\\IMG_3187_nXD3QlI.JPG',
        'form-1-id':'2',
        'form-1-日付':'2025-03-15',
        'form-1-項目コード':'ITEM001',  #Receipt.objects.filter(項目コード='ITEM001').first(),
        'form-1-登録番号':600,
        'form-1-価格':7500,
        'form-1-備考':'POST TEST TWO',
        'form-1-PDF番号':PDF番号.objects.filter(id=1).first(),

    }

    response = client.post(url, post_data)

    # Assert the status code of the response
    assert response.status_code == 302

    # Assert the appropriate template is used
    assert Receipt.objects.all().count() == 2
    assert Receipt.objects.get(id=1).備考 == 'POST TEST'


    assert Receipt.objects.get(id=2).備考 == 'POST TEST TWO'


@pytest.mark.django_db
def test_sort_list_view_get(client, user, pdf_instance, setup_receipts):
    client.login(username='testuser', password='testpassword')
    url = reverse('sort_list')

    response = client.get(url)

    assert response.status_code == 200

    assert 'items' in response.context
    assert 'MEDIA_URL' in response.context
    assert 'sort_start' in response.context
    assert response.context['sort_end'] == datetime.today().strftime('%Y-%m-%d')
    end = datetime.today() - relativedelta(months=6)
    assert response.context['sort_start'] == end.strftime('%Y-%m-%d')

    assert 'receipts/sortlistview.html' in [t.name for t in response.templates]

    assert Receipt.objects.all().count() == 2
    assert Receipt.objects.get(id=1).日付.strftime('%Y-%m-%d') == '2025-01-06'
    assert response.context['MEDIA_URL'] == '/media/'



# def pdf_instance():
#     """Fixture to create a PDF instance."""
#     return PDF番号.objects.create(PDF_num='PDF001', upload='upload_images/IMG_3530.jpg')

# @pytest.mark.django_db
# @pytest.fixture
# def setup_receipts(項目リスト_instance, pdf_instance):
#     Receipt.objects.create(日付='2025-01-06', 項目コード=項目リスト_instance, 価格=2300, 登録番号=100, PDF番号=pdf_instance)
#     Receipt.objects.create(日付='2024-09-05', 項目コード=項目リスト_instance, 価格=3300, 登録番号=400, PDF番号=pdf_instance)




