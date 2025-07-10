from django.db import models
from empresa.models import Empresa

class Cliente(models.Model):
    # Clave primaria explícita para evitar cualquier ambigüedad
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    # Campos que antes estaban en Persona
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('NIT', 'NIT'),
        ('CE', 'Cédula de extranjería'),
    ]
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES)
    documento = models.CharField(max_length=30)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    # Campos originales de Cliente
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('documento', 'empresa')

    def __str__(self):
        return f"{self.nombre} ({self.documento}) - {self.empresa.nombre}"