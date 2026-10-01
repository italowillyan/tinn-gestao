from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Q
from django.shortcuts import render, redirect

from produtos.models import VariacaoProduto
from .models import MovimentacaoEstoque
from .forms import MovimentacaoEstoqueForm

@login_required
@permission_required("accounts.acessar_estoque", raise_exception=True)
def lista_estoque(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()

    variacoes = (
        VariacaoProduto.objects
        .filter(
            empresa=empresa,
            ativa=True,
            produto__ativo=True,
        )
        .select_related(
            "produto",
            "produto__categoria",
        )
        .order_by("produto__nome", "sku")
    )

    if busca:
        variacoes = variacoes.filter(
            Q(produto__nome__icontains=busca)
            | Q(sku__icontains=busca)
            | Q(cor__icontains=busca)
            | Q(tamanho__icontains=busca)
        )

    contexto = {
        "variacoes": variacoes,
        "busca": busca,
    }

    return render(
        request,
        "estoque/lista.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_estoque", raise_exception=True)
def nova_movimentacao(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = MovimentacaoEstoqueForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            movimentacao = form.save(commit=False)

            movimentacao.empresa = empresa
            movimentacao.usuario = request.user

            movimentacao.save()

            return redirect("estoque:lista")

    else:
        form = MovimentacaoEstoqueForm(
            empresa=empresa,
        )

    contexto = {
        "form": form,
    }

    return render(
        request,
        "estoque/movimentacao_formulario.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_estoque", raise_exception=True)
def historico_movimentacoes(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()

    movimentacoes = (
        MovimentacaoEstoque.objects
        .filter(empresa=empresa)
        .select_related(
            "variacao",
            "variacao__produto",
            "usuario",
        )
        .order_by("-criada_em")
    )

    if busca:
        movimentacoes = movimentacoes.filter(
            Q(variacao__produto__nome__icontains=busca)
            | Q(variacao__sku__icontains=busca)
            | Q(observacao__icontains=busca)
        )

    contexto = {
        "movimentacoes": movimentacoes,
        "busca": busca,
    }

    return render(
        request,
        "estoque/historico.html",
        contexto,
    )
