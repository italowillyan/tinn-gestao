from django.contrib import admin

from .models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "nome_fantasia",
        "empresa",
        "documento",
        "telefone",
        "ativo",
    )

    search_fields = (
        "nome",
        "nome_fantasia",
        "documento",
        "telefone",
        "email",
        "instagram",
    )

    list_filter = (
        "empresa",
        "ativo",
    )