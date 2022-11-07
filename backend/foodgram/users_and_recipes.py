from users.models import User
from api.models import Recipe

from api.models import Tag
Tag.objects.create(name='завтрак', color = '#ffa500', slug = 'breakfast').save()
Tag.objects.create(name='обед', color = '#008000', slug = 'lunch').save()   
Tag.objects.create(name='ужин', color = '#ee82ee', slug = 'dinner').save()  

# скрипт с ингредиентами

print ('hello')
for i in range(9):
    new_user = User.objects.create(
        username = f'username{i}', 
        email= f'email{i}',
        first_name = f'first_name{i}',
        last_name = f'last_name{i}'
        )

for i in range(9):
    print (i)
    new_recipe = Recipe.objects.create(name = f'recipe{i}', cooking_time = i, 
    author = User.objects.get(pk=47+i), image = '1')
    new_recipe.save()    

from api.models import RecipeTag, Recipe,Tag
recipes = Recipe.objects.all().values_list('id', flat=True)
for i in recipes[0:3]:
    rt = RecipeTag.objects.create(
        recipe= Recipe.objects.get(pk=i),
        tag = Tag.objects.get(slug='breakfast')
    )
    print (rt)


for i in recipes[3:5]:
    rt = RecipeTag.objects.create(
        recipe= Recipe.objects.get(pk=i),
        tag = Tag.objects.get(slug='dinner')
    )
    print (rt)

for i in recipes[6:9]:
    rt = RecipeTag.objects.create(
        recipe= Recipe.objects.get(pk=i),
        tag = Tag.objects.get(slug='dinner')
    )
    print (rt)