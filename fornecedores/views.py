from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FornecedorForm
from .models import Fornecedor


@login_required
@permission_required("accounts.acessar_fornecedores", raise_exception=True)
def lista_fornecedores(request):
    empresa = request.user.perfil.empresa

    busca = request.GET.get("q", "").strip()

    fornecedores = Fornecedor.objects.filter(
        empresa=empresa,
    ).order_by("nome")

    if busca:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=busca)
            | Q(nome_fantasia__icontains=busca)
            | Q(documento__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(email__icontains=busca)
        )

    return render(
        request,
        "fornecedores/lista.html",
        {
            "fornecedores": fornecedores,
            "busca": busca,
        },
    )


@login_required
@permission_required("accounts.acessar_fornecedores", raise_exception=True)
def criar_fornecedor(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = FornecedorForm(request.POST)

        if form.is_valid():
            fornecedor = form.save(commit=False)
            fornecedor.empresa = empresa
            fornecedor.save()

            return redirect("fornecedores:lista")

    else:
        form = FornecedorForm()

    return render(
        request,
        "fornecedores/formulario.html",
        {
            "form": form,
        },
    )


@login_required
@permission_required("accounts.acessar_fornecedores", raise_exception=True)
def editar_fornecedor(request, fornecedor_id):
    empresa = request.user.perfil.empresa

    fornecedor = get_object_or_404(
        Fornecedor,
        id=fornecedor_id,
        empresa=empresa,
    )

    if request.method == "POST":
        form = FornecedorForm(
            request.POST,
            instance=fornecedor,
        )

        if form.is_valid():
            form.save()

            return redirect("fornecedores:lista")

    else:
        form = FornecedorForm(
            instance=fornecedor,
        )

    return render(
        request,
        "fornecedores/editar.html",
        {
            "form": form,
            "fornecedor": fornecedor,
        },
    )
