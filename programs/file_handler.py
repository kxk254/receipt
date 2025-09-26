import fitz  # PyMuPDF
from PIL import Image
from receipts.models import PDF番号
import os, io
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
import datetime
# pip install pymupdf pillow

def handle_uploaded_file(f, filename):
    with open(filename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# Function to convert PDF to JPEG
def pdf_to_jpeg(file_path, dpi=300):
    
    #open the document
    pdf_document = fitz.open(file_path)
    print("[pdf_to_jpeg]- page count ==>", pdf_document.page_count)
    output_directory = os.path.join(settings.MEDIA_ROOT, 'upload_images')
    print("[pdf_to_jpeg]-output directory", output_directory)

    # create high resolution pixels
    zoom_factor = dpi / 72  # 72 is the default DPI of PyMuPDF
    zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
    
    # Loop through each page
    for page_num in range(pdf_document.page_count):
        # Load a page
        print("[pdf_to_jpeg]- processing page -->:", page_num)
        page = pdf_document.load_page(page_num)
        # Get a pixmap (image) of the page
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # build a unique filename with current datetime & page
        img_filename = f"{current_datetime}_page_{page_num + 1}.jpg"
        # construct the ABSOLUTE PATH to C:~~/media/upload_images/xxx.JPG
        img_path = os.path.join(output_directory, img_filename)
        # save the img object as a JPEG to a file, using ABSOLUTE PATH
        # Save to in-memory buffer
        img_io = io.BytesIO()
        img.save(img_io, format="JPEG", quality=95)
        img_io.seek(0)

        # File, add metadata, assess to django storage system, consistency with storage backend
        django_file = ContentFile(img_io.read(), name=img_filename)
        # django_file is ABSOLUTE PATH C:~~/media/upload_images/xxx.JPG
        # Then reduce to only basename xxxx.JPG
        django_file_basename = os.path.basename(img_path)
        print("[pdf_to_jpeg]-django file basename", django_file_basename, "| [pdf_to_jpeg]-django file to safe ==>", django_file)
        
        instance = PDF番号(PDF_num=f"{current_datetime}_Page {page_num + 1}")
        instance.upload.save(f"{django_file_basename}", django_file)
        instance.save()
        # print("File saved to:", instance.upload.path)
    
    # Close the PDF document
    pdf_document.close()

def save_file_to_temp(uploaded_file):
    # Save the uploaded file to a temporary location
    temp_dir = os.path.join(settings.BASE_DIR, 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    print("[save_file_to_temp]-os.makedirs(temp_dir, exist_ok=True)", os.makedirs(temp_dir, exist_ok=True))

    # extract file name only ####.JPDF
    filename = os.path.basename(uploaded_file.name)
    print("[save_file_to_temp]-filename", filename)
    # Add direction C:\Users\konno\SynologyDrive\develop\receipt\receiptfordev202505\receipts\temp_uploads\CCF_000205.pdf
    temp_file_path = os.path.join(temp_dir, filename)
    print("[save_file_to_temp]-temp_file_path", temp_file_path)

    # save temp file in binary mode
    with open(temp_file_path, 'wb+') as destination:
        # chunk method that returns the uploaded file's content in smapp lieces, to save memory
        for chunk in uploaded_file.chunks():
            # save the chunk file
            destination.write(chunk)
    return temp_file_path
