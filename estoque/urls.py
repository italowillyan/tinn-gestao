from django.urls import path

from . import views


app_name = "estoque"

urlpatterns = [
    path("", views.lista_estoque, name="lista"),
    path(
        "movimentacoes/nova/",
        views.nova_movimentacao,
        name="nova_movimentacao",
    ),
    path(
        "movimentacoes/",
        views.historico_movimentacoes,
        name="historico",
    ),
]