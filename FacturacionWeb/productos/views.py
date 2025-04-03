import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.timezone import now, timedelta
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Producto, Transaccion, DetalleTransaccion

def home(request):
    return render(request, 'home.html')

def productos_list(request):
    query = request.GET.get('q', '')  # Obtén el término de búsqueda desde la URL
    if query:
        productos = Producto.objects.filter(articulo__icontains=query).order_by('articulo')
    else:
        productos = Producto.objects.all().order_by('articulo')
    return render(request, 'productos_list.html', {'productos': productos, 'query': query})

def facturar(request):
    productos = Producto.objects.all()
    return render(request, 'facturar.html', {'productos': productos})

@csrf_exempt
def guardar_transaccion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productos = data.get('productos', [])
            total = data.get('total', 0)

            # Crear la transacción
            transaccion = Transaccion.objects.create(total=total)

            # Guardar los detalles de la transacción
            for producto in productos:
                producto_obj = Producto.objects.get(articulo=producto['producto'])  # Buscar el objeto Producto
                DetalleTransaccion.objects.create(
                    transaccion=transaccion,
                    producto=producto_obj,  # Asignar el objeto Producto
                    precio=producto['precio'],
                    cantidad=producto['cantidad'],
                    subtotal=producto['subtotal']
                )

            return JsonResponse({'success': True, 'transaccion_id': transaccion.id})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def reporte(request):
    # Filtros de tiempo
    filtro = request.GET.get('filtro', 'todo')  # 'dia', 'semana', 'mes', 'todo'
    hoy = now().date()
    if filtro == 'dia':
        transacciones = Transaccion.objects.filter(fecha__date=hoy)
    elif filtro == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        transacciones = Transaccion.objects.filter(fecha__date__gte=inicio_semana)
    elif filtro == 'mes':
        transacciones = Transaccion.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month)
    else:
        transacciones = Transaccion.objects.all()

    # Calcular ganancia por transacción y por detalle
    transacciones_con_ganancia = []
    ganancia_total = 0
    for transaccion in transacciones:
        detalles = []
        ganancia_transaccion = 0
        for detalle in transaccion.detalles.all():
            ganancia_detalle = (detalle.precio - detalle.producto.costo) * detalle.cantidad
            ganancia_transaccion += ganancia_detalle
            detalles.append({
                'producto': detalle.producto,
                'precio': detalle.precio,
                'cantidad': detalle.cantidad,
                'subtotal': detalle.subtotal,
                'ganancia': ganancia_detalle,
            })
        ganancia_total += ganancia_transaccion
        transacciones_con_ganancia.append({
            'transaccion': transaccion,
            'ganancia': ganancia_transaccion,
            'detalles': detalles,
        })

    return render(request, 'reporte.html', {
        'transacciones': transacciones_con_ganancia,
        'ganancia_total': ganancia_total,
        'filtro': filtro
    })

def agregar_producto(request):
    if request.method == 'POST':
        try:
            articulo = request.POST.get('articulo')
            costo = request.POST.get('costo')
            venta = request.POST.get('venta')
            Producto.objects.create(
                articulo=articulo,
                costo=costo,
                venta=venta
            )
            messages.success(request, "¡Producto agregado con éxito!")
        except Exception as e:
            messages.error(request, f"Error al agregar el producto: {e}")
    return render(request, 'agregar_producto.html')

def editar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        messages.error(request, "Producto no encontrado")
        return HttpResponseRedirect(reverse('productos_list'))

    if request.method == 'POST':
        try:
            producto.articulo = request.POST.get('articulo')
            producto.costo = request.POST.get('costo')
            producto.venta = request.POST.get('venta')
            producto.save()
            messages.success(request, "Producto actualizado con éxito")
            return HttpResponseRedirect(reverse('productos_list'))
        except Exception as e:
            messages.error(request, f"Error al actualizar el producto: {e}")

    return render(request, 'editar_producto.html', {'producto': producto})

