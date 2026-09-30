from django.urls import path

from . import views


app_name = "produtos"

urlpatterns = [
    path("", views.lista_produtos, name="lista"),
    path("novo/", views.criar_produto, name="novo"),
    path(
        "<int:produto_id>/variacoes/nova/",
        views.criar_variacao,
        name="nova_variacao",
    ),
    path(
        "<int:produto_id>/editar/",
        views.editar_produto,
        name="editar",
    ),
    path(
        "variacoes/<int:variacao_id>/editar/",
        views.editar_variacao,
        name="editar_variacao",
    ),
]