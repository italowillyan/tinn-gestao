from decimal import Decimal

from django.db.models import Sum

from .models import LancamentoFinanceiro


def resumo_financeiro(empresa):
    lancamentos = LancamentoFinanceiro.objects.filter(
        empresa=empresa
    ).exclude(
        status=LancamentoFinanceiro.STATUS_CANCELADO
    )

    receitas_recebidas = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_PAGO,
        ).aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    despesas_pagas = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_PAGO,
        ).aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    contas_receber = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_PENDENTE,
        ).aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    contas_pagar = (
        lancamentos.filter(
            tipo=LancamentoFinanceiro.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_PENDENTE,
        ).aggregate(total=Sum("valor"))["total"]
        or Decimal("0.00")
    )

    saldo_realizado = receitas_recebidas - despesas_pagas

    return {
        "receitas_recebidas": receitas_recebidas,
        "despesas_pagas": despesas_pagas,
        "saldo_realizado": saldo_realizado,
        "contas_receber": contas_receber,
        "contas_pagar": contas_pagar,
    }