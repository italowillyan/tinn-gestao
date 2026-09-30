from django.urls import path

from . import views


app_name = "clientes"

urlpatterns = [
    path("", views.lista_clientes, name="lista"),
    path("novo/", views.criar_cliente, name="novo"),
    path(
        "<int:cliente_id>/editar/",
        views.editar_cliente,
        name="editar",
    ),
]
