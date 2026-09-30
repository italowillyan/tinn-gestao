from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from empresas.models import Empresa
from estoque.models import MovimentacaoEstoque
from fornecedores.models import Fornecedor
from produtos.models import VariacaoProduto


class Compra(models.Model):
    STATUS_ABERTA = "ABERTA"
    STATUS_FINALIZADA = "FINALIZADA"
    STATUS_CANCELADA = "CANCELADA"

    STATUS = [
        (STATUS_ABERTA, "Aberta"),
        (STATUS_FINALIZADA, "Finalizada"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="compras",
    )

    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name="compras",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="compras",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default=STATUS_ABERTA,
    )

    frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observacao = models.TextField(
        blank=True,
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizada_em = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        if self.frete is not None and self.frete < 0:
            raise ValidationError({"frete": ("O frete não pode ser negativo.")})

        if self.desconto is not None and self.desconto < 0:
            raise ValidationError({"desconto": ("O desconto não pode ser negativo.")})

        if self.fornecedor_id and self.empresa_id:
            if self.fornecedor.empresa_id != self.empresa_id:
                raise ValidationError(
                    {"fornecedor": ("O fornecedor não pertence " "a esta empresa.")}
                )

    @property
    def subtotal(self):
        return sum(
            (item.subtotal for item in self.itens.all()),
            Decimal("0.00"),
        )

    @property
    def total(self):
        valor = self.subtotal + self.frete - self.desconto

        return max(
            valor,
            Decimal("0.00"),
        )

    @transaction.atomic
    def finalizar(self):
        compra = Compra.objects.select_for_update().get(pk=self.pk)

        if compra.status != self.STATUS_ABERTA:
            raise ValidationError("Somente compras abertas podem ser finalizadas.")

        itens = list(
            compra.itens.select_related(
                "variacao",
                "variacao__produto",
            )
        )

        if not itens:
            raise ValidationError("A compra precisa possuir pelo menos um item.")

        for item in itens:
            if item.variacao.empresa_id != compra.empresa_id:
                raise ValidationError(
                    (f"O produto {item.variacao} " "não pertence à empresa da compra.")
                )

            MovimentacaoEstoque.objects.create(
                empresa=compra.empresa,
                variacao=item.variacao,
                tipo=MovimentacaoEstoque.TIPO_ENTRADA,
                motivo=MovimentacaoEstoque.MOTIVO_COMPRA,
                quantidade=item.quantidade,
                usuario=compra.usuario,
                observacao=f"Compra #{compra.pk}",
            )

        compra.status = self.STATUS_FINALIZADA

        compra.save(
            update_fields=[
                "status",
                "atualizada_em",
            ]
        )

        self.status = compra.status

    @transaction.atomic
    def cancelar(self):
        compra = Compra.objects.select_for_update().get(pk=self.pk)

        if compra.status == self.STATUS_CANCELADA:
            raise ValidationError("Esta compra já está cancelada.")

        if compra.status == self.STATUS_FINALIZADA:
            for item in compra.itens.select_related("variacao"):
                MovimentacaoEstoque.objects.create(
                    empresa=compra.empresa,
                    variacao=item.variacao,
                    tipo=MovimentacaoEstoque.TIPO_SAIDA,
                    motivo=MovimentacaoEstoque.MOTIVO_AJUSTE,
                    quantidade=item.quantidade,
                    usuario=compra.usuario,
                    observacao=(f"Cancelamento da compra #{compra.pk}"),
                )

        compra.status = self.STATUS_CANCELADA

        compra.save(
            update_fields=[
                "status",
                "atualizada_em",
            ]
        )

        self.status = compra.status

    def __str__(self):
        return f"Compra #{self.pk or 'nova'}"


class ItemCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    variacao = models.ForeignKey(
        VariacaoProduto,
        on_delete=models.PROTECT,
        related_name="itens_compra",
    )

    quantidade = models.PositiveIntegerField()

    custo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def clean(self):
        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError(
                {"quantidade": ("A quantidade deve ser maior que zero.")}
            )

        if self.custo_unitario is not None and self.custo_unitario < 0:
            raise ValidationError(
                {"custo_unitario": ("O custo não pode ser negativo.")}
            )

        if self.compra_id and self.variacao_id:
            if self.compra.empresa_id != self.variacao.empresa_id:
                raise ValidationError(
                    {"variacao": ("O produto não pertence " "à empresa da compra.")}
                )

        if self.compra_id:
            if self.compra.status != Compra.STATUS_ABERTA:
                raise ValidationError(
                    "Os itens de uma compra finalizada "
                    "ou cancelada não podem ser alterados."
                )

    @property
    def subtotal(self):
        return self.quantidade * self.custo_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.variacao}"
