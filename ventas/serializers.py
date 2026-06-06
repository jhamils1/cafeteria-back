from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from productos.models import MovimientoInventario, Producto
from productos.models import Producto
from .models import Cliente, DetalleVenta, NotaVenta


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class NotaVentaSerializer(serializers.ModelSerializer):
    detalles = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = NotaVenta
        fields = '__all__'

    def validate(self, attrs):
        detalles = attrs.get('detalles')
        if detalles is not None and not detalles:
            raise serializers.ValidationError({'detalles': 'Debes incluir al menos un detalle.'})
        return attrs

    def _calcular_subtotal(self, precio_unitario, cantidad, descuento):
        return (Decimal(str(precio_unitario)) * Decimal(str(cantidad))) - Decimal(str(descuento))

    def _resolver_descuento(self, detalle_data, precio_unitario, cantidad):
        porcentaje_raw = detalle_data.get('descuento_porcentaje')
        descuento_raw = detalle_data.get('descuento')

        if porcentaje_raw not in (None, ''):
            porcentaje = Decimal(str(porcentaje_raw))
            if porcentaje < 0 or porcentaje > 100:
                raise serializers.ValidationError({'descuento_porcentaje': 'Debe estar entre 0 y 100.'})
            descuento = (precio_unitario * Decimal(str(cantidad)) * porcentaje) / Decimal('100')
        else:
            descuento = Decimal(str(descuento_raw if descuento_raw not in (None, '') else '0'))

        if descuento < 0:
            raise serializers.ValidationError({'descuento': 'El descuento no puede ser negativo.'})

        subtotal_bruto = precio_unitario * Decimal(str(cantidad))
        if descuento > subtotal_bruto:
            raise serializers.ValidationError({'descuento': 'El descuento no puede ser mayor al subtotal bruto.'})

        return descuento

    def _registrar_movimiento(self, *, producto, tipo, cantidad, stock_anterior, stock_nuevo, usuario, descripcion):
        MovimientoInventario.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            usuario=usuario,
            descripcion=descripcion,
        )

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        nota_venta = NotaVenta.objects.create(**validated_data)
        total = Decimal('0')

        for detalle_data in detalles_data:
            producto = Producto.objects.select_for_update().get(pk=detalle_data['producto'])
            cantidad = int(detalle_data['cantidad'])
            precio_unitario = Decimal(str(producto.precio_venta))
            descuento = self._resolver_descuento(detalle_data, precio_unitario, cantidad)

            if not producto.estado:
                raise serializers.ValidationError({'producto': f'El producto {producto.nombre} está inactivo.'})
            if cantidad <= 0:
                raise serializers.ValidationError({'cantidad': 'La cantidad debe ser mayor que cero.'})
            if producto.stock < cantidad:
                raise serializers.ValidationError({
                    'stock': f'No hay stock suficiente para {producto.nombre}. Disponible: {producto.stock}.'
                })

            subtotal = self._calcular_subtotal(precio_unitario, cantidad, descuento)
            stock_anterior = producto.stock
            stock_nuevo = producto.stock - cantidad
            DetalleVenta.objects.create(
                nota_venta=nota_venta,
                producto=producto,
                cantidad=cantidad,
                descuento=descuento,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
            producto.stock = stock_nuevo
            producto.save(update_fields=['stock'])
            self._registrar_movimiento(
                producto=producto,
                tipo=MovimientoInventario.TIPO_SALIDA,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=request.user if request and request.user.is_authenticated else None,
                descripcion=f'Salida por nota de venta #{nota_venta.id}',
            )
            total += subtotal

        nota_venta.total = total
        nota_venta.save(update_fields=['total'])
        return nota_venta

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is None:
            instance.total = sum((detalle.subtotal for detalle in instance.detalles.all()), Decimal('0'))
            instance.save(update_fields=['total'])
            return instance

        for detalle in instance.detalles.select_related('producto').all():
            stock_anterior = detalle.producto.stock
            stock_nuevo = detalle.producto.stock + detalle.cantidad
            detalle.producto.stock = stock_nuevo
            detalle.producto.save(update_fields=['stock'])
            self._registrar_movimiento(
                producto=detalle.producto,
                tipo=MovimientoInventario.TIPO_ENTRADA,
                cantidad=detalle.cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=self.context.get('request').user if self.context.get('request') and self.context.get('request').user.is_authenticated else None,
                descripcion=f'Reverso por actualización de nota de venta #{instance.id}',
            )
            detalle.delete()

        total = Decimal('0')
        for detalle_data in detalles_data:
            producto = Producto.objects.select_for_update().get(pk=detalle_data['producto'])
            cantidad = int(detalle_data['cantidad'])
            precio_unitario = Decimal(str(producto.precio_venta))
            descuento = self._resolver_descuento(detalle_data, precio_unitario, cantidad)

            if not producto.estado:
                raise serializers.ValidationError({'producto': f'El producto {producto.nombre} está inactivo.'})
            if cantidad <= 0:
                raise serializers.ValidationError({'cantidad': 'La cantidad debe ser mayor que cero.'})
            if producto.stock < cantidad:
                raise serializers.ValidationError({
                    'stock': f'No hay stock suficiente para {producto.nombre}. Disponible: {producto.stock}.'
                })

            subtotal = self._calcular_subtotal(precio_unitario, cantidad, descuento)
            stock_anterior = producto.stock
            stock_nuevo = producto.stock - cantidad
            DetalleVenta.objects.create(
                nota_venta=instance,
                producto=producto,
                cantidad=cantidad,
                descuento=descuento,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
            producto.stock = stock_nuevo
            producto.save(update_fields=['stock'])
            self._registrar_movimiento(
                producto=producto,
                tipo=MovimientoInventario.TIPO_SALIDA,
                cantidad=cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=self.context.get('request').user if self.context.get('request') and self.context.get('request').user.is_authenticated else None,
                descripcion=f'Salida por actualización de nota de venta #{instance.id}',
            )
            total += subtotal

        instance.total = total
        instance.save(update_fields=['total'])
        return instance


class DetalleVentaSerializer(serializers.ModelSerializer):
    descuento_porcentaje = serializers.DecimalField(max_digits=5, decimal_places=2, write_only=True, required=False)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleVenta
        fields = '__all__'


class ReporteVentasSerializer(serializers.Serializer):
    """Serializer para reportes de ventas (no es ModelSerializer)"""
    total_ventas = serializers.DecimalField(max_digits=15, decimal_places=2)
    cantidad_notas = serializers.IntegerField()
    ventas_por_dia = serializers.ListField(child=serializers.DictField())
    producto_mas_vendido = serializers.DictField()
    top_clientes = serializers.ListField(child=serializers.DictField())
    top_empleados = serializers.ListField(child=serializers.DictField())

    def validate(self, attrs):
        producto = attrs.get('producto')
        cantidad = attrs.get('cantidad')
        if producto and not producto.estado:
            raise serializers.ValidationError({'producto': 'El producto seleccionado está inactivo.'})
        if cantidad is not None and cantidad <= 0:
            raise serializers.ValidationError({'cantidad': 'La cantidad debe ser mayor que cero.'})
        return attrs

    def _calcular_subtotal(self, precio_unitario, cantidad, descuento):
        return (Decimal(str(precio_unitario)) * Decimal(str(cantidad))) - Decimal(str(descuento))

    def _resolver_descuento(self, *, precio_unitario, cantidad, descuento, descuento_porcentaje):
        if descuento_porcentaje not in (None, ''):
            porcentaje = Decimal(str(descuento_porcentaje))
            if porcentaje < 0 or porcentaje > 100:
                raise serializers.ValidationError({'descuento_porcentaje': 'Debe estar entre 0 y 100.'})
            descuento_final = (Decimal(str(precio_unitario)) * Decimal(str(cantidad)) * porcentaje) / Decimal('100')
        else:
            descuento_final = Decimal(str(descuento if descuento not in (None, '') else '0'))

        if descuento_final < 0:
            raise serializers.ValidationError({'descuento': 'El descuento no puede ser negativo.'})

        subtotal_bruto = Decimal(str(precio_unitario)) * Decimal(str(cantidad))
        if descuento_final > subtotal_bruto:
            raise serializers.ValidationError({'descuento': 'El descuento no puede ser mayor al subtotal bruto.'})

        return descuento_final

    @transaction.atomic
    def create(self, validated_data):
        producto = Producto.objects.select_for_update().get(pk=validated_data['producto'].pk)
        cantidad = validated_data['cantidad']
        descuento_porcentaje = self.initial_data.get('descuento_porcentaje')
        if producto.stock < cantidad:
            raise serializers.ValidationError({
                'stock': f'No hay stock suficiente para {producto.nombre}. Disponible: {producto.stock}.'
            })

        descuento = self._resolver_descuento(
            precio_unitario=producto.precio_venta,
            cantidad=cantidad,
            descuento=validated_data.get('descuento', Decimal('0')),
            descuento_porcentaje=descuento_porcentaje,
        )
        validated_data['descuento'] = descuento
        validated_data['precio_unitario'] = producto.precio_venta

        subtotal = self._calcular_subtotal(
            producto.precio_venta,
            cantidad,
            descuento,
        )
        stock_anterior = producto.stock
        stock_nuevo = producto.stock - cantidad
        detalle = DetalleVenta.objects.create(subtotal=subtotal, **validated_data)
        producto.stock = stock_nuevo
        producto.save(update_fields=['stock'])
        request = self.context.get('request')
        MovimientoInventario.objects.create(
            producto=producto,
            tipo=MovimientoInventario.TIPO_SALIDA,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            usuario=request.user if request and request.user.is_authenticated else None,
            descripcion=f'Salida por detalle de venta #{detalle.nota_venta.id}',
        )

        nota_venta = detalle.nota_venta
        nota_venta.total = sum((item.subtotal for item in nota_venta.detalles.all()), Decimal('0'))
        nota_venta.save(update_fields=['total'])
        return detalle

    @transaction.atomic
    def update(self, instance, validated_data):
        producto_anterior = instance.producto
        cantidad_anterior = instance.cantidad
        descuento_porcentaje = self.initial_data.get('descuento_porcentaje')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        producto_nuevo = instance.producto
        cantidad_nueva = instance.cantidad

        if producto_nuevo.pk == producto_anterior.pk:
            diferencia = cantidad_nueva - cantidad_anterior
            if diferencia > 0 and producto_nuevo.stock < diferencia:
                raise serializers.ValidationError({
                    'stock': f'No hay stock suficiente para {producto_nuevo.nombre}. Disponible: {producto_nuevo.stock}.'
                })
            stock_anterior = producto_nuevo.stock
            producto_nuevo.stock -= diferencia
            stock_nuevo = producto_nuevo.stock
            producto_nuevo.save(update_fields=['stock'])
            if diferencia != 0:
                MovimientoInventario.objects.create(
                    producto=producto_nuevo,
                    tipo=MovimientoInventario.TIPO_AJUSTE,
                    cantidad=abs(diferencia),
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    usuario=self.context.get('request').user if self.context.get('request') and self.context.get('request').user.is_authenticated else None,
                    descripcion=f'Ajuste por edición de detalle de venta #{instance.nota_venta.id}',
                )
        else:
            stock_anterior = producto_anterior.stock
            producto_anterior.stock += cantidad_anterior
            stock_nuevo = producto_anterior.stock
            producto_anterior.save(update_fields=['stock'])
            MovimientoInventario.objects.create(
                producto=producto_anterior,
                tipo=MovimientoInventario.TIPO_ENTRADA,
                cantidad=cantidad_anterior,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=self.context.get('request').user if self.context.get('request') and self.context.get('request').user.is_authenticated else None,
                descripcion=f'Reverso por cambio de producto en detalle de venta #{instance.nota_venta.id}',
            )
            if producto_nuevo.stock < cantidad_nueva:
                raise serializers.ValidationError({
                    'stock': f'No hay stock suficiente para {producto_nuevo.nombre}. Disponible: {producto_nuevo.stock}.'
                })
            stock_anterior = producto_nuevo.stock
            producto_nuevo.stock -= cantidad_nueva
            stock_nuevo = producto_nuevo.stock
            producto_nuevo.save(update_fields=['stock'])
            MovimientoInventario.objects.create(
                producto=producto_nuevo,
                tipo=MovimientoInventario.TIPO_SALIDA,
                cantidad=cantidad_nueva,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                usuario=self.context.get('request').user if self.context.get('request') and self.context.get('request').user.is_authenticated else None,
                descripcion=f'Ajuste por cambio de producto en detalle de venta #{instance.nota_venta.id}',
            )

        instance.precio_unitario = instance.producto.precio_venta
        instance.descuento = self._resolver_descuento(
            precio_unitario=instance.precio_unitario,
            cantidad=instance.cantidad,
            descuento=instance.descuento,
            descuento_porcentaje=descuento_porcentaje,
        )

        instance.subtotal = self._calcular_subtotal(
            instance.precio_unitario,
            instance.cantidad,
            instance.descuento,
        )
        instance.save()

        nota_venta = instance.nota_venta
        nota_venta.total = sum((item.subtotal for item in nota_venta.detalles.all()), Decimal('0'))
        nota_venta.save(update_fields=['total'])
        return instance