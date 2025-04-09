# Developed By Tecktrio At Liquidlab Infosystems
# Project: Models
# Version: 1.0
# Date: 2025-03-08
# Description: Database models fields or schema

from django.db import models

class NetworkSettings(models.Model):
    ipv4_address = models.GenericIPAddressField(default='192.168.0.254')
    gateway_address = models.GenericIPAddressField(default='192.168.0.1')
    subnet_mask = models.GenericIPAddressField(default='255.255.255.0')

    ap_ssid = models.CharField(max_length=100, default='admin')
    ap_password = models.CharField(max_length=100, default='admin@1234')

    default_ap_ssid = models.CharField(max_length=100, default='LiquidlabCPGSDefaultSSID')
    default_ap_password = models.CharField(max_length=100, default='LiquidlabCPGS')

    server_ip = models.GenericIPAddressField(default='192.168.1.100')
    server_port = models.PositiveIntegerField(default=9090)

    host_name = models.CharField(max_length=50, default='cpgs')

    ip_type = models.CharField(
        max_length=10,
        choices=[('static', 'Static'), ('dynamic', 'Dynamic')],
        default='static'
    )

    def __str__(self):
        return f"Network Settings ({self.host_name})"


class Account(models.Model):
    username = models.CharField(max_length=100,default="admin")
    password = models.CharField(max_length=100,default="admin")
    deviceID = models.CharField(max_length=100,default="000")

    def __str__(self):
        return f"Network Settings ({self.username})"




class SpaceInfo(models.Model):
    spaceID = models.TextField()
    spaceStatus = models.TextField()
    previousSpaceStatus = models.TextField()
    licensePlate = models.TextField()
    spaceFrame = models.TextField(default = "", null=True, blank=True)
    topleft = models.TextField(default=0)
    topright = models.TextField(default=0)
    downleft = models.TextField(default=0)
    downright = models.TextField(default=0)

    def __str__(self):
        return f"Network Settings ({self.spaceID})"
