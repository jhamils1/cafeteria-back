from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0003_alter_empleado_estado_civil_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='first_name',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='empleado',
            name='last_name',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='nombre',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]