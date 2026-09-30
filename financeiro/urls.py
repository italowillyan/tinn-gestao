from django.urls import path

from . import views

app_name = "financeiro"


urlpatterns = [
    path(
        "",
        views.lista_lancamentos,
        name="lista",
    ),
    path(
        "novo/",
        views.novo_lancamento,
        name="novo",
    ),
    path(
        "<int:lancamento_id>/pagar/",
        views.marcar_como_pago,
        name="marcar_como_pago",
    ),
    path(
        "<int:lancamento_id>/",
        views.detalhe_lancamento,
        name="detalhe",
    ),
    path(
        "<int:lancamento_id>/cancelar/",
        views.cancelar_lancamento,
        name="cancelar",
    ),
    path(
        "<int:lancamento_id>/editar/",
        views.editar_lancamento,
        name="editar",
    ),
]
