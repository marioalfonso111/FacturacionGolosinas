"""
WSGI config for mi_negocio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('D:/GolosinasFact/mi_negocio')  # Ajusta la ruta según tu proyecto

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_negocio.settings')

application = get_wsgi_application()
