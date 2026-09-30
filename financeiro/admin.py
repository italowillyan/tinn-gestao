from django.contrib import admin, messages
from django.utils import timezone

from .models import LancamentoFinanceiro


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "empresa",
        "tipo",
        "valor",
        "status",
        "data_vencimento",
        "data_pagamento",
    )

    search_fields = (
        "descricao",
        "observacao",
    )

    list_filter = (
        "empresa",
        "tipo",
        "status",
        "data_vencimento",
    )

    readonly_fields = (
        "venda",
        "compra",
        "criado_em",
        "atualizado_em",
    )

    actions = (
        "marcar_como_pago",
        "marcar_como_pendente",
    )

    @admin.action(description="Marcar selecionados como pagos/recebidos")
    def marcar_como_pago(self, request, queryset):
        atualizados = 0

        for lancamento in queryset:
            if lancamento.status == LancamentoFinanceiro.STATUS_CANCELADO:
                self.message_user(
                    request,
                    f"{lancamento}: lançamento cancelado não pode ser liquidado.",
                    level=messages.ERROR,
                )
                continue

            lancamento.status = LancamentoFinanceiro.STATUS_PAGO
            lancamento.data_pagamento = timezone.localdate()
            lancamento.save()

            atualizados += 1

        if atualizados:
            self.message_user(
                request,
                f"{atualizados} lançamento(s) marcado(s) como pago/recebido.",
                level=messages.SUCCESS,
            )

    @admin.action(description="Marcar selecionados como pendentes")
    def marcar_como_pendente(self, request, queryset):
        atualizados = 0

        for lancamento in queryset:
            if lancamento.status == LancamentoFinanceiro.STATUS_CANCELADO:
                self.message_user(
                    request,
                    f"{lancamento}: lançamento cancelado não pode voltar para pendente.",
                    level=messages.ERROR,
                )
                continue

            lancamento.status = LancamentoFinanceiro.STATUS_PENDENTE
            lancamento.data_pagamento = None
            lancamento.save()

            atualizados += 1

        if atualizados:
            self.message_user(
                request,
                f"{atualizados} lançamento(s) marcado(s) como pendente.",
                level=messages.SUCCESS,
            )

    def has_delete_permission(self, request, obj=None):
        return False