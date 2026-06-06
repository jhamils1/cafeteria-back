from rest_framework import viewsets

from backend_cafeteria.permissions import IsStaffOrReadOnly

from .models import CategoriaProducto, Producto
from .serializers import CategoriaProductoSerializer, ProductoSerializer


class CategoriaProductoViewSet(viewsets.ModelViewSet):
	queryset = CategoriaProducto.objects.all().order_by('id')
	serializer_class = CategoriaProductoSerializer
	permission_classes = [IsStaffOrReadOnly]


class ProductoViewSet(viewsets.ModelViewSet):
	queryset = Producto.objects.all().select_related('categoria')
	serializer_class = ProductoSerializer
	permission_classes = [IsStaffOrReadOnly]
