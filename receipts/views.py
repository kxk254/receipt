from django.shortcuts import render, redirect, get_object_or_404
from .models import Receipt, 項目リスト, PDF番号
from django.views.generic.base import View
from programs.ocr_main import ocr_get, get_initial_data
import os
from django.conf import settings
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from urllib.parse import urlencode
from programs.file_handler import handle_uploaded_file, pdf_to_jpeg, save_file_to_temp
from django.views.generic import TemplateView, ListView
from .forms import ReceiptFormSet, ReceiptFormSet_no_extra, ReceiptForm, PDFNumFormSet
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import calendar
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory
from . import backup_logic

# konno
# kkonno@soliton-cm.com 
# yuta0126

# Create your views here.

###  メインページを表示させる
@login_required
def main(request):
    return render(request, 'receipts/main.html')

## PDFのページをスキャンする
class InputView(LoginRequiredMixin, View):
    template_name = 'receipts/input.html'
    print("INSIDE THE INPUT VIEW ====")

    def get(self, request, id):
        options = 項目リスト.objects.all().order_by('項目コード')
        selected_option = options[0]
        instance = PDF番号.objects.filter(id=id).first()

        image_path = instance.upload.path
        ocrs = ocr_get(image_path)
        print("INPUT VIEW ocr to get_initial_data ocrs====>>", ocrs)
        initial_data = get_initial_data(ocrs, id)

        print("initial_data ===", initial_data)
        print("Number of forms in initial_data ===", len(initial_data))
        len_ini = len(initial_data)+1
        ReceiptFormSet5 = modelformset_factory(Receipt, form=ReceiptForm, extra=len_ini, can_delete=True)
        ocrs_formset = ReceiptFormSet5(queryset=Receipt.objects.none(),initial=initial_data)
        print("Number of forms in formset:", len(ocrs_formset))
        relative_image_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
        image_url = os.path.join(settings.MEDIA_URL, relative_image_path)
        passing_id = instance.id

        context = {
            'options': options,
            'selected_option': selected_option,
            'ocrs': ocrs_formset,
            'image_path': image_url,
            'passing_id': passing_id,
            'check': 'yes',
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        print("request.POST========>>>>>", request.POST)
        form_data = ReceiptFormSet(request.POST)
        pdf_id = request.POST['form-0-PDF番号']
        instance = PDF番号.objects.filter(id=pdf_id).first()

        if form_data.is_valid():
            print("saved the form data")
            form_data.save()
            instance.processed = True
            instance.save()
        else:
            print("error", form_data.errors, form_data.non_form_errors())
            for f in form_data:
                print("error", f.errors)
            options = 項目リスト.objects.all().order_by('項目コード')
            return render(request, 'receipts/input.html', {
                'options': options,'image_path': request.POST['image_path'],'ocrs': form_data})

        return redirect('list_up_view')

## ドロップアップロード画面を表示させる
class MainView(LoginRequiredMixin, TemplateView):
    template_name = 'receipts/dropupload.html'

## ファイルをアップロードする
@login_required
def file_upload_view(request):

    if request.method == 'POST':
        # print("Files in request:", request.FILES)
        files = request.FILES.getlist('file')
        print("[file_upload_view]-FILES keys:", request.FILES.keys())
        print("[file_upload_view]-FILES dict:", request.FILES)
        print("[file_upload_view]-POST dict:", request.POST)
        # print("FILES ==", files)
        print("[file_upload_view] ==== inside list of files: ", files)
        for uploaded_file in files:
            if uploaded_file.content_type == "application/pdf":  #   pdf doc to jpeg
                # save in the temp folder and obtain ABSOLUTE PATH
                temp_file_path = save_file_to_temp(uploaded_file)
                print("[file_upload_view]- temp_file_path", temp_file_path)
                pdf_to_jpeg(temp_file_path) #, uploaded_file.name)  #   pdf doc to jpeg
                # Delete temp file in temp folder
                os.remove(temp_file_path)
            else:
                # if JPEG directly save
                print("[file_upload_view]- JPEG file to save as uploaded_file", uploaded_file)
                instance = PDF番号.objects.create(upload=uploaded_file, PDF_num=uploaded_file.name)
                # print("File saved to:", instance.upload.path)
        return render(request, 'receipts/success.html')

    return HttpResponseBadRequest('Only POST method allowed')

##　PDFを削除する
class ListUpView(LoginRequiredMixin, TemplateView):

    def get(self, request):

        items = PDFNumFormSet(queryset=PDF番号.objects.all())  #filter(processed=False)
        # print("items in ListUpView", items)
        context = {
            'formset': items,
            'MEDIA_URL': settings.MEDIA_URL
        }
        return render(request, 'receipts/list_up.html', context)
    
    def post(self, request):
        items = PDFNumFormSet(request.POST)
        # print("request.POST", request.POST)

        if 'delete' in request.POST:
            print("delete process started")
            if items.is_valid():
                print("formset saved")

                # delete each jpeg files first before delete PDF番号-models
                for item in items.forms:
                    # Select the item where form-{i}-DELET is 'on'
                    if item.cleaned_data.get('DELETE'):
                        # Obtain each item's instance
                        instance = item.instance
                        print("debug 22", instance)
                        #obtain relative path upload_imates/xxxx.JPG
                        file_field = instance.upload  
                        print("debug 23", file_field)

                        # Delete the JPG file
                        if file_field:
                            # Obtain /project/media/upload_images/xxxx.JPG project path workable in production
                            file_path = file_field.path
                            print("debug 24", file_field)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"Deleted file: {file_path}")
                            else:
                                print(f"File not found: {file_path}")
                        instance.delete()

            else:
                print("formset errors", items.errors)
                for f in items:
                    print("form errors", f.errors)

        if request.POST['filtering'] == '2':
            if PDF番号.objects.all():
                items = PDF番号.objects.all() 
            else:
                items = 'No Value'
        else:
            items = PDF番号.objects.filter(processed=int(request.POST['filtering'])) 
        # print("items", items)
        items = PDFNumFormSet(queryset=items)
        context = {
            'filtering':request.POST['filtering'],
            'formset': items,
            'MEDIA_URL': settings.MEDIA_URL
        }
       
        return render(request, 'receipts/list_up.html', context)


