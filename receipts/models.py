from django.db import models

# Create your models here.

class 項目リスト(models.Model):
    項目コード = models.CharField(max_length=32, primary_key=True)
    項目印字名 = models.CharField(max_length=100)
    項目短縮名 = models.CharField(max_length=50, blank=True) 
    項目レポート分類区分 = models.CharField(max_length=100)

    def __str__(self):
        return self.項目短縮名 if self.項目短縮名 else self.項目印字名  # Return tenant name as string representation

class PDF番号(models.Model):
    PDF_num = models.CharField(max_length=50)
    upload = models.ImageField(upload_to='upload_images/')
    processed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Receipt(models.Model):
    日付 = models.DateField()
    項目コード = models.ForeignKey(項目リスト,on_delete=models.CASCADE, db_index=True)
    価格 = models.PositiveIntegerField(default=0)
    登録番号 = models.BigIntegerField(default=0)
    備考 = models.CharField(max_length=255, blank=True, null=True)
    PDF番号 = models.ForeignKey(PDF番号, on_delete=models.CASCADE, db_index=True, related_name='receipts_by_pdf_number')

