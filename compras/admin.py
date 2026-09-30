from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from financeiro.services import (
    cancelar_compra,
    finalizar_compra,
)

from .models import Compra, ItemCompra


class ItemCompraInline(admin.TabularInline):
    model = ItemCompra
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Compra.STATUS_ABERTA:
            return (
                "variacao",
                "quantidade",
                "custo_unitario",
            )

        return ()


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "empresa",
        "fornecedor",
        "status",
        "subtotal",
        "frete",
        "desconto",
        "total",
        "usuario",
        "criada_em",
    )

    search_fields = (
        "fornecedor__nome",
        "fornecedor__nome_fantasia",
        "observacao",
    )

    list_filter = (
        "empresa",
        "status",
        "criada_em",
    )

    readonly_fields = (
        "status",
        "criada_em",
        "atualizada_em",
    )

    inlines = [ItemCompraInline]

    actions = (
        "finalizar_compras",
        "cancelar_compras",
    )

    @admin.action(description="Finalizar compras selecionadas")
    def finalizar_compras(self, request, queryset):
        finalizadas = 0

        for compra in queryset:
            try:
                finalizar_compra(compra)
                finalizadas += 1

            except ValidationError as erro:
                self.message_user(
                    request,
                    f"Compra #{compra.pk}: {' '.join(erro.messages)}",
                    level=messages.ERROR,
                )

        if finalizadas:
            self.message_user(
                request,
                f"{finalizadas} compra(s) finalizada(s) com sucesso.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Cancelar compras selecionadas")
    def cancelar_compras(self, request, queryset):
        canceladas = 0

        for compra in queryset:
            try:
                cancelar_compra(compra)
                canceladas += 1

            except ValidationError as erro:
                self.message_user(
                    request,
                    f"Compra #{compra.pk}: {' '.join(erro.messages)}",
                    level=messages.ERROR,
                )

        if canceladas:
            self.message_user(
                request,
                f"{canceladas} compra(s) cancelada(s) com sucesso.",
                level=messages.SUCCESS,
            )

    def has_delete_permission(self, request, obj=None):
        return False