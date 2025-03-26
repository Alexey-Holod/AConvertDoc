import os
from time import time

from PIL.Image import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import render
from fontTools.misc.cython import returns
from pdf2image import convert_from_path

from .forms import UploadFileForm
from pdf2docx import Converter
from AConvertDoc import settings
import easyocr
import numpy as np


# def text_recognition(request):
#     reader = easyocr.Reader(['ru', 'en'], gpu=False, workers=2)  # workers = количество ядер, ['ru', 'en'] = языки
#     file = upload_file(request, scaner=True)
#     result = reader.readtext(file, detail=0)
#     print('*****EASYOCR*****\n', result)


def upload_file(request, scaner=True):
    if request.method == "POST" and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = os.path.join(settings.MEDIA_ROOT, 'uploads/', filename)

        # -----------------------------/-----------------------------
        # Балуюсь с EASYOCR
        # Если пользователь выбрал распознать текст со скана
        if scaner:
            reader = easyocr.Reader(['ru', 'en'], gpu=False)  # workers = количество ядер, ['ru', 'en'] = языки

            with open(os.path.join(settings.MEDIA_ROOT, 'result_scan/', 'result.txt'), "w", encoding="utf-8") as file:

                # Проверяем расшинение файла
                if os.path.splitext(file_url)[1] == '.pdf':
                    images = convert_from_path(file_url)

                    # Разбираем PDF на отдельные картинки
                    i = 0
                    for image in images:
                        image_np = np.array(image)
                        text = reader.readtext(image_np, detail=0)  # detail=0 → только текст
                        i += 1
                        file.write(f"Страница {i}:\n")
                        file.write("".join(text) + "\n\n")
                else:
                    image = reader.readtext(image_np, detail=0)  # detail=0 → только текст


            file.close()

            # Путь для скачивания
            url_download = os.path.join(settings.MEDIA_ROOT, 'result_scan/', 'result.txt')
            response = FileResponse(open(str(url_download), "rb"), as_attachment=True)
            return response

# -----------------------------/-----------------------------

        if not scaner:

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
