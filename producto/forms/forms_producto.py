from django import forms
from producto.models import Producto, PrecioProducto, Categoria, Proveedor

class ProductoForm(forms.ModelForm):
    precio = forms.DecimalField(
        label='Precio por día', 
        max_digits=10, 
        decimal_places=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ej: 20000',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })
    )

    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'codigo_interno', 'estado', 'iva_porcentaje',
            'ubicacion_actual', 'modelo', 'marca', 'serial', 'imagen', 
            'categoria', 'proveedor'
        ]
        # NOTA: 'precio' no está aquí porque no es un campo del modelo Producto.
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-[var(--primary-color)]',
                'placeholder': 'Nombre del producto'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded bg-white'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded resize-y focus:ring-2 focus:ring-[var(--primary-color)]',
                'placeholder': 'Descripción del producto',
                'rows': 3
            }),
            'codigo_interno': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Código interno'
            }),
            'ubicacion_actual': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Ubicación actual'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Marca'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Modelo'
            }),
            'serial': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'placeholder': 'Serial'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-gray-300 p-2 rounded bg-white'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded bg-white'
            }),
            'proveedor': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded bg-white'
            }),
            'iva_porcentaje': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded',
                'min': 0,
                'step': 1,
                'placeholder': 'Ej. 19 para 19%',
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Llenar el campo 'precio' si estamos editando un producto existente
        if self.instance and self.instance.pk:
            try:
                precio_obj = PrecioProducto.objects.get(producto=self.instance)
                self.fields['precio'].initial = int(precio_obj.valor)
            except PrecioProducto.DoesNotExist:
                self.fields['precio'].initial = 0

        # Filtrar los querysets de Categoria y Proveedor por la empresa del usuario
        if user and hasattr(user, 'empresa') and user.empresa:
            self.fields['categoria'].queryset = Categoria.objects.filter(empresa=user.empresa)
            self.fields['proveedor'].queryset = Proveedor.objects.filter(empresa=user.empresa)

    # Eliminamos el método save() para usar el comportamiento por defecto de ModelForm.
    # La lógica de guardar el PrecioProducto se moverá a la vista.