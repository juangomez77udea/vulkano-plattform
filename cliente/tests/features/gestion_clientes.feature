Feature: Gestión de Clientes
  Como usuario del sistema,
  quiero poder crear clientes de forma fiable
  para mantener un registro correcto de mis contactos comerciales.

  Scenario: Creación exitosa de un nuevo cliente
    Given un usuario administrador está autenticado y tiene una empresa asignada
    When el usuario navega a la página de creación de clientes
    And envía el formulario con datos válidos para un cliente
    Then el nuevo cliente debe ser creado en la base de datos
    And el usuario debe ser redirigido a la lista de clientes

  Scenario: Intento de crear un cliente con un documento duplicado
    Given un usuario administrador está autenticado y tiene una empresa asignada
    And ya existe un cliente con el documento "987654321"
    When el usuario navega a la página de creación de clientes
    And envía el formulario con datos de un nuevo cliente con documento "987654321"
    Then la página debe mostrar un mensaje de error de documento duplicado
    And el cliente con documento "987654321" debe existir solo una vez en la base de datos

  Scenario: Editar la información de un cliente existente
    Given un usuario administrador está autenticado y tiene una empresa asignada
    And ya existe un cliente llamado "Cliente Para Editar" con el documento "11223344"
    When el usuario navega a la página de edición del cliente con documento "11223344"
    And actualiza el nombre a "Cliente Editado Correctamente" y envía el formulario
    Then el cliente con el documento "11223344" debe tener el nombre "Cliente Editado Correctamente"

  Scenario: Ver un cliente específico en la lista de clientes
    Given un usuario administrador está autenticado y tiene una empresa asignada
    And ya existe un cliente llamado "Cliente Visible en Lista" con el documento "99887766"
    When el usuario navega a la lista de clientes
    Then la página debe mostrar el nombre "Cliente Visible en Lista"

  Scenario: Intentar eliminar un cliente con alquileres asociados
    Given un usuario administrador está autenticado y tiene una empresa asignada
    And ya existe un cliente con el documento "77775555"
    And el cliente con el documento "77775555" tiene un alquiler asociado
    When el usuario intenta eliminar el cliente con el documento "77775555"
    Then el sistema debe mostrar un mensaje de error de borrado protegido
    And el cliente con el documento "77775555" todavía debe existir en la base de datos