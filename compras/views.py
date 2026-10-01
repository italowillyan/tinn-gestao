from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from financeiro.services import cancelar_compra, finalizar_compra

from .forms import CompraForm, ItemCompraForm
from .models import Compra, ItemCompra


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def lista_compras(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()

    compras = (
        Compra.objects.filter(empresa=empresa)
        .select_related(
            "fornecedor",
            "usuario",
        )
        .prefetch_related("itens")
        .order_by("-criada_em")
    )

    if busca:
        filtros = (
            Q(fornecedor__nome__icontains=busca)
            | Q(fornecedor__nome_fantasia__icontains=busca)
            | Q(usuario__username__icontains=busca)
        )

        if busca.isdigit():
            filtros |= Q(id=int(busca))

        compras = compras.filter(filtros)

    return render(
        request,
        "compras/lista.html",
        {
            "compras": compras,
            "busca": busca,
        },
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def criar_compra(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = CompraForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            compra = form.save(commit=False)

            compra.empresa = empresa
            compra.usuario = request.user
            compra.status = Compra.STATUS_ABERTA

            compra.full_clean()
            compra.save()

            messages.success(
                request,
                "Compra criada. Agora adicione os produtos.",
            )

            return redirect(
                "compras:detalhe",
                compra_id=compra.id,
            )

    else:
        form = CompraForm(
            empresa=empresa,
        )

    return render(
        request,
        "compras/formulario.html",
        {
            "form": form,
        },
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def detalhe_compra(request, compra_id):
    empresa = request.user.perfil.empresa

    compra = get_object_or_404(
        Compra.objects.select_related(
            "fornecedor",
            "usuario",
        ).prefetch_related(
            "itens__variacao__produto",
        ),
        id=compra_id,
        empresa=empresa,
    )

    return render(
        request,
        "compras/detalhe.html",
        {
            "compra": compra,
        },
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def adicionar_item(request, compra_id):
    empresa = request.user.perfil.empresa

    compra = get_object_or_404(
        Compra,
        id=compra_id,
        empresa=empresa,
        status=Compra.STATUS_ABERTA,
    )

    if request.method == "POST":
        form = ItemCompraForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.compra = compra

            item.full_clean()
            item.save()

            messages.success(
                request,
                "Produto adicionado à compra.",
            )

            return redirect(
                "compras:detalhe",
                compra_id=compra.id,
            )

    else:
        form = ItemCompraForm(
            empresa=empresa,
        )

    return render(
        request,
        "compras/item_formulario.html",
        {
            "form": form,
            "compra": compra,
        },
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def editar_item(request, item_id):
    empresa = request.user.perfil.empresa

    item = get_object_or_404(
        ItemCompra.objects.select_related("compra"),
        id=item_id,
        compra__empresa=empresa,
    )

    compra = item.compra

    if compra.status != Compra.STATUS_ABERTA:
        messages.error(
            request,
            "Itens de uma compra finalizada ou cancelada " "não podem ser alterados.",
        )

        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    if request.method == "POST":
        form = ItemCompraForm(
            request.POST,
            instance=item,
            empresa=empresa,
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.compra = compra

            item.full_clean()
            item.save()

            messages.success(
                request,
                "Item atualizado.",
            )

            return redirect(
                "compras:detalhe",
                compra_id=compra.id,
            )

    else:
        form = ItemCompraForm(
            instance=item,
            empresa=empresa,
        )

    return render(
        request,
        "compras/item_editar.html",
        {
            "form": form,
            "compra": compra,
            "item": item,
        },
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def remover_item(request, item_id):
    empresa = request.user.perfil.empresa

    item = get_object_or_404(
        ItemCompra.objects.select_related("compra"),
        id=item_id,
        compra__empresa=empresa,
    )

    compra = item.compra

    if request.method != "POST":
        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    if compra.status != Compra.STATUS_ABERTA:
        messages.error(
            request,
            "Itens de uma compra finalizada ou cancelada " "não podem ser removidos.",
        )

        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    item.delete()

    messages.success(
        request,
        "Produto removido da compra.",
    )

    return redirect(
        "compras:detalhe",
        compra_id=compra.id,
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def finalizar(request, compra_id):
    empresa = request.user.perfil.empresa

    compra = get_object_or_404(
        Compra,
        id=compra_id,
        empresa=empresa,
    )

    if request.method != "POST":
        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    try:
        finalizar_compra(compra)

        messages.success(
            request,
            "Compra finalizada. O estoque foi atualizado "
            "e a despesa foi gerada no financeiro.",
        )

    except ValidationError as erro:
        messages.error(
            request,
            " ".join(erro.messages),
        )

    return redirect(
        "compras:detalhe",
        compra_id=compra.id,
    )


@login_required
@permission_required("accounts.acessar_compras", raise_exception=True)
def cancelar(request, compra_id):
    empresa = request.user.perfil.empresa

    compra = get_object_or_404(
        Compra,
        id=compra_id,
        empresa=empresa,
    )

    if request.method != "POST":
        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    if compra.status == Compra.STATUS_CANCELADA:
        messages.warning(
            request,
            "Esta compra já está cancelada.",
        )

        return redirect(
            "compras:detalhe",
            compra_id=compra.id,
        )

    try:
        cancelar_compra(compra)

        messages.success(
            request,
            "Compra cancelada.",
        )

    except ValidationError as erro:
        messages.error(
            request,
            " ".join(erro.messages),
        )

    return redirect(
        "compras:detalhe",
        compra_id=compra.id,
    )
