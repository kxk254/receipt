from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.main, name="main"),
    path('dropupload/', views.MainView.as_view(), name="main-upload"),
    path('upload/', views.file_upload_view, name="upload-view"),
    # path('input/', views.input_view, name="input-view"),
    # path('input/<int:id>/', views.input_view, name="input-view-id"),

    path('input/<int:id>/', views.InputView.as_view(), name='input_view'),
    # path('create/', views.CreateReceiptView.as_view(), name='create_view'),
    path('create/', views.InputView.as_view(), name='create_view'),

    path('list_up/', views.ListUpView.as_view(), name="list_up_view"),

    path('jpeg_list/', views.JpegListView.as_view(), name="jpeg_all_list"),

    path('sortupdate/', views.SortUpdateView.as_view(), name="sortupdate_list"),
    path('sortlist/', views.SortListView.as_view(), name="sort_list"),

    ### BACKUP ROUTE
    # URL for the home page (optional)
    path('backup/', views.backup_home_view, name='backup_home'),

    # URL to trigger the local backup
    path('backup/local/', views.local_db_backup_view, name='local_db_backup'),

    # URL to trigger the NAS copy (copies the latest local backup)
    path('backup/nas/', views.nas_db_backup_view, name='nas_db_backup'),

    # POSTGRES
    path('postgres_backup/', views.postgres_db_backup_to_nas_as_json, name='postgres-backup'),
    path('restore/', views.restore_view, name='restore-db'),


]  
