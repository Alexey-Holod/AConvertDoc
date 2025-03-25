import os
from time import time
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import render
from .forms import UploadFileForm
from pdf2docx import Converter
from AConvertDoc import settings


def upload_file(request):
    if request.method == "POST" and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = os.path.join(settings.MEDIA_ROOT, 'uploads/', filename)

        # Проверяем наличие файла
        if not os.path.exists(file_url):
            return HttpResponse("Ошибка: файл не найден", status=400)

        # Задаём путь для сохранения результата в /media/converted/
        converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
        os.makedirs(converted_dir, exist_ok=True)

        # Берем вермя для использовании его в имени
        time_file = str(time())
        give_file_url = os.path.join(converted_dir, time_file + '.docx')

        cv = Converter(file_url)
        cv.convert(str(give_file_url))
        cv.close()

        # Проверяем, существует ли файл
        if not os.path.exists(give_file_url):
            return HttpResponse("Файл не найден", status=404)
        else:
            # Путь для скачивания
            url_download = os.path.join(settings.MEDIA_URL, 'converted/', time_file + '.docx')

        return render(request, "base.html", {"download_url": url_download})
    else:
        form = UploadFileForm()
    return render(request, "base.html", {"form": form})
# Create your views here.