## Jpegリストを表示し、中身も表示させる
class JpegListView(LoginRequiredMixin, ListView):
    template_name = 'receipts/jpeg_all_list.html'
    model = PDF番号

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs) # Article.objects.all() と同じ結果

        # GETリクエストパラメータにkeywordがあれば、それでフィルタする
        keyword = self.request.GET.get('keyword')
        if keyword is not None:
            queryset = queryset.filter(processed='True')

        # is_publishedがTrueのものに絞り、titleをキーに並び変える
        queryset = queryset.filter(processed=True).order_by('PDF_num')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receipt_queryset = Receipt.objects.none()
        formset = ReceiptFormSet(queryset=receipt_queryset)

        context['formset'] = formset
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context
        
    def post(self, request):

        pdf_id = request.POST.getlist('select_field')[0]

        if not pdf_id:
            print("GOING TO NO SELECT VIEW")
            return render(request, 'receipts/jpeg_all_list.html')
        path_info = Receipt.objects.filter(PDF番号=int(pdf_id)).first()
        form_data_queryset  = Receipt.objects.filter(PDF番号=int(pdf_id))
        form_data = ReceiptFormSet(queryset=form_data_queryset)
        left = PDF番号.objects.filter(processed=True).order_by('PDF_num')

        
        if 'save' in request.POST: 
            form_data = ReceiptFormSet(request.POST)
            
            if form_data.is_valid():
                print("FORM SAVED")
                form_data.save()
            else:
                print("Formset is invalid.")
                print(form_data.errors)  # This will give you a dictionary of errors for all the forms in the formset.
                for form in form_data:
                    print(f"Errors for form {form.instance.id}: {form.errors}")

        form_data_queryset  = Receipt.objects.filter(PDF番号=int(pdf_id))
        form_data = ReceiptFormSet(queryset=form_data_queryset)
        context = {
            'path_info': str(path_info.PDF番号.upload),
            'formset': form_data,
            'object_list':left,
            'MEDIA_URL': settings.MEDIA_URL,
            'selected_pdf_id': pdf_id,
            }
        return render(request, 'receipts/jpeg_all_list.html', context)



