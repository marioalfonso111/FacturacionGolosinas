import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_negocio.settings')
django.setup()


import pandas as pd
from productos.models import Producto

def cargar_productos_desde_excel(ruta_archivo):
    # Lee el archivo Excel
    datos = pd.read_excel(ruta_archivo)

    # Itera sobre las filas y guarda los datos en la base de datos
    for _, fila in datos.iterrows():
        producto = Producto(
            articulo=fila['articulo'],
            costo=fila['costo'],
            venta=fila['venta']
        )
        producto.save()

    print("¡Productos cargados exitosamente!")
    
if __name__ == "__main__":
    cargar_productos_desde_excel("productos.xlsx")
