from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import ItemVenda, Venda
from .forms import ItemVendaForm, VendaForm

from financeiro.services import cancelar_venda, finalizar_venda


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def lista_vendas(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()

    vendas = (
        Venda.objects
        .filter(empresa=empresa)
        .select_related(
            "cliente",
            "usuario",
        )
        .prefetch_related("itens")
        .order_by("-criada_em")
    )

    if busca:
        filtros = (
            Q(cliente__nome__icontains=busca)
            | Q(usuario__username__icontains=busca)
        )

        if busca.isdigit():
            filtros |= Q(pk=int(busca))

        vendas = vendas.filter(filtros)

    contexto = {
        "vendas": vendas,
        "busca": busca,
    }

    return render(
        request,
        "vendas/lista.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def criar_venda(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = VendaForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            venda = form.save(commit=False)

            venda.empresa = empresa
            venda.usuario = request.user
            venda.status = Venda.STATUS_ABERTA

            venda.save()

            return redirect(
                "vendas:detalhe",
                venda_id=venda.id,
            )

    else:
        form = VendaForm(
            empresa=empresa,
        )

    contexto = {
        "form": form,
    }

    return render(
        request,
        "vendas/formulario.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def detalhe_venda(request, venda_id):
    empresa = request.user.perfil.empresa

    venda = get_object_or_404(
        Venda.objects
        .select_related(
            "cliente",
            "usuario",
        )
        .prefetch_related(
            "itens__variacao__produto",
        ),
        pk=venda_id,
        empresa=empresa,
    )

    contexto = {
        "venda": venda,
    }

    return render(
        request,
        "vendas/detalhe.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def adicionar_item(request, venda_id):
    empresa = request.user.perfil.empresa

    venda = get_object_or_404(
        Venda,
        pk=venda_id,
        empresa=empresa,
        status=Venda.STATUS_ABERTA,
    )

    if request.method == "POST":
        form = ItemVendaForm(
            request.POST,
            empresa=empresa,
        )

        if form.is_valid():
            item = form.save(commit=False)

            item.venda = venda
            item.full_clean()
            item.save()

            return redirect(
                "vendas:detalhe",
                venda_id=venda.id,
            )

    else:
        form = ItemVendaForm(
            empresa=empresa,
        )

    contexto = {
        "form": form,
        "venda": venda,
    }

    return render(
        request,
        "vendas/item_formulario.html",
        contexto,
    )


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def finalizar(request, venda_id):
    empresa = request.user.perfil.empresa

    venda = get_object_or_404(
        Venda,
        pk=venda_id,
        empresa=empresa,
        status=Venda.STATUS_ABERTA,
    )

    if request.method == "POST":
        try:
            finalizar_venda(venda)

            messages.success(
                request,
                f"Venda #{venda.id} finalizada com sucesso.",
            )

        except ValidationError as erro:
            messages.error(
                request,
                " ".join(erro.messages),
            )

        return redirect(
            "vendas:detalhe",
            venda_id=venda.id,
        )

    return redirect(
        "vendas:detalhe",
        venda_id=venda.id,
    )


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def cancelar(request, venda_id):
    empresa = request.user.perfil.empresa

    venda = get_object_or_404(
        Venda,
        id=venda_id,
        empresa=empresa,
    )

    if request.method != "POST":
        return redirect("vendas:detalhe", venda_id=venda.id)

    if venda.status == Venda.STATUS_CANCELADA:
        messages.warning(request, "Esta venda já está cancelada.")
        return redirect("vendas:detalhe", venda_id=venda.id)

    try:
        cancelar_venda(venda)
        messages.success(request, "Venda cancelada com sucesso.")
    except ValidationError as erro:
        messages.error(request, " ".join(erro.messages))

    return redirect("vendas:detalhe", venda_id=venda.id)


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def remover_item(request, item_id):
    empresa = request.user.perfil.empresa

    item = get_object_or_404(
        ItemVenda.objects.select_related("venda"),
        id=item_id,
        venda__empresa=empresa,
    )

    venda = item.venda

    if request.method != "POST":
        return redirect("vendas:detalhe", venda_id=venda.id)

    if venda.status != Venda.STATUS_ABERTA:
        messages.error(
            request,
            "Não é possível remover itens de uma venda finalizada ou cancelada.",
        )
        return redirect("vendas:detalhe", venda_id=venda.id)

    item.delete()

    messages.success(
        request,
        "Produto removido da venda com sucesso.",
    )

    return redirect("vendas:detalhe", venda_id=venda.id)


@login_required
@permission_required("accounts.acessar_vendas", raise_exception=True)
def editar_item(request, item_id):
    empresa = request.user.perfil.empresa

    item = get_object_or_404(
        ItemVenda.objects.select_related(
            "venda",
            "variacao",
            "variacao__produto",
        ),
        id=item_id,
        venda__empresa=empresa,
    )

    venda = item.venda

    if venda.status != Venda.STATUS_ABERTA:
        messages.error(
            request,
            "Não é possível editar itens de uma venda finalizada ou cancelada.",
        )
        return redirect("vendas:detalhe", venda_id=venda.id)

    if request.method == "POST":
        form = ItemVendaForm(
            request.POST,
            instance=item,
            empresa=empresa,
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.venda = venda
            item.full_clean()
            item.save()

            messages.success(
                request,
                "Produto atualizado com sucesso.",
            )

            return redirect(
                "vendas:detalhe",
                venda_id=venda.id,
            )
    else:
        form = ItemVendaForm(
            instance=item,
            empresa=empresa,
        )

    return render(
        request,
        "vendas/item_editar.html",
        {
            "form": form,
            "venda": venda,
            "item": item,
        },
    )