## 日付や項目コードでソートし表示させ、アップデートも受け付ける。写真も表示
class SortUpdateView(LoginRequiredMixin, View):
    
    def get(self, request):
        options = 項目リスト.objects.all()
        sort_start, sort_end = get_start_date(request.GET.get('sort_start'), request.GET.get('sort_end'))
        sort_account = request.GET.get('sort_account')

        if not sort_start and not sort_end:
            context = {
                    'options': options,
                }
            return render(request, 'receipts/sortupdate.html', context)
        
        else:
            receipts = Receipt.objects.all()

            if sort_account == 'all':
                receipts = receipts.filter(日付__range=[sort_start, sort_end])
            else:
                receipts = receipts.filter(日付__range=[sort_start, sort_end])
                receipts = receipts.filter(項目コード__項目コード=sort_account)
            
            receipts = ReceiptFormSet_no_extra(queryset=receipts)
            context = {
                'sort_start':sort_start,
                'sort_end': sort_end,
                'sort_account': sort_account,
                'options': options,
                'formset': receipts,
                'MEDIA_URL': settings.MEDIA_URL,
            }
            return render(request, 'receipts/sortupdate.html', context)
    
    def post(self, request):
        qs = Receipt.objects.all()
        formset = ReceiptFormSet_no_extra(request.POST, queryset=qs)

        if formset.is_valid():
            formset.save()
            print("saved")
        else:
            print("form error", formset.errors)
            for f in formset:
                print("error", f.errors)

        sort_start = request.POST.get('sort_start')
        sort_end = request.POST.get('sort_end')
        sort_num = request.POST.get('sort_account')
        if sort_num == None:
            sort_account = "all"
        else:
            sort_account = sort_num

        print("sort_account", str(sort_account))

        query_params = {
            'sort_start': sort_start,
            'sort_end': sort_end,
            'sort_account': sort_account,
        }

        # Construct the URL with query parameters
        url = reverse('sortupdate_list')  # URL pattern name
        url_with_params = f"{url}?{urlencode(query_params)}"

        # Redirect to the URL with the query parameters
        return HttpResponseRedirect(url_with_params)

## アイテムと画像を表示してクリックすると登録者番号を確認する    
class SortListView(LoginRequiredMixin, View):
    
    def get(self, request):
        options = 項目リスト.objects.all()

        sort_start, sort_end = get_start_date(request.GET.get('sort_start'), request.GET.get('sort_end'))
        sort_account = request.GET.get('sort_account')

        if not sort_start and not sort_end:
            context = {
                    'options': options,
                }
            return render(request, 'receipts/sortlistview.html', context)
        
        else:
            receipts = Receipt.objects.all()

            print("sort account", sort_account)
            if sort_account == '全て':
                print("NOW IN 全て", sort_account)
                receipts = receipts.filter(日付__range=[sort_start, sort_end])
            else:
                receipts = receipts.filter(日付__range=[sort_start, sort_end])
                receipts = receipts.filter(項目コード__項目コード=sort_account)
            context = {
                'sort_start':sort_start,
                'sort_end': sort_end,
                'sort_account': sort_account,
                'options': options,
                'items': receipts,
                'MEDIA_URL': settings.MEDIA_URL,
            }
            return render(request, 'receipts/sortlistview.html', context)
    



# FUNCTIONS ==
def clean_price(price_str):
    # Remove any commas and convert to integer
    try:
        return int(price_str.replace(',', ''))
    except ValueError:
        # Handle the case where conversion fails (e.g., if the string isn't a valid number)
        return None
    
def get_start_date(start, end):
    today = datetime.today()
    six_months_ago = today - relativedelta(months=6)
    if start:
        sort_start = start
    else:
        sort_start = six_months_ago.strftime('%Y-%m-%d')

    if end:
        sort_end = end
    else:
        sort_end = today.strftime('%Y-%m-%d')

    return sort_start, sort_end

