# Developed By Tecktrio At Liquidlab Infosystems
# Project: Wsgi config
# Version: 1.0
# Date: 2025-03-08
# Description: wsgi config

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpgsserver.settings')
application = get_wsgi_application()
