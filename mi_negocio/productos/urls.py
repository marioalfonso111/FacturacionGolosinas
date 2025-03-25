from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),
    path('lista/', views.lista_productos, name='lista_productos'),
    path('facturar/', views.facturar, name='facturar'),
    path('factura/<int:venta_id>/', views.generar_factura, name='generar_factura'),
    path('mostrar_factura/<int:venta_id>/', views.mostrar_factura, name='mostrar_factura'),
    path('reporte_ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('reporte/', views.reporte_ventas, name='reporte_ventas'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),  # Ruta para agregar productos
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),  # Ruta para editar productos
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),  # Ruta para eliminar productos

]