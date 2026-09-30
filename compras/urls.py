from django.urls import path

from . import views

app_name = "compras"

urlpatterns = [
    path(
        "",
        views.lista_compras,
        name="lista",
    ),
    path(
        "nova/",
        views.criar_compra,
        name="nova",
    ),
    path(
        "<int:compra_id>/itens/novo/",
        views.adicionar_item,
        name="adicionar_item",
    ),
    path(
        "itens/<int:item_id>/editar/",
        views.editar_item,
        name="editar_item",
    ),
    path(
        "itens/<int:item_id>/remover/",
        views.remover_item,
        name="remover_item",
    ),
    path(
        "<int:compra_id>/finalizar/",
        views.finalizar,
        name="finalizar",
    ),
    path(
        "<int:compra_id>/cancelar/",
        views.cancelar,
        name="cancelar",
    ),
    path(
        "<int:compra_id>/",
        views.detalhe_compra,
        name="detalhe",
    ),
]
