import pytest
from pytest_bdd import scenario, given, when, then, parsers
from django.urls import reverse
from faker import Faker
from empresa.models import Empresa, Sucursal
from autenticacion.models import Usuario
from cliente.models import Cliente
from alquiler.models import Alquiler
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

pytestmark = pytest.mark.django_db
fake = Faker('es_ES')

# --- ESCENARIOS ---
@scenario('features/gestion_clientes.feature', 'Creación exitosa de un nuevo cliente')
def test_creacion_exitosa_de_cliente():
    pass

@scenario('features/gestion_clientes.feature', 'Intento de crear un cliente con un documento duplicado')
def test_creacion_de_cliente_duplicado():
    pass

@scenario('features/gestion_clientes.feature', 'Editar la información de un cliente existente')
def test_editar_cliente_existente():
    pass

@scenario('features/gestion_clientes.feature', 'Ver un cliente específico en la lista de clientes')
def test_ver_cliente_en_la_lista():
    pass

@scenario('features/gestion_clientes.feature', 'Intentar eliminar un cliente con alquileres asociados')
def test_eliminar_cliente_protegido():
    pass

# --- FIXTURES ---

@pytest.fixture
def empresa():
    return Empresa.objects.create(nombre="Empresa BDD", nit="111.222.333-4")

@pytest.fixture
def sucursal(empresa):
    return Sucursal.objects.create(nombre="Sucursal BDD", empresa=empresa)

@pytest.fixture
def admin_user(db, empresa, sucursal):
    return Usuario.objects.create_user(
        username='admin_bdd', password='password123', is_staff=True,
        is_superuser=True, empresa=empresa, sucursal=sucursal
    )

# --- IMPLEMENTACIÓN DE PASOS ---

@given("un usuario administrador está autenticado y tiene una empresa asignada", target_fixture="admin_client")
def admin_client(client, admin_user):
    logging.info(f"GIVEN: Autenticando al usuario: {admin_user.username}")
    client.force_login(admin_user)
    return client

@given(parsers.parse('que el cliente con documento "{documento}" no existe'))
def no_existe_cliente(documento):
    existe = Cliente.objects.filter(documento=documento).exists()
    logging.info(f"GIVEN: Verificando que cliente con documento '{documento}' no existe. Existe: {existe}")
    assert not existe

@given(parsers.parse('ya existe un cliente con el documento "{documento}"'), target_fixture="cliente_existente")
def crear_cliente_preexistente(admin_user, documento):
    logging.info(f"GIVEN: Creando cliente preexistente con documento: {documento}")
    return Cliente.objects.create(nombre="Cliente", apellidos="Existente", documento=documento, empresa=admin_user.empresa)

@given(parsers.parse('ya existe un cliente llamado "{nombre}" con el documento "{documento}"'), target_fixture="cliente_a_editar")
def crear_cliente_para_editar(admin_user, nombre, documento):
    logging.info(f'GIVEN: Creando cliente preexistente llamado "{nombre}" con documento: {documento}')
    return Cliente.objects.create(nombre=nombre, apellidos="Apellidos Originales", documento=documento, empresa=admin_user.empresa)

@given(parsers.parse('el cliente con el documento "{documento}" tiene un alquiler asociado'))
def crear_alquiler_para_cliente(admin_user, cliente_existente):
    logging.info(f"GIVEN: Creando alquiler para el cliente con documento: {cliente_existente.documento}")
    Alquiler.objects.create(cliente=cliente_existente, usuario=admin_user)

@when("el usuario navega a la página de creación de clientes", target_fixture="response")
def navegar_a_crear_cliente(admin_client):
    url = reverse('cliente_create')
    logging.info(f"WHEN: Navegando a la URL: {url}")
    return admin_client.get(url)

@when("envía el formulario con datos válidos para un cliente", target_fixture="response")
def enviar_formulario_cliente(admin_client):
    url = reverse('cliente_create')
    data = {'nombre': 'Cliente', 'apellidos': 'Prueba BDD', 'tipo_documento': 'CC', 'documento': '12345678', 'correo': 'cliente.bdd@test.com', 'estado': 'on'}
    logging.info(f"WHEN: Enviando formulario para crear cliente con documento: {data['documento']}")
    return admin_client.post(url, data)

@when(parsers.parse('envía el formulario con datos de un nuevo cliente con documento "{documento}"'), target_fixture="response")
def enviar_formulario_cliente_duplicado(admin_client, documento):
    url = reverse('cliente_create')
    data = {'nombre': 'Cliente', 'apellidos': 'Duplicado', 'tipo_documento': 'CC', 'documento': documento, 'correo': 'duplicado.bdd@test.com', 'estado': 'on'}
    logging.info(f"WHEN: Enviando formulario con documento duplicado: {documento}")
    return admin_client.post(url, data)

