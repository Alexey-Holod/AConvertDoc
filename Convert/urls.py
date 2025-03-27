from django.urls import path
from .views import *

urlpatterns = [
    path('', start, name='/'),
    # path('text_recognition/', text_recognition, name='text_recognition'),
]
