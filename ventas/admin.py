from django.contrib import admin

from .models import Cliente, DetalleVenta, NotaVenta


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'ci_nit', 'celular', 'email')
	search_fields = ('nombre', 'ci_nit', 'email')


class DetalleVentaInline(admin.TabularInline):
	model = DetalleVenta
	extra = 0


@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'empleado', 'cliente', 'fecha', 'total')
	list_filter = ('fecha', 'empleado')
	search_fields = ('empleado__nombre', 'cliente__nombre')
	inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nota_venta', 'producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal')
	list_filter = ('producto',)
	search_fields = ('nota_venta__id', 'producto__nombre')
