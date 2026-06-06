from rest_framework import serializers

from .models import Empleado, EstadoCivil, Nacionalidad, Salario, TipoContrato, Turno


class EstadoCivilSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCivil
        fields = '__all__'


class NacionalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nacionalidad
        fields = '__all__'


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = '__all__'


class TipoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoContrato
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    estado_civil_display = serializers.CharField(source='estado_civil.descripcion', read_only=True)
    nacionalidad_display = serializers.CharField(source='nacionalidad.descripcion', read_only=True)
    turno_display = serializers.CharField(source='turno.descripcion', read_only=True)
    tipo_contrato_display = serializers.CharField(source='tipo_contrato.descripcion', read_only=True)
    
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Empleado
        fields = (
            'id',
            'user',
            'first_name',
            'last_name',
            'nombre',
            'ci',
            'telefono_fijo',
            'celular',
            'telefono_contacto',
            'email',
            'direccion',
            'nombre_contacto',
            'estado_civil',
            'estado_civil_display',
            'nacionalidad',
            'nacionalidad_display',
            'turno',
            'turno_display',
            'tipo_contrato',
            'tipo_contrato_display',
            'fecha_registro',
            'activo',
        )

    def create(self, validated_data):
        # rellenar nombre legacy desde first_name + last_name si están presentes
        fn = validated_data.get('first_name') or ''
        ln = validated_data.get('last_name') or ''
        if fn or ln:
            validated_data['nombre'] = f"{fn} {ln}".strip()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        fn = validated_data.get('first_name')
        ln = validated_data.get('last_name')
        if fn is not None or ln is not None:
            first = fn if fn is not None else instance.first_name or ''
            last = ln if ln is not None else instance.last_name or ''
            instance.nombre = f"{first} {last}".strip()
        return super().update(instance, validated_data)


class SalarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salario
        fields = '__all__'