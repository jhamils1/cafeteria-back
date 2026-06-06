from django.contrib import admin

from .models import CategoriaProducto, MovimientoInventario, Producto


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'descripcion')
	search_fields = ('descripcion',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'codigo', 'nombre', 'categoria', 'precio_venta', 'stock', 'estado')
	list_filter = ('estado', 'categoria')
	search_fields = ('codigo', 'nombre')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha')
	list_filter = ('tipo', 'fecha')
	search_fields = ('producto__nombre', 'descripcion', 'usuario__username')
