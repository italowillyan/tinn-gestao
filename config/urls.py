from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("produtos/", include("produtos.urls")),
    path("estoque/", include("estoque.urls")),
    path("clientes/", include("clientes.urls")),
    path("vendas/", include("vendas.urls")),
    path("fornecedores/", include("fornecedores.urls")),
    path("compras/", include("compras.urls")),
    path("financeiro/", include("financeiro.urls")),
    path("accounts/", include("accounts.urls")),
]
