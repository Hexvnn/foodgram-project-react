from django.urls import path, include
from rest_framework import routers

from .views import (
    CustomUserViewSet,
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
)
router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
