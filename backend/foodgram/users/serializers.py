from api.models import Recipe
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Subscription, User


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserSerializer(UserSerializer):
    is_surbscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_surbscribed')

    def get_is_surbscribed(self, obj):
        return self.context.get('request').user.follower.filter(
            author=obj).exists()


class UserRegistrSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    first_name = serializers.CharField(
        required=True,
    )
    last_name = serializers.CharField(
        required=True,
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        instance = User.objects.create(**validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False, source='author.email')
    id = serializers.IntegerField(required=False, source='author.id')
    username = serializers.CharField(required=False, source='author.username')
    first_name = serializers.CharField(
        required=False, source='author.first_name')
    last_name = serializers.CharField(
        required=False, source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    # Используем methodfield
    # засунем nested serializer в функцию get_serializer, чтобы добавить
    # фильтрацию по recipes_limit
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all().order_by('-id')
        if 'recipes_limit' in self.context.get('request').query_params:
            recipes_limit = int(self.context.get(
                'request').query_params.get('recipes_limit'))
            recipes = recipes[:recipes_limit]
        serializer = RecipeForSubscriptionSerializer(recipes, many=True,)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def get_is_subscribed(self, obj):
        return self.context.get('request').user.follower.filter(
            author=obj.author).exists()

    def save(self, **kwargs):
        follower = self.context.get('request').user
        author_id = self.context.get('view').kwargs.get('id')
        author = User.objects.get(id=author_id)
        self.instance = Subscription.objects.create(
            author=author, follower=follower)
        return self.instance