@when(parsers.parse('el usuario navega a la página de edición del cliente con documento "{documento}"'))
def navegar_a_editar_cliente(admin_client, documento):
    cliente = Cliente.objects.get(documento=documento)
    url = reverse('cliente_edit', kwargs={'pk': cliente.pk})
    logging.info(f"WHEN: Navegando a la página de edición: {url}")
    admin_client.get(url)

@when(parsers.parse('actualiza el nombre a "{nuevo_nombre}" y envía el formulario'), target_fixture="response")
def enviar_formulario_de_edicion(admin_client, cliente_a_editar, nuevo_nombre):
    url = reverse('cliente_edit', kwargs={'pk': cliente_a_editar.pk})
    data = {'nombre': nuevo_nombre, 'apellidos': cliente_a_editar.apellidos, 'tipo_documento': 'CC', 'documento': cliente_a_editar.documento, 'correo': 'editado.bdd@test.com', 'estado': 'on'}
    logging.info(f"WHEN: Enviando formulario de edición para cliente ID {cliente_a_editar.pk} con nuevo nombre: {nuevo_nombre}")
    return admin_client.post(url, data)

@when("el usuario navega a la lista de clientes", target_fixture="response")
def navegar_a_lista_de_clientes(admin_client):
    url = reverse('cliente_list')
    logging.info(f"WHEN: Navegando a la lista de clientes: {url}")
    return admin_client.get(url)

@when(parsers.parse('el usuario intenta eliminar el cliente con el documento "{documento}"'), target_fixture="response")
def intentar_eliminar_cliente(admin_client, documento):
    cliente = Cliente.objects.get(documento=documento)
    url = reverse('cliente_delete', kwargs={'pk': cliente.pk})
    logging.info(f"WHEN: Intentando eliminar cliente con ID {cliente.pk} en URL: {url}")
    return admin_client.post(url, follow=True)

@then("el nuevo cliente debe ser creado en la base de datos")
def verificar_cliente_en_db():
    cliente_existe = Cliente.objects.filter(documento='12345678').exists()
    logging.info(f"THEN: Verificando creación en DB. Cliente existe: {cliente_existe}")
    assert cliente_existe

@then("el usuario debe ser redirigido a la lista de clientes")
def verificar_redireccion(response):
    es_redireccion = response.status_code == 302 and response.url == reverse('cliente_list')
    logging.info(f"THEN: Verificando redirección a lista de clientes. Es correcta: {es_redireccion}")
    assert es_redireccion

@then("la página debe mostrar un mensaje de error de documento duplicado")
def verificar_mensaje_de_error(response):
    messages = list(response.context['messages'])
    mensaje_encontrado = len(messages) == 1 and "Ya existe un cliente con ese documento" in str(messages[0])
    logging.info(f"THEN: Verificando mensaje de error por duplicado. Encontrado: {mensaje_encontrado}")
    assert response.status_code == 200
    assert mensaje_encontrado

@then(parsers.parse('el cliente con documento "{documento}" debe existir solo una vez en la base de datos'))
def verificar_conteo_unico_de_cliente(documento):
    count = Cliente.objects.filter(documento=documento).count()
    logging.info(f"THEN: Verificando que el conteo del cliente con documento '{documento}' es 1. Conteo actual: {count}")
    assert count == 1

@then(parsers.parse('el cliente con el documento "{documento}" debe tener el nombre "{nombre_esperado}"'))
def verificar_nombre_actualizado(documento, nombre_esperado):
    cliente_actualizado = Cliente.objects.get(documento=documento)
    nombre_es_correcto = cliente_actualizado.nombre == nombre_esperado
    logging.info(f"THEN: Verificando nombre actualizado para documento '{documento}'. Esperado: '{nombre_esperado}', Obtenido: '{cliente_actualizado.nombre}'. Correcto: {nombre_es_correcto}")
    assert nombre_es_correcto

@then(parsers.parse('la página debe mostrar el nombre "{nombre}"'))
def verificar_nombre_en_contenido_de_pagina(response, nombre):
    nombre_en_contenido = nombre.encode('utf-8') in response.content
    logging.info(f"THEN: Verificando si el nombre '{nombre}' está en la página. Encontrado: {nombre_en_contenido}")
    assert nombre_en_contenido

@then("el sistema debe mostrar un mensaje de error de borrado protegido")
def verificar_mensaje_error_proteccion(response):
    messages = list(response.context['messages'])
    mensaje_encontrado = len(messages) == 1 and "No se puede eliminar este cliente porque está asociado" in str(messages[0])
    logging.info(f"THEN: Verificando mensaje de error por borrado protegido. Encontrado: {mensaje_encontrado}")
    assert mensaje_encontrado

@then(parsers.parse('el cliente con el documento "{documento}" todavía debe existir en la base de datos'))
def verificar_que_cliente_no_se_borro(documento):
    cliente_existe = Cliente.objects.filter(documento=documento).exists()
    logging.info(f"THEN: Verificando que cliente con documento '{documento}' no fue borrado. Existe: {cliente_existe}")
    assert cliente_existe