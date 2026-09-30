from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models, transaction

from clientes.models import Cliente
from empresas.models import Empresa
from estoque.models import MovimentacaoEstoque
from produtos.models import VariacaoProduto


class Venda(models.Model):
    STATUS_ABERTA = "ABERTA"
    STATUS_FINALIZADA = "FINALIZADA"
    STATUS_CANCELADA = "CANCELADA"

    STATUS = [
        (STATUS_ABERTA, "Aberta"),
        (STATUS_FINALIZADA, "Finalizada"),
        (STATUS_CANCELADA, "Cancelada"),
    ]

    PAGAMENTO_DINHEIRO = "DINHEIRO"
    PAGAMENTO_PIX = "PIX"
    PAGAMENTO_DEBITO = "DEBITO"
    PAGAMENTO_CREDITO = "CREDITO"
    PAGAMENTO_OUTRO = "OUTRO"

    FORMAS_PAGAMENTO = [
        (PAGAMENTO_DINHEIRO, "Dinheiro"),
        (PAGAMENTO_PIX, "PIX"),
        (PAGAMENTO_DEBITO, "Cartão de débito"),
        (PAGAMENTO_CREDITO, "Cartão de crédito"),
        (PAGAMENTO_OUTRO, "Outro"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="vendas",
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="vendas",
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vendas",
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default=STATUS_ABERTA,
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMAS_PAGAMENTO,
        blank=True,
    )

    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observacao = models.TextField(blank=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.desconto is not None and self.desconto < 0:
            raise ValidationError(
                {
                    "desconto": "O desconto não pode ser negativo.",
                }
            )

        if self.cliente_id and self.empresa_id:
            if self.cliente.empresa_id != self.empresa_id:
                raise ValidationError(
                    {
                        "cliente": "O cliente não pertence a esta empresa.",
                    }
                )

    @property
    def subtotal(self):
        return sum(
            (item.subtotal for item in self.itens.all()),
            Decimal("0.00"),
        )

    @property
    def total(self):
        valor = self.subtotal - self.desconto

        return max(
            valor,
            Decimal("0.00"),
        )

    @transaction.atomic
    def finalizar(self):
        venda = Venda.objects.select_for_update().get(pk=self.pk)

        if venda.status != self.STATUS_ABERTA:
            raise ValidationError(
                "Somente vendas abertas podem ser finalizadas."
            )

        itens = list(
            venda.itens.select_related(
                "variacao",
                "variacao__produto",
            )
        )

        if not itens:
            raise ValidationError(
                "A venda precisa possuir pelo menos um item."
            )

        if not venda.forma_pagamento:
            raise ValidationError(
                "Informe a forma de pagamento antes de finalizar."
            )

        for item in itens:
            if item.variacao.empresa_id != venda.empresa_id:
                raise ValidationError(
                    f"O produto {item.variacao} não pertence "
                    "à empresa da venda."
                )

            MovimentacaoEstoque.objects.create(
                empresa=venda.empresa,
                variacao=item.variacao,
                tipo=MovimentacaoEstoque.TIPO_SAIDA,
                motivo=MovimentacaoEstoque.MOTIVO_VENDA,
                quantidade=item.quantidade,
                usuario=venda.usuario,
                observacao=f"Venda #{venda.pk}",
            )

        venda.status = self.STATUS_FINALIZADA
        venda.finalizada_em = timezone.now()

        venda.save(
            update_fields=[
                "status",
                "atualizada_em",
                "finalizada_em",
            ]
        )

        self.status = venda.status

    @transaction.atomic
    def cancelar(self):
        venda = Venda.objects.select_for_update().get(pk=self.pk)

        if venda.status == self.STATUS_CANCELADA:
            raise ValidationError(
                "Esta venda já está cancelada."
            )

        if venda.status == self.STATUS_FINALIZADA:
            for item in venda.itens.select_related("variacao"):
                MovimentacaoEstoque.objects.create(
                    empresa=venda.empresa,
                    variacao=item.variacao,
                    tipo=MovimentacaoEstoque.TIPO_ENTRADA,
                    motivo=MovimentacaoEstoque.MOTIVO_DEVOLUCAO,
                    quantidade=item.quantidade,
                    usuario=venda.usuario,
                    observacao=(
                        f"Cancelamento da venda #{venda.pk}"
                    ),
                )

        venda.status = self.STATUS_CANCELADA
        venda.finalizada_em = timezone.now()

        venda.save(
            update_fields=[
                "status",
                "atualizada_em",
                "finalizada_em",
            ]
        )

        self.status = venda.status

    def __str__(self):
        return f"Venda #{self.pk or 'nova'}"


class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    variacao = models.ForeignKey(
        VariacaoProduto,
        on_delete=models.PROTECT,
        related_name="itens_venda",
    )

    quantidade = models.PositiveIntegerField()

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def clean(self):
        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError(
                {
                    "quantidade": (
                        "A quantidade deve ser maior que zero."
                    )
                }
            )

        if (
            self.preco_unitario is not None
            and self.preco_unitario < 0
        ):
            raise ValidationError(
                {
                    "preco_unitario": (
                        "O preço não pode ser negativo."
                    )
                }
            )

        if self.venda_id and self.variacao_id:
            if self.venda.empresa_id != self.variacao.empresa_id:
                raise ValidationError(
                    {
                        "variacao": (
                            "O produto não pertence à empresa da venda."
                        )
                    }
                )

        if self.venda_id:
            if self.venda.status != Venda.STATUS_ABERTA:
                raise ValidationError(
                    "Os itens de uma venda finalizada ou "
                    "cancelada não podem ser alterados."
                )

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.variacao}"
