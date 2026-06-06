from django.contrib.auth.models import Group, Permission, User
from rest_framework import serializers

from .models import Bitacora, Estado


class UserSerializer(serializers.ModelSerializer):
    activo = serializers.SerializerMethodField(read_only=True)
    activo_write = serializers.BooleanField(
        write_only=True,
        required=False,
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        min_length=6,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    groups = serializers.SerializerMethodField(read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        write_only=True,
        required=False,
        source='groups',
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'activo',
            'activo_write',
            'password',
            'password_confirm',
            'groups',
            'group_ids',
        )

    def get_activo(self, obj):
        estado_relacion = getattr(obj, 'estado', None)
        if estado_relacion is None:
            return None
        return estado_relacion.activo

    def get_groups(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.groups.all()]

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # En creación: la contraseña es obligatoria y debe coincidir
        if not self.instance:
            if not password:
                raise serializers.ValidationError({'password': 'La contraseña es requerida.'})
            if not password_confirm:
                raise serializers.ValidationError({'password_confirm': 'Confirma la contraseña.'})

        # Si se proporciona contraseña (creación o edición), validar que coincida
        if password or password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError({
                    'password_confirm': 'Las contraseñas no coinciden.'
                })

        return data

    def _asignar_estado(self, user, activo):
        if activo is None:
            return

        relacion, _ = Estado.objects.get_or_create(usuario=user, defaults={'activo': activo})
        if relacion.activo != activo:
            relacion.activo = activo
            relacion.save(update_fields=['activo'])

    def create(self, validated_data):
        activo = validated_data.pop('activo_write', None)
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        user = super().create(validated_data)
        # Asignar contraseña hasheada si se proporcionó
        if password:
            user.set_password(password)
            user.save()
        self._asignar_estado(user, activo if activo is not None else True)
        return user

    def update(self, instance, validated_data):
        activo = validated_data.pop('activo_write', None)
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        user = super().update(instance, validated_data)
        
        # Cambiar contraseña si se proporciona
        if password:
            user.set_password(password)
            user.save()
        
        if activo is not None:
            self._asignar_estado(user, activo)
        return user


class CurrentUserSerializer(UserSerializer):
    roles = serializers.SerializerMethodField(read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('roles', 'permissions', 'is_staff')

    def get_roles(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.groups.all()]

    def get_permissions(self, obj):
        permissions = obj.get_all_permissions()
        return sorted(permissions)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source='permissions',
        required=False,
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'permission_ids')

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        if permissions_data:
            group.permissions.set(permissions_data)
        return group

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', None)
        instance = super().update(instance, validated_data)
        if permissions_data is not None:
            instance.permissions.set(permissions_data)
        return instance


class BitacoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bitacora
        fields = '__all__'