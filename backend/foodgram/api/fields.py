import base64
# Модуль с функциями кодирования и декодирования base64
from django.core.files.base import ContentFile
# Модуль для создания файла из base64
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для управления картинками"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            # декодируем
            ext = format.split('/')[-1]
            # делим строку на части
            # и извлечкаем расширение файла.
            data = ContentFile(base64.b64decode(imgstr), name='recipe.' + ext)
            # Сохраняем в файл
        return super().to_internal_value(data)

    def to_representation(self, value):
        return value.url