def eliminar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        producto.delete()
        messages.success(request, "Producto eliminado con éxito")
    except Producto.DoesNotExist:
        messages.error(request, "Producto no encontrado")
    except Exception as e:
        messages.error(request, f"Error al eliminar el producto: {e}")
    
    return HttpResponseRedirect(reverse('productos_list'))

def listado_productos(request):
    # Obtener el término de búsqueda desde la URL
    query = request.GET.get('q', '')

    # Filtrar productos si hay un término de búsqueda
    if query:
        productos = Producto.objects.filter(articulo__icontains=query)
    else:
        productos = Producto.objects.all()

    # Pasar los productos y el término de búsqueda al contexto
    return render(request, 'productos_list.html', {'productos': productos, 'query': query})

def cargar_productos_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo_excel = request.FILES['archivo_excel']
        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo_excel)

            # Validar que las columnas necesarias estén presentes
            columnas_requeridas = {'articulo', 'costo', 'venta'}
            if not columnas_requeridas.issubset(df.columns):
                messages.error(request, "El archivo Excel no tiene las columnas requeridas: articulo, costo, venta.")
                return redirect('productos_list')

            # Iterar sobre las filas del DataFrame y guardar en la base de datos
            for _, row in df.iterrows():
                Producto.objects.create(
                    articulo=row['articulo'],
                    costo=row['costo'],
                    venta=row['venta']
                )

            messages.success(request, "Productos cargados exitosamente desde el archivo Excel.")
        except Exception as e:
            messages.error(request, f"Error al cargar productos: {str(e)}")
    else:
        messages.error(request, "Por favor, sube un archivo Excel válido.")

    return redirect('productos_list')

def buscar_producto(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(articulo__icontains=query).values('id', 'articulo', 'venta')
        return JsonResponse(list(productos), safe=False)
    return JsonResponse([], safe=False)

def listar_ventas(request):
    transacciones = Transaccion.objects.all().order_by('-fecha')
    return render(request, 'listar_ventas.html', {'transacciones': transacciones})

@require_http_methods(["DELETE"])
def eliminar_transaccion(request, transaccion_id):
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)
        transaccion.delete()
        return JsonResponse({'success': True})
    except Transaccion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Transacción no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def generar_factura(request, transaccion_id):
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)
        detalles = transaccion.detalles.all()
        total = transaccion.total
        return render(request, 'factura.html', {'detalles': detalles, 'total': total})
    except Transaccion.DoesNotExist:
        messages.error(request, "Transacción no encontrada")
        return redirect('listar_ventas')

def generar_factura_pdf(request, transaccion_id):
    try:
        transaccion = Transaccion.objects.get(id=transaccion_id)
        detalles = transaccion.detalles.all()

        # Crear un buffer para el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        subtitle_style = styles['Normal']
        subtitle_style.fontSize = 14
        subtitle_style.leading = 16
        subtitle_style.alignment = 1  # Centrado

        # Título y subtítulo
        elements = []
        elements.append(Paragraph("Golosinas", title_style))
        elements.append(Paragraph("094471243", subtitle_style))  # Teléfono centrado
        elements.append(Paragraph("<br/><br/>", subtitle_style))  # Espaciado

        # Tabla de productos
        data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
        for detalle in detalles:
            data.append([
                detalle.producto.articulo,
                detalle.cantidad,
                f"${detalle.precio:.2f}",
                f"${detalle.subtotal:.2f}"
            ])

        # Estilo de la tabla
        table = Table(data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Paragraph("<br/><br/>", subtitle_style))  # Espaciado

        # Total estilizado
        total_data = [["Total:", f"${transaccion.total:.2f}"]]
        total_table = Table(total_data, colWidths=[1.5 * inch, 2 * inch])  # Ajustar el ancho de las columnas
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(total_table)

        # Generar el PDF
        doc.build(elements)
        buffer.seek(0)

        # Devolver el PDF como respuesta
        return FileResponse(buffer, as_attachment=True, filename="factura.pdf")
    except Transaccion.DoesNotExist:
        messages.error(request, "Transacción no encontrada")
        return redirect('listar_ventas')
