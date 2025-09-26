# pip install pdf2image
# https://github.com/oschwartz10612/poppler-windows/releases/

from pdf2image import convert_from_path

poppler_path = r'C:/Users/konno/OneDrive - SCM/Dev/sapps/poppler-24.07.0/Library/bin'

pages = convert_from_path('sapps\ocr_v1\media\p1.pdf', poppler_path=poppler_path)
# pages = convert_from_path('CCF_000032.pdf', poppler_path=poppler_path)

# Save each page as a JPEG file using Pillow

for i, page in enumerate(pages):
	page.save(f'sapps\ocr_v1\media\page_{i}.jpg', 'JPEG')

# pages[0].save(f'p1.jpg', 'JPEG')