import random
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from empleados.models import Empleado, EstadoCivil, Nacionalidad, TipoContrato, Turno
from productos.models import CategoriaProducto, Producto
from usuarios.models import Bitacora
from ventas.models import Cliente, DetalleVenta, NotaVenta


class Command(BaseCommand):
    help = 'Pobla datos demo: 5 usuarios, 8 empleados y 10 ventas.'

    @transaction.atomic
    def handle(self, *args, **options):
        usuarios = self._crear_usuarios(5)
        self._crear_lookups_empleados()
        empleados = self._crear_empleados(8, usuarios)
        self._crear_salarios(empleados)
        productos = self._crear_productos_base()
        clientes = self._crear_clientes_base(10)
        self._crear_ventas(10, clientes, productos)
        self._crear_bitacoras(usuarios)

        self.stdout.write(self.style.SUCCESS('Datos demo generados correctamente.'))

    def _crear_usuarios(self, cantidad):
        usuarios = []
        for i in range(1, cantidad + 1):
            username = f'user_demo_{i}'
            email = f'user_demo_{i}@cafeteria.local'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Usuario{i}',
                    'last_name': 'Demo',
                    'is_active': True,
                    'is_staff': True,
                },
            )
            if created:
                user.set_password('Demo12345*')
                user.save(update_fields=['password'])
            usuarios.append(user)

        self.stdout.write(self.style.NOTICE(f'Usuarios demo listos: {len(usuarios)}'))
        return usuarios

    def _crear_lookups_empleados(self):
        for descripcion in ['Soltero', 'Casado', 'Divorciado']:
            EstadoCivil.objects.get_or_create(descripcion=descripcion)

        for descripcion in ['Boliviana', 'Peruana', 'Argentina']:
            Nacionalidad.objects.get_or_create(descripcion=descripcion)

        for descripcion in ['Manana', 'Tarde', 'Noche']:
            Turno.objects.get_or_create(descripcion=descripcion)

        for descripcion in ['Indefinido', 'Temporal', 'Medio tiempo']:
            TipoContrato.objects.get_or_create(descripcion=descripcion)

    def _crear_empleados(self, cantidad, usuarios):
        estados = list(EstadoCivil.objects.all())
        nacionalidades = list(Nacionalidad.objects.all())
        turnos = list(Turno.objects.all())
        contratos = list(TipoContrato.objects.all())

        creados = 0
        for i in range(1, cantidad + 1):
            ci = f'CI_DEMO_{i:04d}'
            defaults = {
                'nombre': f'Empleado Demo {i}',
                'telefono_fijo': f'4{i:06d}',
                'celular': f'7{i:07d}'[:8],
                'telefono_contacto': f'6{i:07d}'[:8],
                'email': f'empleado{i}@cafeteria.local',
                'direccion': f'Zona Centro #{i}',
                'nombre_contacto': f'Contacto {i}',
                'estado_civil': random.choice(estados),
                'nacionalidad': random.choice(nacionalidades),
                'turno': random.choice(turnos),
                'tipo_contrato': random.choice(contratos),
                'activo': True,
            }
            empleado, created = Empleado.objects.get_or_create(ci=ci, defaults=defaults)
            if created:
                creados += 1

            if i <= len(usuarios) and empleado.user_id is None:
                empleado.user = usuarios[i - 1]
                empleado.save(update_fields=['user'])

        self.stdout.write(self.style.NOTICE(f'Empleados nuevos creados: {creados}'))
        return list(Empleado.objects.filter(ci__startswith='CI_DEMO_').order_by('id')[:cantidad])

    def _crear_salarios(self, empleados):
        creados = 0

        for index, empleado in enumerate(empleados, start=1):
            descripcion = f'SEED_DEMO_SALARIO_{index:02d}'
            existe = empleado.salarios.filter(descripcion=descripcion).exists()
            if existe:
                continue

            empleado.salarios.create(
                descripcion=descripcion,
                monto=Decimal('2500.00') + (Decimal(index) * Decimal('150.00')),
                fecha_inicio='2026-01-01',
            )
            creados += 1

        self.stdout.write(self.style.NOTICE(f'Salarios nuevos creados: {creados}'))

    def _crear_productos_base(self):
        categorias = []
        for descripcion in ['Bebidas', 'Panaderia', 'Snacks']:
            categoria, _ = CategoriaProducto.objects.get_or_create(descripcion=descripcion)
            categorias.append(categoria)

        data_productos = [
            ('Cafe Americano', categorias[0], Decimal('10.00'), 120),
            ('Cafe Latte', categorias[0], Decimal('14.00'), 80),
            ('Capuccino', categorias[0], Decimal('16.00'), 70),
            ('Te Negro', categorias[0], Decimal('8.50'), 90),
            ('Croissant', categorias[1], Decimal('7.00'), 100),
            ('Muffin Vainilla', categorias[1], Decimal('9.00'), 75),
            ('Sandwich Mixto', categorias[2], Decimal('18.00'), 60),
            ('Galleta Avena', categorias[2], Decimal('5.00'), 150),
        ]

        productos = []
        for nombre, categoria, precio, stock in data_productos:
            producto, _ = Producto.objects.get_or_create(
                nombre=nombre,
                categoria=categoria,
                defaults={'precio_venta': precio, 'stock': stock, 'estado': True},
            )
            productos.append(producto)

        return productos

    def _crear_clientes_base(self, cantidad):
        clientes = []
        for i in range(1, cantidad + 1):
            ci_nit = f'NIT_DEMO_{i:04d}'
            cliente, _ = Cliente.objects.get_or_create(
                ci_nit=ci_nit,
                defaults={
                    'nombre': f'Cliente Demo {i}',
                    'celular': f'7{i:07d}'[:8],
                    'email': f'cliente{i}@correo.local',
                    'direccion': f'Avenida Demo #{i}',
                },
            )
            clientes.append(cliente)

        return clientes

    def _crear_ventas(self, cantidad, clientes, productos):
        creadas = 0

        for i in range(1, cantidad + 1):
            observacion = f'SEED_DEMO_VENTA_{i:02d}'
            nota = NotaVenta.objects.filter(observacion=observacion).first()
            if nota is None:
                nota = NotaVenta.objects.create(
                    cliente=random.choice(clientes),
                    observacion=observacion,
                    total=Decimal('0.00'),
                )
                creada_nota = True
            else:
                creada_nota = False

            if nota.detalles.exists():
                continue

            detalle_count = random.randint(1, 3)
            seleccion = random.sample(productos, k=detalle_count)
            total = Decimal('0.00')

            for producto in seleccion:
                cantidad_item = random.randint(1, 4)
                descuento = Decimal(random.choice(['0.00', '0.50', '1.00', '1.50']))
                precio = producto.precio_venta
                subtotal = (precio * cantidad_item) - descuento

                DetalleVenta.objects.create(
                    nota_venta=nota,
                    producto=producto,
                    cantidad=cantidad_item,
                    descuento=descuento,
                    precio_unitario=precio,
                    subtotal=subtotal,
                )
                total += subtotal

            nota.total = total
            nota.save(update_fields=['total'])

            if creada_nota:
                creadas += 1

        self.stdout.write(self.style.NOTICE(f'Notas de venta nuevas creadas: {creadas}'))

    def _crear_bitacoras(self, usuarios):
        creadas = 0

        for index, usuario in enumerate(usuarios, start=1):
            detalle = f'SEED_DEMO_BITACORA_{index:02d}'
            existe = Bitacora.objects.filter(usuario=usuario, detalle=detalle).exists()
            if existe:
                continue

            Bitacora.objects.create(
                usuario=usuario,
                accion='DATOS_DEMO',
                detalle=detalle,
            )
            creadas += 1

        self.stdout.write(self.style.NOTICE(f'Bitacoras nuevas creadas: {creadas}'))
