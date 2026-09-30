from django.contrib import admin

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "empresa", "cargo", "ativo")
    search_fields = ("usuario__username", "empresa__nome", "cargo")
    list_filter = ("empresa", "ativo")