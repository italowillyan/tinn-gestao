from decimal import Decimal

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.utils import timezone

from financeiro.resumos import resumo_financeiro
from produtos.models import VariacaoProduto
from vendas.models import Venda


@login_required
@permission_required("accounts.acessar_dashboard", raise_exception=True)
def dashboard(request):
    empresa = request.user.perfil.empresa
    hoje = timezone.localdate()

    financeiro = resumo_financeiro(empresa)

    vendas_finalizadas = Venda.objects.filter(
        empresa=empresa,
        status=Venda.STATUS_FINALIZADA,
    ).prefetch_related("itens")

    vendas_hoje = vendas_finalizadas.filter(criada_em__date=hoje)

    quantidade_vendas_hoje = vendas_hoje.count()

    faturamento_hoje = sum(
        (venda.total for venda in vendas_hoje),
        Decimal("0.00"),
    )

    quantidade_vendas_total = vendas_finalizadas.count()

    faturamento_total = sum(
        (venda.total for venda in vendas_finalizadas),
        Decimal("0.00"),
    )

    variacoes = VariacaoProduto.objects.filter(
        empresa=empresa,
        ativa=True,
        produto__ativo=True,
    )

    quantidade_variacoes = variacoes.count()

    unidades_estoque = sum(
        variacoes.values_list(
            "estoque_atual",
            flat=True,
        )
    )

    estoque_zerado = variacoes.filter(
        estoque_atual=0,
    ).count()

    estoque_baixo = variacoes.filter(
        estoque_atual__gt=0,
        estoque_atual__lte=5,
    ).count()

    contexto = {
        "empresa": empresa,
        "financeiro": financeiro,
        "vendas": {
            "hoje": quantidade_vendas_hoje,
            "faturamento_hoje": faturamento_hoje,
            "total": quantidade_vendas_total,
            "faturamento_total": faturamento_total,
        },
        "estoque": {
            "variacoes": quantidade_variacoes,
            "unidades": unidades_estoque,
            "zerado": estoque_zerado,
            "baixo": estoque_baixo,
        },
    }

    return render(
        request,
        "dashboard/dashboard.html",
        contexto,
    )
