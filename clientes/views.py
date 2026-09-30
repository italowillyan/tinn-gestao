from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Cliente
from .forms import ClienteForm


@login_required
def lista_clientes(request):
    empresa = request.user.perfil.empresa
    busca = request.GET.get("q", "").strip()

    clientes = (
        Cliente.objects
        .filter(empresa=empresa)
        .order_by("nome")
    )

    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(email__icontains=busca)
            | Q(cpf__icontains=busca)
            | Q(instagram__icontains=busca)
        )

    contexto = {
        "clientes": clientes,
        "busca": busca,
    }

    return render(
        request,
        "clientes/lista.html",
        contexto,
    )

@login_required
def criar_cliente(request):
    empresa = request.user.perfil.empresa

    if request.method == "POST":
        form = ClienteForm(request.POST)

        if form.is_valid():
            cliente = form.save(commit=False)

            cliente.empresa = empresa
            cliente.save()

            return redirect("clientes:lista")

    else:
        form = ClienteForm()

    contexto = {
        "form": form,
    }

    return render(
        request,
        "clientes/formulario.html",
        contexto,
    )

@login_required
def editar_cliente(request, cliente_id):
    empresa = request.user.perfil.empresa

    cliente = get_object_or_404(
        Cliente,
        pk=cliente_id,
        empresa=empresa,
    )

    if request.method == "POST":
        form = ClienteForm(
            request.POST,
            instance=cliente,
        )

        if form.is_valid():
            form.save()

            return redirect("clientes:lista")

    else:
        form = ClienteForm(
            instance=cliente,
        )

    contexto = {
        "form": form,
        "cliente": cliente,
    }

    return render(
        request,
        "clientes/editar.html",
        contexto,
    )

