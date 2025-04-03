import os
import threading
import time

from PIL.Image import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import render
from pdf2image import convert_from_path
from .forms import UploadFileForm
from pdf2docx import Converter
from AConvertDoc import settings
import easyocr
import numpy as np
from .forms import UploadFileForm


def delete_file_after_delay(file_path, delay=10):
    """Удаляет файл через 10 секунд после отправки пользователю."""
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)


def check_pages_count(request, images, count_pages):
    if len(images) > count_pages:
        request.method = ''
        return start(request, f'СТРАНИЦ БОЛЬШЕ {count_pages}!')
    else:
        return False


def upload_file(request):
    uploaded_file = request.FILES['file']
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_url = os.path.join(settings.MEDIA_ROOT, 'uploads/', filename)
    return file_url

def start(request, ErrorMessage = ''):
    context = {}
    if ErrorMessage != '':
        context['ErrorMessage'] = ErrorMessage
    if request.method == "POST":
        file_url = upload_file(request)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            selected_choice = form.cleaned_data["choice"]  # Получаем значение

            # Тут надо проверить выбор функции пользователем
            # -----------------------------------------------------------
            if selected_choice == '1':
                return conversion(request, file_url)
            elif selected_choice == '2':
                return  text_recognition(request, file_url)
            # -----------------------------------------------------------
        else:
            validation = 'Валидация формы не пройдена'
            context['validation'] = validation
    form = UploadFileForm()
    context['form'] = form
    return render(request, "base.html", context = context)


# Распознать текст
def text_recognition(request, file_url):
    reader = easyocr.Reader(['ru', 'en'], gpu=False)  # workers = количество ядер, ['ru', 'en'] = языки
    with open(os.path.join(settings.MEDIA_ROOT, 'result_scan/', 'result.txt'), "w", encoding="utf-8") as file:

        # Проверяем расшинение файла
        if 'pdf' in os.path.splitext(file_url)[1]:
            images = convert_from_path(file_url)

            check_pages_count(request, images, 5)
            check_file = check_pages_count(request, images, 5)
            if check_file:
                return check_file

            # if len(images) > 5:
            #     request.method = ''
            #     return start(request, 'СТРАНИЦ БОЛЬШЕ 5ти!')

            # Разбираем PDF на отдельные картинки
            i = 0
            for image in images:
                image_np = np.array(image)
                text = reader.readtext(image_np, detail=0)  # detail=0 → только текст
                i += 1
                file.write(f"Страница {i}:\n")
                file.write("".join(text) + "\n\n")
        else:
            text = reader.readtext(file_url, detail=0)
            file.write(f"Страница IMG:\n")
            file.write("".join(text) + "\n\n")
    file.close()

    # Путь для скачивания
    url_download = os.path.join(settings.MEDIA_ROOT, 'result_scan/', 'result.txt')
    response = FileResponse(open(str(url_download), "rb"), as_attachment=True)
    return response

# Конвертировать PDF в WORD
def conversion(request, file_url):

    # Проверяем наличие файла
    if not os.path.exists(file_url):
        return HttpResponse("Ошибка: файл не найден", status=400)

    images = convert_from_path(file_url)
    check_file = check_pages_count(request, images, 100)
    if check_file:
        return check_file

    # Задаём путь для сохранения результата в /media/converted/
    converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    os.makedirs(converted_dir, exist_ok=True)

    # Берем вермя для использовании его в имени
    time_file = str(time.time())
    give_file_url = os.path.join(converted_dir, time_file + '.docx')
    cv = Converter(file_url)
    cv.convert(str(give_file_url))
    cv.close()

    # Проверяем, существует ли файл
    if not os.path.exists(give_file_url):
        return HttpResponse("Файл не найден", status=404)
    else:
        if os.path.exists(file_url):
            os.remove(file_url)
    response = FileResponse(open(give_file_url, "rb"), as_attachment=True)
    threading.Thread(target=delete_file_after_delay, args=(give_file_url,), daemon=True).start()
    return response
    #return render(request, "base.html", {"download_url": FileResponse})

