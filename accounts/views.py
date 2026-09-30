from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    erro = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        usuario = authenticate(
            request,
            username=username,
            password=password,
        )

        if usuario is not None:
            login(request, usuario)

            destino = request.GET.get("next") or "/"

            return redirect(destino)

        erro = "Usuário ou senha inválidos."

    return render(
        request,
        "accounts/login.html",
        {
            "erro": erro,
        },
    )


def logout_view(request):
    logout(request)

    return redirect("accounts:login")
