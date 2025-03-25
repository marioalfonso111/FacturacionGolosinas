from django.db import models # type: ignore

# Create your models here.

class Producto(models.Model):
    articulo = models.CharField(max_length=200)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    venta = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.articulo

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha y hora de la venta

    def total_venta(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())

    def ganancia_total(self):
        return sum(detalle.ganancia() for detalle in self.detalles.all())

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%Y-%m-%d')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calcular el subtotal automáticamente
        self.subtotal = self.cantidad * self.producto.venta
        super().save(*args, **kwargs)
        
    def ganancia(self):
        return (self.producto.venta - self.producto.costo) * self.cantidad

    def __str__(self):
        return f"{self.producto.articulo} x {self.cantidad}"
