from django.contrib import admin

from .models import Empleado, EstadoCivil, Nacionalidad, Salario, TipoContrato, Turno


@admin.register(EstadoCivil)
class EstadoCivilAdmin(admin.ModelAdmin):
	list_display = ('id', 'descripcion')
	search_fields = ('descripcion',)


@admin.register(Nacionalidad)
class NacionalidadAdmin(admin.ModelAdmin):
	list_display = ('id', 'descripcion')
	search_fields = ('descripcion',)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
	list_display = ('id', 'descripcion')
	search_fields = ('descripcion',)


@admin.register(TipoContrato)
class TipoContratoAdmin(admin.ModelAdmin):
	list_display = ('id', 'descripcion')
	search_fields = ('descripcion',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
	def full_name(self, obj):
		return f"{obj.first_name or ''} {obj.last_name or ''}".strip() or obj.nombre

	list_display = ('id', 'full_name', 'ci', 'email', 'turno', 'tipo_contrato', 'activo')
	list_filter = ('activo', 'turno', 'tipo_contrato', 'estado_civil', 'nacionalidad')
	search_fields = ('first_name', 'last_name', 'nombre', 'ci', 'email', 'celular', 'telefono_contacto')


@admin.register(Salario)
class SalarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'empleado', 'descripcion', 'monto', 'fecha_inicio')
	list_filter = ('fecha_inicio',)
	search_fields = ('empleado__nombre', 'descripcion')
