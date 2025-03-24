import os
from time import time
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from pdf2docx import Converter
from AConvertDoc import settings


def upload_file(request):
    if request.method == "POST" and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        # file_url = fs.url(filename)
        file_url = os.path.join(settings.MEDIA_ROOT, filename)
        give_file_url = os.path.join(settings.MEDIA_ROOT, str(time()) + '.docx')
        print('filename -', filename)
        print('file_url -', file_url)

        cv = Converter(file_url)
        cv.convert(give_file_url)
        cv.close()
        return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request, "base.html", {"form": form})
# Create your views here.
