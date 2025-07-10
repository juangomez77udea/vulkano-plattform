from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from .models import Producto, PrecioProducto
from producto.forms.forms_producto import ProductoForm
from core.views import BreadcrumbMixin
from django.db.models import Q

@login_required
def eliminar_producto(request, id):
    # Asegurarse de que el producto pertenece a la empresa del usuario
    producto = Producto.objects.get(id=id, empresa=request.user.empresa)
    producto.delete()
    return redirect('producto_list')

class ProductoCreateView(LoginRequiredMixin, BreadcrumbMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_crear.html'
    success_url = reverse_lazy('producto_list')

    breadcrumb_items = [
        ("Productos", reverse_lazy("producto_list")),
        ("Crear", None)
    ]

    def form_valid(self, form):
        # 1. Obtiene el objeto producto SIN guardarlo en la BD
        producto = form.save(commit=False)
        
        # 2. Asigna los campos que no vienen del formulario
        producto.empresa = self.request.user.empresa
        producto.sucursal = self.request.user.sucursal
        
        usuario_nombre = self.request.user.get_full_name() or self.request.user.username
        producto.creado_por = usuario_nombre
        producto.modificado_por = usuario_nombre
        
        # 3. Guarda el objeto producto en la BD. A partir de aquí, producto.id ya existe.
        producto.save()
        
        # 4. Ahora que el producto está guardado, crea/actualiza su precio.
        valor_precio = form.cleaned_data.get('precio')
        if valor_precio is not None:
            PrecioProducto.objects.update_or_create(
                producto=producto,  # Ahora 'producto' es un objeto válido y guardado
                defaults={'valor': valor_precio}
            )
            
        # 5. Asigna el objeto guardado a self.object y deja que la vista padre redirija.
        self.object = producto
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductoListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    model = Producto
    template_name = 'producto_list.html'
    context_object_name = 'productos'
    ordering = ['nombre']
    paginate_by = 9

    breadcrumb_items = [
        ("Productos", None)
    ]

    def get_queryset(self):
        # Asegurarse de que el usuario tenga una empresa asignada
        if not self.request.user.empresa:
            return Producto.objects.none() # No mostrar nada si no hay empresa
            
        queryset = Producto.objects.filter(empresa=self.request.user.empresa)
        q = self.request.GET.get('q')
        
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(codigo_interno__icontains=q) |
                Q(ubicacion_actual__icontains=q)
            )
        return queryset

class ProductoUpdateView(LoginRequiredMixin, BreadcrumbMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_crear.html'
    success_url = reverse_lazy('producto_list')

    breadcrumb_items = [
        ("Productos", reverse_lazy("producto_list")),
        ("Editar", None)
    ]

    def form_valid(self, form):
        # La lógica para actualizar el precio también debe estar aquí.
        valor_precio = form.cleaned_data.get('precio')
        if valor_precio is not None:
            PrecioProducto.objects.update_or_create(
                producto=self.object,
                defaults={'valor': valor_precio}
            )

        form.instance.modificado_por = self.request.user.get_full_name() or self.request.user.username
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Editar Producto"
        context['boton_texto'] = "Actualizar Producto"
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductoDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    model = Producto
    template_name = 'producto_detalle.html'
    context_object_name = 'producto'

    breadcrumb_items = [
        ("Productos", reverse_lazy("producto_list")),
        ("Detalle", None)
    ]