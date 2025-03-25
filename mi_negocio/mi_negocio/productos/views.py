# Create your views here.
from django.http import HttpResponse
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.units import mm
from django.db.models import Sum
from datetime import datetime
from .models import Venta, DetalleVenta, Producto

def lista_productos(request):
    productos = Producto.objects.all()  # Obtiene todos los productos de la base de datos
    return render(request, 'productos/lista.html', {'productos': productos})

def registrar_venta(request):
    
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        venta = Venta.objects.create()  # Crea una nueva venta
        productos = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')
        precios = request.POST.getlist('precio[]')

        for producto_nombre, cantidad, precio in zip(productos, cantidades, precios):
            producto = Producto.objects.get(articulo=producto_nombre)
            subtotal = float(precio) * int(cantidad)

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=int(cantidad),
                subtotal=subtotal
            )

        return redirect('mostrar_factura', venta_id=venta.id)

        productos = Producto.objects.all()
    return render(request, 'productos/facturar.html', {'productos': productos})

def generar_factura(request, venta_id):
    # Obtén la venta desde la base de datos
    venta = get_object_or_404(Venta, id=venta_id)

    # Configura la respuesta como un archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_golosinas.pdf"'

    # Crear el documento PDF
    pdf = SimpleDocTemplate(
        response,
        pagesize=A5,
        rightMargin=20, leftMargin=20, topMargin=40, bottomMargin=20
    )

    elements = []

    # Título centrado
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    estilo_titulo = ParagraphStyle('titulo', fontSize=16, alignment=1, fontName="Helvetica-Bold")
    titulo = Paragraph("Golosinas", estilo_titulo)
    elements.append(titulo)
    
    elements.append(Spacer(1, 5 * mm))  # Espaciador

    # Teléfono centrado
    estilo_telefono = ParagraphStyle('telefono', fontSize=12, alignment=1, fontName="Helvetica")
    telefono = Paragraph("Teléfono: 094471243", estilo_telefono)
    elements.append(telefono)

    elements.append(Spacer(1, 10 * mm))  # Espaciador

    # Crear la tabla de productos
    estilo_articulo = ParagraphStyle(name="Articulo", fontSize=10, alignment=0)  # Estilo para envolver texto
    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]
    for detalle in venta.detalles.all():
        data.append([
            Paragraph(detalle.producto.articulo, estilo_articulo),  # Envuelve el texto largo
            detalle.cantidad,
            f"${detalle.producto.venta:.2f}",
            f"${detalle.subtotal:.2f}"
        ])

    # Añadir estilo a la tabla
    tabla = Table(data, colWidths=[140, 60, 80, 80])  # Ancho de columnas
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Encabezado en gris
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    tabla.setStyle(estilo_tabla)

    elements.append(tabla)
    
    elements.append(Spacer(1, 20))
    total_general = f"<b>Total: ${venta.total_venta():.2f}</b>"
    elements.append(Paragraph(total_general, ParagraphStyle(name='Total', fontSize=12, alignment=1)))

    # Construir PDF
    pdf.build(elements)
    return response


def reporte_ventas(request):
    # Inicializar filtro de fecha
    fecha = request.GET.get('fecha')
    
    # Filtrar ventas por fecha, si se selecciona una
    if fecha:
        fecha_inicio = datetime.strptime(fecha, "%Y-%m-%d")
        ventas = Venta.objects.filter(fecha__date=fecha_inicio)
    else:
        ventas = Venta.objects.all()

    # Calcular totales
    total_ingresos = ventas.aggregate(Sum('detalles__subtotal'))['detalles__subtotal__sum'] or 0
    total_ganancia = sum(
        sum(detalle.subtotal - (detalle.cantidad * detalle.producto.costo) for detalle in venta.detalles.all())
        for venta in ventas
    )

    # Enviar datos al template
    return render(request, 'productos/reporte_ventas.html', {
        'ventas': ventas,
        'total_ingresos': total_ingresos,
        'total_ganancia': total_ganancia,
        'fecha': fecha
    })

def mostrar_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'productos/mostrar_factura.html', {'venta': venta})

def facturar(request):
    productos = Producto.objects.all()
    return render(request, 'productos/facturar.html', {'productos': productos})
