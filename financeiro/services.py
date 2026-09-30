from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone


from .models import LancamentoFinanceiro


@transaction.atomic
def finalizar_venda(venda):
    venda.finalizar()

    hoje = timezone.localdate()

    # Dinheiro, PIX e débito entram imediatamente no caixa.
    pagamento_imediato = venda.forma_pagamento in [
        venda.PAGAMENTO_DINHEIRO,
        venda.PAGAMENTO_PIX,
        venda.PAGAMENTO_DEBITO,
    ]

    status = (
        LancamentoFinanceiro.STATUS_PAGO
        if pagamento_imediato
        else LancamentoFinanceiro.STATUS_PENDENTE
    )

    data_pagamento = hoje if pagamento_imediato else None

    if LancamentoFinanceiro.objects.filter(venda=venda).exists():
        raise ValidationError(
            f"A venda #{venda.pk} já possui lançamento financeiro."
        )

    LancamentoFinanceiro.objects.create(
        empresa=venda.empresa,
        venda=venda,
        tipo=LancamentoFinanceiro.TIPO_RECEITA,
        descricao=f"Venda #{venda.pk}",
        valor=venda.total,
        status=status,
        data_vencimento=hoje,
        data_pagamento=data_pagamento,
        usuario=venda.usuario,
    )


@transaction.atomic
def cancelar_venda(venda):
    venda.cancelar()

    try:
        lancamento = venda.lancamento_financeiro
    except LancamentoFinanceiro.DoesNotExist:
        return

    lancamento.status = LancamentoFinanceiro.STATUS_CANCELADO
    lancamento.save()


@transaction.atomic
def finalizar_compra(compra):
    compra.finalizar()

    hoje = timezone.localdate()

    if LancamentoFinanceiro.objects.filter(compra=compra).exists():
        raise ValidationError(
            f"A compra #{compra.pk} já possui lançamento financeiro."
        )

    LancamentoFinanceiro.objects.create(
        empresa=compra.empresa,
        compra=compra,
        tipo=LancamentoFinanceiro.TIPO_DESPESA,
        descricao=f"Compra #{compra.pk} - {compra.fornecedor}",
        valor=compra.total,
        status=LancamentoFinanceiro.STATUS_PENDENTE,
        data_vencimento=hoje,
        usuario=compra.usuario,
    )


@transaction.atomic
def cancelar_compra(compra):
    compra.cancelar()

    try:
        lancamento = compra.lancamento_financeiro
    except LancamentoFinanceiro.DoesNotExist:
        return

    lancamento.status = LancamentoFinanceiro.STATUS_CANCELADO
    lancamento.save()


def resumo_financeiro(empresa):
    lancamentos = LancamentoFinanceiro.objects.filter(empresa=empresa).exclude(
        status=LancamentoFinanceiro.STATUS_CANCELADO
    )

    receitas_recebidas = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_PAGO,
        ).aggregate(total=Sum("valor"))["total"]
        or 0
    )

    despesas_pagas = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_PAGO,
        ).aggregate(total=Sum("valor"))["total"]
        or 0
    )

    a_receber = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_PENDENTE,
        ).aggregate(total=Sum("valor"))["total"]
        or 0
    )

    a_pagar = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_PENDENTE,
        ).aggregate(total=Sum("valor"))["total"]
        or 0
    )

    saldo_realizado = receitas_recebidas - despesas_pagas

    return {
        "receitas_recebidas": receitas_recebidas,
        "despesas_pagas": despesas_pagas,
        "a_receber": a_receber,
        "a_pagar": a_pagar,
        "saldo_realizado": saldo_realizado,
    }
