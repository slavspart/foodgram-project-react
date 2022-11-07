import pandas
# библиотека для работы c csv
import os
from api.models import Ingredient
file_path = os.path.join(os.getcwd(), '../../data/ingredients.csv')
print (file_path)   
#указываем путь до файла
data_frame = pandas.read_csv(file_path, names=['name','measurement_unit'])
#  переводим csv в объект data_frame и поскольку отсутствуют
#  названия столбцов даем им названия
data_frame.to_csv()
# # # сохраняем изменения в csv

for i in range(len(data_frame)):
    new_ingredient = Ingredient.objects.create(
        name=data_frame['name'][i],
        measurement_unit=data_frame['measurement_unit'][i]
        )
    # перебираем в цикле изменения и создаем ингредиенты
    # запускаем скрипт python manage.py shell < название файла
    new_ingredient.save()
    print (new_ingredient)
