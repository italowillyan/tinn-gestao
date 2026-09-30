from django.urls import path

from . import views

app_name = "fornecedores"

urlpatterns = [
    path(
        "",
        views.lista_fornecedores,
        name="lista",
    ),
    path(
        "novo/",
        views.criar_fornecedor,
        name="novo",
    ),
    path(
        "<int:fornecedor_id>/editar/",
        views.editar_fornecedor,
        name="editar",
    ),
]
