# vulkano/core/management/commands/seed_db.py

import random
from django.core.management.base import BaseCommand
from faker import Faker
from empresa.models import Empresa, Sucursal
from cliente.models import Cliente
from producto.models import Categoria, Proveedor, Producto, PrecioProducto
from autenticacion.models import Usuario
from alquiler.models import Alquiler, AlquilerItem

fake = Faker('es_ES')

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando el proceso de creación de datos de prueba...'))

        self.stdout.write('Limpiando la base de datos...')
        AlquilerItem.objects.all().delete()
        Alquiler.objects.all().delete()
        PrecioProducto.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        Proveedor.objects.all().delete()
        Cliente.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        Sucursal.objects.all().delete()
        Empresa.objects.all().delete()

        self.stdout.write('Creando empresa y sucursal...')
        empresa, _ = Empresa.objects.get_or_create(
            nombre='Vulkano Alquileres',
            defaults={
                'nit': '900123456-7',
                'direccion': 'Calle Falsa 123, Medellín',
                'telefono': '6041234567'
                # La línea 'correo' ha sido eliminada
            }
        )
        sucursal, _ = Sucursal.objects.get_or_create(
            nombre='Sede Principal',
            empresa=empresa,
            defaults={'direccion': 'Carrera 45 # 67-89, Medellín'}
        )

        try:
            admin_user = Usuario.objects.filter(is_superuser=True).first()
            if admin_user:
                admin_user.empresa = empresa
                admin_user.sucursal = sucursal
                admin_user.save()
                self.stdout.write(f'Empresa y sucursal asignadas al superusuario "{admin_user.username}"')
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.WARNING('No se encontró un superusuario para asignarle empresa/sucursal.'))

        self.stdout.write('Creando categorías y proveedores...')
        categorias = []
        nombres_cat = ['Herramientas Eléctricas', 'Andamios', 'Maquinaria Pesada', 'Equipos de Medición']
        for nombre in nombres_cat:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre, empresa=empresa)
            categorias.append(cat)
            
        proveedores = []
        for _ in range(5):
            prov, _ = Proveedor.objects.get_or_create(
                nombre=fake.company(), 
                empresa=empresa,
                defaults={'nit': fake.ssn(), 'telefono': fake.phone_number()}
            )
            proveedores.append(prov)

        self.stdout.write('Creando 50 clientes...')
        for _ in range(50):
            Cliente.objects.create(
                nombre=fake.first_name(),
                apellidos=fake.last_name(),
                documento=fake.unique.ssn(),
                tipo_documento=random.choice(['CC', 'NIT', 'CE']),
                telefono=fake.phone_number(),
                correo=fake.email(),
                direccion=fake.address(),
                empresa=empresa,
                estado=True
            )

        self.stdout.write('Creando 100 productos con sus precios...')
        marcas = ['Bosch', 'DeWalt', 'Makita', 'Hilti', 'Toyota', 'CAT']
        for i in range(100):
            producto = Producto.objects.create(
                nombre=f'{random.choice(marcas)} Herramienta Genérica #{i+1}',
                descripcion=fake.text(max_nb_chars=150),
                codigo_interno=f'PROD-{i+1:04d}',
                empresa=empresa,
                sucursal=sucursal,
                categoria=random.choice(categorias),
                proveedor=random.choice(proveedores),
                creado_por='script',
                modificado_por='script'
            )
            PrecioProducto.objects.create(
                producto=producto,
                valor=random.randint(10000, 200000)
            )

        self.stdout.write(self.style.SUCCESS('¡Proceso completado! Base de datos poblada con éxito.'))