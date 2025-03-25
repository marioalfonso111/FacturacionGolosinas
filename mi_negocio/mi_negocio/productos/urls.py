from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.lista_productos, name='lista_productos'),
    path('facturar/', views.registrar_venta, name='registrar_venta'),
    path('factura/<int:venta_id>/', views.generar_factura, name='generar_factura'),
    path('mostrar_factura/<int:venta_id>/', views.mostrar_factura, name='mostrar_factura'),
    path('reporte_ventas/', views.reporte_ventas, name='reporte_ventas'),
]