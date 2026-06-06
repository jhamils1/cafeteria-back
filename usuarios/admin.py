from django.contrib import admin

from .models import Bitacora, Estado


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'activo')
	list_filter = ('activo',)
	search_fields = ('usuario__username',)


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'accion', 'fecha')
	list_filter = ('accion', 'fecha')
	search_fields = ('usuario__username', 'accion', 'detalle')
	ordering = ('-fecha',)
