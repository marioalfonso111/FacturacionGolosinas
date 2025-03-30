from django.db import models

class Producto(models.Model):
    articulo = models.CharField(max_length=100)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    venta = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.articulo
    
class Reporte(models.Model):
    periodo = models.CharField(max_length=50)  # 'dia', 'semana', 'mes'
    ganancia = models.DecimalField(max_digits=10, decimal_places=2)

class Transaccion(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class DetalleTransaccion(models.Model):
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Cambiado a ForeignKey
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)


