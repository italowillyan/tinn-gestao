from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from financeiro.services import (
    cancelar_venda,
    finalizar_venda,
)

from .models import ItemVenda, Venda


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Venda.STATUS_ABERTA:
            return (
                "variacao",
                "quantidade",
                "preco_unitario",
            )

        return ()


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "empresa",
        "cliente",
        "status",
        "forma_pagamento",
        "subtotal",
        "total",
        "usuario",
        "criada_em",
    )

    search_fields = (
        "cliente__nome",
        "observacao",
    )

    list_filter = (
        "empresa",
        "status",
        "forma_pagamento",
        "criada_em",
    )

    readonly_fields = (
        "status",
        "criada_em",
        "atualizada_em",
    )

    inlines = [ItemVendaInline]

    actions = (
        "finalizar_vendas",
        "cancelar_vendas",
    )

    @admin.action(description="Finalizar vendas selecionadas")
    def finalizar_vendas(self, request, queryset):
        finalizadas = 0

        for venda in queryset:
            try:
                finalizar_venda(venda)
                finalizadas += 1

            except ValidationError as erro:
                self.message_user(
                    request,
                    f"Venda #{venda.pk}: {' '.join(erro.messages)}",
                    level=messages.ERROR,
                )

        if finalizadas:
            self.message_user(
                request,
                f"{finalizadas} venda(s) finalizada(s) com sucesso.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Cancelar vendas selecionadas")
    def cancelar_vendas(self, request, queryset):
        canceladas = 0

        for venda in queryset:
            try:
                cancelar_venda(venda)
                canceladas += 1

            except ValidationError as erro:
                self.message_user(
                    request,
                    f"Venda #{venda.pk}: {' '.join(erro.messages)}",
                    level=messages.ERROR,
                )

        if canceladas:
            self.message_user(
                request,
                f"{canceladas} venda(s) cancelada(s) com sucesso.",
                level=messages.SUCCESS,
            )

    def has_delete_permission(self, request, obj=None):
        return False