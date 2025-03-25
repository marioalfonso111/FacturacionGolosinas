# Create your views here.
from django.http import HttpResponse
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from datetime import datetime
from .forms import ProductoForm
from .models import Venta, DetalleVenta, Producto

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/agregar_producto.html', {'form': form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar_producto.html', {'form': form})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'productos/eliminar_producto.html', {'producto': producto})

def pagina_principal(request):
    return render(request, 'productos/pagina_principal.html')

def lista_productos(request):
    query = request.GET.get('q')  # Obtiene el término de búsqueda de la URL
    if query:
        # Filtrar productos cuyo artículo contenga el término de búsqueda (case insensitive)
        productos = Producto.objects.filter(articulo__icontains=query)
    else:
        # Mostrar todos los productos si no hay búsqueda
        productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos, 'query': query})

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
    from django.utils.timezone import now, timedelta

def reporte_ventas(request):
    filtro = request.GET.get('filtro')  # Obtiene el filtro del parámetro de la URL
    hoy = now().date()

    if filtro == 'dia':
        # Ventas del día actual
        ventas = Venta.objects.filter(fecha__date=hoy)
    elif filtro == 'semana':
        # Ventas de los últimos 7 días
        semana_pasada = hoy - timedelta(days=7)
        ventas = Venta.objects.filter(fecha__date__range=[semana_pasada, hoy])
    elif filtro == 'mes':
        # Ventas del mes actual
        primer_dia_mes = hoy.replace(day=1)
        ventas = Venta.objects.filter(fecha__date__range=[primer_dia_mes, hoy])
    else:
        # Mostrar todas las ventas si no hay filtro
        ventas = Venta.objects.all()

    # Calcular ingresos y ganancias
    total_ingresos = ventas.aggregate(Sum('detalles__subtotal'))['detalles__subtotal__sum'] or 0
    total_ganancia = sum(
        sum(detalle.subtotal - (detalle.cantidad * detalle.producto.costo) for detalle in venta.detalles.all())
        for venta in ventas
    )

    return render(request, 'productos/reporte_ventas.html', {
        'ventas': ventas,
        'total_ingresos': total_ingresos,
        'total_ganancia': total_ganancia,
        'filtro': filtro
    })

def mostrar_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request, 'productos/mostrar_factura.html', {'venta': venta})

def facturar(request):
    productos = Producto.objects.all()
    return render(request, 'productos/facturar.html', {'productos': productos})

def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'detalle_venta.html', {'venta': venta})

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'lista_ventas.html', {'ventas': ventas})


