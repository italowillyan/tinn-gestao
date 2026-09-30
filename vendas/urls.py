from django.urls import path

from . import views

app_name = "vendas"

urlpatterns = [
    path("", views.lista_vendas, name="lista"),
    path("nova/", views.criar_venda, name="nova"),
    path(
        "<int:venda_id>/itens/novo/",
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
        "<int:venda_id>/finalizar/",
        views.finalizar,
        name="finalizar",
    ),
    path(
        "<int:venda_id>/cancelar/",
        views.cancelar,
        name="cancelar",
    ),
    path(
        "<int:venda_id>/",
        views.detalhe_venda,
        name="detalhe",
    ),
]
