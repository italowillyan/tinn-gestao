from django.contrib import admin

from .models import Categoria, Produto, VariacaoProduto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "empresa", "ativa")
    search_fields = ("nome",)
    list_filter = ("empresa", "ativa")


class VariacaoProdutoInline(admin.TabularInline):
    model = VariacaoProduto
    extra = 1


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "empresa",
        "categoria",
        "preco_venda",
        "ativo",
    )

    search_fields = ("nome",)
    list_filter = ("empresa", "categoria", "ativo")

    inlines = [VariacaoProdutoInline]


@admin.register(VariacaoProduto)
class VariacaoProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "sku",
        "tamanho",
        "cor",
        "estoque_atual",
        "estoque_minimo",
        "ativa",
    )

    search_fields = ("produto__nome", "sku")
    list_filter = ("ativa",)