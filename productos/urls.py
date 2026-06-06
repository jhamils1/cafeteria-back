from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoriaProductoViewSet, ProductoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet, basename='categorias')
router.register(r'productos', ProductoViewSet, basename='productos')

urlpatterns = [
    path('', include(router.urls)),
]