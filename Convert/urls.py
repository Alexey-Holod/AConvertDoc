from django.urls import path
from .views import *

urlpatterns = [
    path('', upload_file, name='/'),
    # path('text_recognition/', text_recognition, name='text_recognition'),
]
