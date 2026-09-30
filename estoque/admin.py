from django.contrib import admin

from .models import MovimentacaoEstoque


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "variacao",
        "empresa",
        "tipo",
        "motivo",
        "quantidade",
        "usuario",
        "criada_em",
    )

    search_fields = (
        "variacao__produto__nome",
        "variacao__sku",
        "observacao",
    )

    list_filter = (
        "empresa",
        "tipo",
        "motivo",
        "criada_em",
    )

    readonly_fields = ("criada_em",)

    def has_delete_permission(self, request, obj=None):
        return False