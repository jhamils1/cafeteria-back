from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
	NotaVenta = apps.get_model('ventas', 'NotaVenta')
	Empleado = apps.get_model('empleados', 'Empleado')
	fallback_empleado = Empleado.objects.filter(user__isnull=True, activo=True).order_by('id').first()

	for nota in NotaVenta.objects.all().select_related('usuario'):
		empleado = getattr(nota.usuario, 'empleado', None)
		if empleado is None:
			empleado = fallback_empleado
		if empleado is None:
			raise RuntimeError(
				f'No se pudo determinar un empleado para la nota de venta {nota.id}. '
				'Necesitas crear al menos un empleado disponible para completar la migración.'
			)
		nota.empleado_id = empleado.id
		nota.save(update_fields=['empleado'])


class Migration(migrations.Migration):

	dependencies = [
		('ventas', '0002_alter_cliente_id_alter_detalleventa_id_and_more'),
		('empleados', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='notaventa',
			name='empleado',
			field=models.ForeignKey(
				to='empleados.empleado',
				on_delete=django.db.models.deletion.PROTECT,
				related_name='notas_venta',
				null=True,
				blank=True,
			),
		),
		migrations.RunPython(forwards, migrations.RunPython.noop),
		migrations.AlterField(
			model_name='notaventa',
			name='empleado',
			field=models.ForeignKey(
				to='empleados.empleado',
				on_delete=django.db.models.deletion.PROTECT,
				related_name='notas_venta',
			),
		),
	]