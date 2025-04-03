from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.productos_list, name='productos_list'),
    path('facturar/', views.facturar, name='facturar'),
    path('reporte/', views.reporte, name='reporte'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),  # Nueva ruta
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),  # Nueva ruta
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),  # Nueva ruta
    path('cargar-productos/', views.cargar_productos_excel, name='cargar_productos_excel'),
    path('guardar-transaccion/', views.guardar_transaccion, name='guardar_transaccion'),
    path('api/buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('ventas/', views.listar_ventas, name='listar_ventas'),  # Nueva ruta para listar ventas
    path('eliminar-transaccion/<int:transaccion_id>/', views.eliminar_transaccion, name='eliminar_transaccion'),  # Nueva ruta
    path('factura/<int:transaccion_id>/', views.generar_factura, name='generar_factura'),
    path('factura-pdf/<int:transaccion_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
]
