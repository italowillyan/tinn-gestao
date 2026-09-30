from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "empresa",
        "telefone",
        "instagram",
        "ativo",
        "criado_em",
    )

    search_fields = (
        "nome",
        "telefone",
        "email",
        "instagram",
        "cpf",
    )

    list_filter = (
        "empresa",
        "ativo",
    )