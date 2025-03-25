# Register your models here.
from django.contrib import admin
from .models import Producto, Venta, DetalleVenta

# Configuración para el modelo Producto
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'articulo', 'costo', 'venta')  # Mostrar columnas relevantes
    search_fields = ('articulo',)  # Barra de búsqueda por el nombre del artículo
    ordering = ('articulo',)  # Ordenar por el nombre del artículo

# Configuración para el modelo Venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'total_venta', 'mostrar_ganancia_total')  # Mostrar el ID, fecha y el total de la venta
    date_hierarchy = 'fecha'  # Navegación por fechas en la parte superior
    ordering = ('-fecha',)  # Ordenar de las ventas más recientes a las más antiguas
    
    @admin.display(description='Ganancia Total')  # Añadir un título personalizado en el admin
    def mostrar_ganancia_total(self, obj):
        return obj.ganancia_total()

# Configuración para el modelo DetalleVenta
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'subtotal', 'ganancia')  # Mostrar detalles de cada venta
    list_filter = ('producto',)  # Filtros por producto
    search_fields = ('producto__articulo',)  # Barra de búsqueda por el nombre del producto