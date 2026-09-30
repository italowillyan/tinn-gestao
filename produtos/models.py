from django.db import models

from empresas.models import Empresa


class Categoria(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="categorias",
    )

    nome = models.CharField(max_length=100)
    ativa = models.BooleanField(default=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="produtos",
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
    )

    nome = models.CharField(max_length=150)

    descricao = models.TextField(blank=True)

    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    preco_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class VariacaoProduto(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="variacoes_produtos",
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="variacoes",
    )

    sku = models.CharField(max_length=50)

    tamanho = models.CharField(
        max_length=20,
        blank=True,
    )

    cor = models.CharField(
        max_length=50,
        blank=True,
    )

    estoque_atual = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)

    ativa = models.BooleanField(default=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "sku"],
                name="unique_sku_por_empresa",
            )
        ]

    def __str__(self):
        detalhes = " / ".join(
            item for item in [self.tamanho, self.cor] if item
        )

        if detalhes:
            return f"{self.produto.nome} - {detalhes}"

        return self.produto.nome