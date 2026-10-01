from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProdutoForm, VariacaoProdutoForm
from .models import Produto, VariacaoProduto


@login_required
@permission_required("accounts.acessar_produtos", raise_exception=True)
def lista_produtos(request):
    empresa = request.user.perfil.empresa

    busca = request.GET.get("q", "").strip()

    produtos = (
        Produto.objects
        .filter(empresa=empresa)
        .select_related("categoria")
        .prefetch_related("variacoes")
        .order_by("nome")
    )

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca)
            | Q(variacoes__sku__icontains=busca)
        ).distinct()

    contexto = {
        "produtos": produtos,
        "busca": busca,
    }

    return render(
        request,
        "produtos/lista.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_produtos", raise_exception=True)
def criar_produto(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = ProdutoForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            produto = form.save(commit=False)

            produto.empresa = empresa

            produto.save()

            return redirect("produtos:lista")

    else:
        form = ProdutoForm(
            empresa=empresa,
        )

    contexto = {
        "form": form,
    }

    return render(
        request,
        "produtos/formulario.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_produtos", raise_exception=True)
def criar_variacao(request, produto_id):
    empresa = request.user.perfil.empresa

    produto = get_object_or_404(
        Produto,
        pk=produto_id,
        empresa=empresa,
    )

    if request.method == "POST":
        form = VariacaoProdutoForm(request.POST)

        if form.is_valid():
            variacao = form.save(commit=False)

            variacao.empresa = empresa
            variacao.produto = produto

            variacao.save()

            return redirect("produtos:lista")

    else:
        form = VariacaoProdutoForm()

    contexto = {
        "form": form,
        "produto": produto,
    }

    return render(
        request,
        "produtos/variacao_formulario.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_produtos", raise_exception=True)
def editar_produto(request, produto_id):
    empresa = request.user.perfil.empresa

    produto = get_object_or_404(
        Produto,
        pk=produto_id,
        empresa=empresa,
    )

    if request.method == "POST":
        form = ProdutoForm(
            request.POST,
            instance=produto,
            empresa=empresa,
        )

        if form.is_valid():
            form.save()

            return redirect("produtos:lista")

    else:
        form = ProdutoForm(
            instance=produto,
            empresa=empresa,
        )

    contexto = {
        "form": form,
        "produto": produto,
    }

    return render(
        request,
        "produtos/editar.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_produtos", raise_exception=True)
def editar_variacao(request, variacao_id):
    empresa = request.user.perfil.empresa

    variacao = get_object_or_404(
        VariacaoProduto,
        pk=variacao_id,
        empresa=empresa,
    )

    if request.method == "POST":
        form = VariacaoProdutoForm(
            request.POST,
            instance=variacao,
        )

        if form.is_valid():
            form.save()

            return redirect("produtos:lista")

    else:
        form = VariacaoProdutoForm(
            instance=variacao,
        )

    contexto = {
        "form": form,
        "variacao": variacao,
        "produto": variacao.produto,
    }

    return render(
        request,
        "produtos/variacao_editar.html",
        contexto,
    )
