FROM python:3.10-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX /usr/share/tessdata

WORKDIR /receipt

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# # Install dependencies and Tesseract
# RUN apt-get update && apt-get install -y \
#     tesseract-ocr=5.3.4-1build5 \
#     libtesseract-dev=5.3.4-1build5 \
#     tesseract-ocr-eng=1:4.1.0-2 \
#     tesseract-ocr-jpn=1:4.1.0-2 \
#     tesseract-ocr-osd=1:4.1.0-2 \
#     && rm -rf /var/lib/apt/lists/*

# # OPTION2 =================================================

# # Install necessary tools for adding repositories
# RUN apt-get update && apt-get install -y software-properties-common && rm -rf /var/lib/apt/lists/*

# # Add Tesseract PPA for newer versions
# RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel \
#     && apt-get update && apt-get install -y \
#         tesseract-ocr \
#         libtesseract-dev \
#         tesseract-ocr-eng \
#         tesseract-ocr-jpn \
#         tesseract-ocr-osd \
#     && rm -rf /var/lib/apt/lists/*
# # OPTION2 =================================================

# OPTION 3 ===============================================
RUN apt-get update && apt-get install -y tesseract-ocr

# Download language data manually for Tesseract 5.x
RUN mkdir -p /usr/share/tessdata && \
    wget -O /usr/share/tessdata/jpn.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/jpn.traineddata && \
    wget -O /usr/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata && \
    wget -O /usr/share/tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/osd.traineddata
# OPTION 3 ===============================================

# Verify installation
RUN tesseract --version

# # Create tessdata directory if it doesn't exist
# RUN mkdir -p $TESSDATA_PREFIX

# # Download Japanese language data files
# RUN curl -L -o $TESSDATA_PREFIX/jpn.traineddata \
#     https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata && \
#     curl -L -o $TESSDATA_PREFIX/jpn_vert.traineddata \
#     https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata && \
#     curl -L -o $TESSDATA_PREFIX/jpn_vert_fast.traineddata \
#     https://github.com/tesseract-ocr/tessdata_fast/raw/main/jpn_vert.traineddata

COPY .  .

# Expose the port your Django app runs on
EXPOSE 8000

CMD ["gunicorn", "ocr_v1.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]