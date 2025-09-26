import fitz  # PyMuPDF
from PIL import Image
from receipts.models import PDF番号
import os
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files import File
import datetime
import tempfile # Import tempfile module
import logging
# pip install pymupdf pillow

def handle_uploaded_file(f, filename):
    with open(filename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Function to convert PDF to JPEG
def pdf_to_jpeg(file_path, file_name, dpi=300):

    """ You have a PDF file uploaded by a user, 
    and you want to convert each page of that PDF into a 
    separate image (specifically a JPEG) and save each image 
    in your database, linked to a record. 

    The code takes an uploaded PDF, goes through each page, 
    converts each page into a separate high-quality JPEG image, 
    and saves each of these page-images as its own entry 
    in the database using the PDF番号 model. Temporary files 
    are used during the process and cleaned up automatically.
    
    """

    logger.info(f"Starting PDF to JPEG conversion for: {file_name}")

    pdf_document = None
    processed_instances = []

    try:
        pdf_document = fitz.open(file_path)
        num_pages = pdf_document.page_count

        zoom_factor = dpi / 72
        zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)

        for page_num in range(num_pages):
            temp_jpeg_path = None
            page = None

            try:
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=zoom_matrix)

                # Convert pixmap to RGB (or RGBA if it had alpha) for consistent PIL processing
                # This handles different input color spaces like CMYK gracefully.
                if pix.colorspace.n > 3 and not pix.alpha: # Handle CMYK explicitly for clarity
                    # Convert to RGB colorspace. fitz.csRGB handles the conversion.
                    new_pix = fitz.Pixmap(fitz.csRGB, pix)
                    pix = new_pix # Replace the original pixmap with the RGB one
                    logger.info(f"Converted page {page_num + 1} from {pix.colorspace.name} to RGB.")
                    # Important: If new_pix was created, the original 'pix' might need freeing,
                    # but PyMuPDF's Python bindings often manage this automatically.
                    # Explicitly deleting might be safer if memory is an issue, but let's test this first.
                    # if 'new_pix' in locals() and new_pix is not pix: del new_pix # Optional cleanup

                # Convert the pixmap to a PIL Image
                img = pixmap_to_pil(pix)

                # --- Save the image to a temporary JPEG file using tempfile ---
                fd, temp_jpeg_path = tempfile.mkstemp(suffix='.jpg')
                os.close(fd)

                # JPEG does not support alpha channels. If the image is RGBA,
                # convert it to RGB before saving to prevent invalid JPEG file issues.
                if img.mode == "RGBA":
                    # Convert to RGB. Pillow handles transparency (often by compositing
                    # onto a white background, which is typical for document images).
                    img = img.convert("RGB")
                    logger.info(f"Converted RGBA PIL image to RGB for JPEG save for page {page_num + 1}.")


                img.save(temp_jpeg_path, "JPEG", quality=95)
                logger.info(f"Saved temporary JPEG for page {page_num + 1} to : {temp_jpeg_path}")

                # --- Open the temporary JPEG file and save it via Django model ---
                with open(temp_jpeg_path, 'rb') as img_file:
                    django_file = File(img_file)
                    current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    instance_name = f"{os.path.splitext(file_name)[0]}_page_{page_num + 1}"

                    instance = PDF番号.objects.create(
                        upload=django_file,
                        PDF_num=instance_name
                    )
                    processed_instances.append(instance)
                    logger.info(f"Created PDF番号 instance for {instance_name}, save to :{instance.upload.path}")
            
            except Exception as e:
                # Log the error for this specific page, but continue with other pages if possible
                logger.error(f"Error processing page {page_num + 1} of {file_name}: {e}", exc_info=True)
                # Clean up the temporary JPEG file if it was created before the error
                if temp_jpeg_path and os.path.exists(temp_jpeg_path):
                     try:
                         os.remove(temp_jpeg_path)
                         logger.info(f"Cleaned up temp JPEG: {temp_jpeg_path}")
                     except OSError as cleanup_err:
                         logger.error(f"Error cleaning up temp JPEG {temp_jpeg_path}: {cleanup_err}")
                # Depending on requirements, you might want to skip this page or stop processing
                # For now, we log and continue to the next page

            finally:
                 # Ensure the temporary JPEG file is deleted *after* it's saved by Django
                 if temp_jpeg_path and os.path.exists(temp_jpeg_path):
                     try:
                         os.remove(temp_jpeg_path)
                         logger.info(f"Cleaned up temp JPEG: {temp_jpeg_path}")
                     except OSError as cleanup_err:
                         logger.error(f"Error cleaning up temp JPEG {temp_jpeg_path}: {cleanup_err}")

    except fitz.FileDataError as e:
        logger.error(f"Error opening PDF file {file_path}: {e}", exc_info=True)
        # Handle cases where the PDF is invalid or corrupted
        # You might want to return an error response or status here
        # Return the instances successfully processed before the error
        return processed_instances # Or raise the exception after logging
    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF processing for {file_name}: {e}", exc_info=True)
        # Handle any other unexpected errors during PDF conversion
        # Return the instances successfully processed before the error
        return processed_instances # Or raise the exception after logging
    finally:
        # Ensure the PDF document is closed even if errors occur
        if pdf_document:
            pdf_document.close()
            logger.info("PDF document closed.")
        # The temporary PDF file created by save_file_to_temp is cleaned up in the caller (file_upload_view)


    logger.info(f"Finished processing PDF: {file_name}")
    return processed_instances # Return list of successfully created instances
    
    # pdf_document = fitz.open(file_path)
    # output_directory = os.path.join(settings.MEDIA_ROOT, 'upload_images')
    # zoom_factor = dpi / 72  # 72 is the default DPI of PyMuPDF
    # zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
    
    # # Loop through each page
    # for page_num in range(pdf_document.page_count):
    #     # Load a page
    #     page = pdf_document.load_page(page_num)
    #     # Get a pixmap (image) of the page
    #     pix = page.get_pixmap(matrix=zoom_matrix)
        
    #     # Convert the pixmap to a PIL Image
    #     img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #     current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #     # file_name_without_ext, _ = os.path.splitext(file_name)
    #     img_filename = f"{current_datetime}_page_{page_num + 1}.jpg"
    #     # img_path = os.path.join('media\\upload_images\\', img_filename)
    #     img_path = os.path.join('', img_filename)
    #     # print("image path", img_path)
    #     img.save(img_path, "JPEG", quality=95)


    #     with open(img_path, "rb") as img_file:
    #         django_file = File(img_file)
    #         instance = PDF番号.objects.create(upload=django_file, PDF_num=f"{current_datetime}_Page {page_num + 1}")
    #         # print("File saved to:", instance.upload.path)
    #     os.remove(img_path)

    
    # # Close the PDF document
    # pdf_document.close()

def save_file_to_temp(uploaded_file):
    """Saves an InMemoryUploadedFile or TemporaryUploadedFile to a temporary file."""
    # Save the uploaded file to a temporary location
    # temp_file_path = default_storage.save(f"temp/{uploaded_file.name}", uploaded_file)
    # return os.path.join(settings.MEDIA_ROOT, temp_file_path)

    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(uploaded_file.name)[1])

    try:
        with os.fdopen(fd, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
    
    except Exception as e:
        logger.error(f"Error saving uploaded file to temp: {e}")
        os.remove(temp_path)
        raise

    logger.info(f"Saved uploaded file to temporary path: {temp_path}")
    return temp_path
