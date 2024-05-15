import base64

from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.serializers import ModelSerializer

from djoser.serializers import UserCreateSerializer

from recipes.models import (
    Tag, Ingredient, Recipe, IngredientInRecipe,
    Subscribe, Favorite, ShoppingCart,
)

from users.models import User


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=user, author=obj.id).exists()
        return False


class CreateUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):

    class Meta:

        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:

        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    MIN_AMOUNT = 1

    @staticmethod
    def validate_amount(value):

        if value < CreateIngredientsInRecipeSerializer.MIN_AMOUNT:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть больше 0!'
            )
        return value

    class Meta:

        model = IngredientInRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)

    class Meta:

        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):

        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate_ingredients(self, data):
        list_ingredient = []
        for ingredient in data:
            ingredient_id = ingredient.get('id')
            if ingredient_id in list_ingredient:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными!'
                )
            list_ingredient.append(ingredient_id)
            try:
                Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с id={ingredient_id} не существует!'
                )
        if not data:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым!'
            )
        return data

    def validate_tags(self, data):
        if len(data) != len(set(data)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными!'
            )

        if not data:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым!'
            )
        return data

    def create_ingredients(self, ingredients, recipe):

        ingredient_ids = [element['id'] for element in ingredients]
        existing_ingredients = Ingredient.objects.filter(pk__in=ingredient_ids)
        ingredient_map = {ingredient.id: ingredient for ingredient in existing_ingredients}

        ingredients_to_create = []
        for element in ingredients:
            ingredient_id = element['id']
            amount = element['amount']
            if ingredient_id in ingredient_map:
                ingredient = ingredient_map[ingredient_id]
                ingredients_to_create.append(
                    IngredientInRecipe(
                        ingredient=ingredient,
                        recipe=recipe,
                        amount=amount
                    )
                )
        
        IngredientInRecipe.objects.bulk_create(ingredients_to_create)

    def create_tags(self, tags, recipe):

        recipe.tags.set(tags)

    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if ingredients_data is None:
            raise serializers.ValidationError(
                '''Запрос на обновление рецепта должен содержать поле
                `ingredients`!'''
            )

        if tags_data is None:
            raise serializers.ValidationError(
                '''Запрос на обновление рецепта должен содержать поле
                `tags`!'''
            )

        IngredientInRecipe.objects.filter(recipe=instance).delete()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=instance, amount=amount
            )

        return super().update(instance, validated_data)


class AdditionalForRecipeSerializer(serializers.ModelSerializer):

    class Meta:

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)


    def validate(self, data):
        author = data['author']
        user = self.context.get('request').user
        change_subscription_status = Subscribe.objects.filter( 
            user=user.id, author=author.id 
        )
        if change_subscription_status.exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author}!',
                status=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                'Вы пытаетесь подписаться на самого себя!',
                status=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):

        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return AdditionalForRecipeSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class AddFavoritesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
