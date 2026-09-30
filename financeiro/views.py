from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LancamentoFinanceiroForm
from .models import LancamentoFinanceiro
from .services import resumo_financeiro


@login_required
def lista_lancamentos(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    status = request.GET.get("status", "").strip()

    lancamentos = (
        LancamentoFinanceiro.objects.filter(empresa=empresa)
        .select_related("usuario", "venda", "compra")
        .order_by("-criado_em")
    )

    if busca:
        filtros = (
            Q(descricao__icontains=busca)
            | Q(observacao__icontains=busca)
            | Q(usuario__username__icontains=busca)
        )

        if busca.isdigit():
            filtros |= Q(id=int(busca))

        lancamentos = lancamentos.filter(filtros)

    if tipo in {
        LancamentoFinanceiro.TIPO_RECEITA,
        LancamentoFinanceiro.TIPO_DESPESA,
    }:
        lancamentos = lancamentos.filter(tipo=tipo)

    if status in {
        LancamentoFinanceiro.STATUS_PENDENTE,
        LancamentoFinanceiro.STATUS_PAGO,
        LancamentoFinanceiro.STATUS_CANCELADO,
    }:
        lancamentos = lancamentos.filter(status=status)

    resumo = resumo_financeiro(empresa)

    contexto = {
        "lancamentos": lancamentos,
        "busca": busca,
        "tipo_selecionado": tipo,
        "status_selecionado": status,
        "resumo": resumo,
    }

    return render(
        request,
        "financeiro/lista.html",
        contexto,
    )


@login_required
def novo_lancamento(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = LancamentoFinanceiroForm(request.POST)

        if form.is_valid():
            lancamento = form.save(commit=False)

            lancamento.empresa = empresa
            lancamento.usuario = request.user

            lancamento.full_clean()
            lancamento.save()

            messages.success(
                request,
                "Lançamento financeiro criado com sucesso.",
            )

            return redirect("financeiro:lista")

    else:
        form = LancamentoFinanceiroForm()

    return render(
        request,
        "financeiro/formulario.html",
        {
            "form": form,
        },
    )


@login_required
def detalhe_lancamento(request, lancamento_id):
    empresa = request.user.perfil.empresa

    lancamento = get_object_or_404(
        LancamentoFinanceiro.objects.select_related(
            "usuario",
            "venda",
            "compra",
        ),
        id=lancamento_id,
        empresa=empresa,
    )

    return render(
        request,
        "financeiro/detalhe.html",
        {
            "lancamento": lancamento,
        },
    )


@login_required
def marcar_como_pago(request, lancamento_id):
    empresa = request.user.perfil.empresa

    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        empresa=empresa,
    )

    if request.method != "POST":
        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if lancamento.status == LancamentoFinanceiro.STATUS_CANCELADO:
        messages.error(
            request,
            "Um lançamento cancelado não pode ser marcado como pago.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if lancamento.status == LancamentoFinanceiro.STATUS_PAGO:
        messages.warning(
            request,
            "Este lançamento já está pago.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    lancamento.status = LancamentoFinanceiro.STATUS_PAGO
    lancamento.save()

    if lancamento.tipo == LancamentoFinanceiro.TIPO_RECEITA:
        mensagem = "Receita marcada como recebida."
    else:
        mensagem = "Despesa marcada como paga."

    messages.success(request, mensagem)

    return redirect(
        "financeiro:detalhe",
        lancamento_id=lancamento.id,
    )


@login_required
def cancelar_lancamento(request, lancamento_id):
    empresa = request.user.perfil.empresa

    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        empresa=empresa,
    )

    if request.method != "POST":
        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if lancamento.venda_id or lancamento.compra_id:
        messages.error(
            request,
            "Lançamentos gerados por vendas ou compras devem ser "
            "cancelados pela operação de origem.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if lancamento.status == LancamentoFinanceiro.STATUS_CANCELADO:
        messages.warning(
            request,
            "Este lançamento já está cancelado.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    lancamento.status = LancamentoFinanceiro.STATUS_CANCELADO
    lancamento.save()

    messages.success(
        request,
        "Lançamento cancelado com sucesso.",
    )

    return redirect(
        "financeiro:detalhe",
        lancamento_id=lancamento.id,
    )


@login_required
def editar_lancamento(request, lancamento_id):
    empresa = request.user.perfil.empresa

    lancamento = get_object_or_404(
        LancamentoFinanceiro,
        id=lancamento_id,
        empresa=empresa,
    )

    if lancamento.venda_id or lancamento.compra_id:
        messages.error(
            request,
            "Lançamentos gerados por vendas ou compras não podem "
            "ser editados diretamente.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if lancamento.status != LancamentoFinanceiro.STATUS_PENDENTE:
        messages.error(
            request,
            "Somente lançamentos pendentes podem ser editados.",
        )

        return redirect(
            "financeiro:detalhe",
            lancamento_id=lancamento.id,
        )

    if request.method == "POST":
        form = LancamentoFinanceiroForm(
            request.POST,
            instance=lancamento,
        )

        if form.is_valid():
            lancamento = form.save(commit=False)

            lancamento.empresa = empresa
            lancamento.usuario = request.user

            lancamento.full_clean()
            lancamento.save()

            messages.success(
                request,
                "Lançamento atualizado com sucesso.",
            )

            return redirect(
                "financeiro:detalhe",
                lancamento_id=lancamento.id,
            )

    else:
        form = LancamentoFinanceiroForm(
            instance=lancamento,
        )

    return render(
        request,
        "financeiro/editar.html",
        {
            "form": form,
            "lancamento": lancamento,
        },
    )

