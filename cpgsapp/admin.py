# Developed By Tecktrio At Liquidlab Infosystems
# Project: admin.py
# Version: 1.0
# Date: 2025-03-08
# Description: Manage admin controls in inbuild panel


from django.contrib import admin
from cpgsapp.models import Account, NetworkSettings

# Register your models here.
admin.site.register(NetworkSettings)
admin.site.register(Account)