"""
CREATE DATABASE BACKUP
"""
def local_db_backup_view(request):
    """Django view to trigger the local database backup."""
    try:
        local_copy_path = backup_logic.copy_local_db()
        filename = os.path.basename(local_copy_path)
        # Success message, maybe include the filename
        return HttpResponse(f"Successfully created local backup:<br>{filename}<br><br>Now you can try copying to NAS.")
    except FileNotFoundError as e:
        return HttpResponse(f"Error: {e}", status=404) # Not Found
    except PermissionError as e:
        return HttpResponse(f"Error: {e}", status=403) # Forbidden
    except Exception as e:
        # Catch any other exceptions from the logic
        return HttpResponse(f"An unexpected error occurred during local backup: {e}", status=500) # Internal Server Error

def nas_db_backup_view(request):
    """Django view to trigger copying the latest local backup to NAS."""
    try:
        nas_copy_path = backup_logic.copy_to_nas()
        filename = os.path.basename(nas_copy_path)
        # Success message
        return HttpResponse(f"Successfully copied local backup to NAS:<br>{filename}")
    except FileNotFoundError as e:
        # This specific error means no local backup was found by copy_to_nas
        return HttpResponse(f"Error: {e}<br>Please run 'Copy Local DB' first.", status=404)
    except OSError as e:
        # Error accessing/creating NAS directory
        return HttpResponse(f"Error: Cannot access NAS directory. {e}", status=500)
    except PermissionError as e:
         return HttpResponse(f"Error: Permission denied to write to NAS directory. {e}", status=403)
    except Exception as e:
        # Catch any other exceptions
        return HttpResponse(f"An unexpected error occurred during NAS copy: {e}", status=500)

# Optional: A simple view to display the links
def backup_home_view(request):
    context = {
        'SOURCE_DB_PATH': backup_logic.SOURCE_DB_PATH,
        'LOCAL_BACKUP_DIR': backup_logic.LOCAL_BACKUP_DIR,
        'NAS_BACKUP_DIR': backup_logic.NAS_BACKUP_DIR,
    }
    return render(request, 'receipts/backup_home.html', context) # You'll create this template next


"""
CREATE POSTGRES DATABASE BACKUP
"""
def postgres_db_backup_to_nas_as_json(request):
    """Django view to dump json data as backup to NAS."""
    try:
        local_copy_path = backup_logic.dump_postgres_to_json()
        filename = os.path.basename(local_copy_path)
        # Success message, maybe include the filename
        return HttpResponse(f"Successfully dump json data to NAS:<br>{filename}<br><br>{local_copy_path}")
    except FileNotFoundError as e:
        return HttpResponse(f"Error: {e}", status=404) # Not Found
    except PermissionError as e:
        return HttpResponse(f"Error: {e}", status=403) # Forbidden
    except Exception as e:
        # Catch any other exceptions from the logic
        return HttpResponse(f"An unexpected error occurred during local backup: {e}", status=500) # Internal Server Error


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def restore_view(request):
    if request.method == "POST":
        json_file = request.FILES.get("json_file")
        if not json_file:
            return HttpResponse("No file uploaded", status=400)
        
        # save temporary
        temp_path = f"/tmp/{json_file.name}"
        with open(temp_path, "wb+") as f:
            for chunk in json_file.chunks():
                f.write(chunk)
        
        # Load into DB
        try:
            # ⚠️ Wipe all existing data
            subprocess.run(["python", "manage.py", "flush", "--noinput"], check=True)
            
            # ✅ Load new data
            subprocess.run(["python", "manage.py", "loaddata", temp_path], check=True)
            
            return HttpResponse(f"Restored database from {json_file.name}")
        except subprocess.CalledProcessError as e:
            return HttpResponse(F"Restore failed: {e}", status=500)
        finally:
            os.remove(temp_path)
    else:
        return render(request, "receipts/restore_postgres.html")