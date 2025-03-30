from django.core.management.base import BaseCommand
from productos.models import DetalleTransaccion, Producto

class Command(BaseCommand):
    help = 'Corrige los datos en productos_detalletransaccion para que coincidan con productos_producto'

    def handle(self, *args, **kwargs):
        detalles = DetalleTransaccion.objects.all()
        for detalle in detalles:
            try:
                # Buscar el producto por el nombre almacenado en el campo producto
                producto = Producto.objects.get(articulo=detalle.producto)
                detalle.producto = producto  # Asignar el objeto Producto al campo ForeignKey
                detalle.save()
                self.stdout.write(self.style.SUCCESS(f'Detalle actualizado: {detalle.id}'))
            except Producto.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Producto no encontrado para detalle: {detalle.id}'))
