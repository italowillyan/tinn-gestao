from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "nome_fantasia", "documento", "ativa", "criada_em")
    search_fields = ("nome", "nome_fantasia", "documento")
    list_filter = ("ativa",)