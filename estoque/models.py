from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from empresas.models import Empresa
from produtos.models import VariacaoProduto


class MovimentacaoEstoque(models.Model):
    TIPO_ENTRADA = "ENTRADA"
    TIPO_SAIDA = "SAIDA"

    TIPOS = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
    ]

    MOTIVO_COMPRA = "COMPRA"
    MOTIVO_VENDA = "VENDA"
    MOTIVO_AJUSTE = "AJUSTE"
    MOTIVO_DEVOLUCAO = "DEVOLUCAO"
    MOTIVO_OUTRO = "OUTRO"

    MOTIVOS = [
        (MOTIVO_COMPRA, "Compra"),
        (MOTIVO_VENDA, "Venda"),
        (MOTIVO_AJUSTE, "Ajuste de estoque"),
        (MOTIVO_DEVOLUCAO, "Devolução"),
        (MOTIVO_OUTRO, "Outro"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="movimentacoes_estoque",
    )

    variacao = models.ForeignKey(
        VariacaoProduto,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
    )

    motivo = models.CharField(
        max_length=20,
        choices=MOTIVOS,
    )

    quantidade = models.PositiveIntegerField()

    observacao = models.CharField(
        max_length=255,
        blank=True,
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_estoque",
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.quantidade <= 0:
            raise ValidationError(
                {"quantidade": "A quantidade deve ser maior que zero."}
            )

        if self.variacao_id and self.empresa_id:
            if self.variacao.empresa_id != self.empresa_id:
                raise ValidationError(
                    "A variação selecionada não pertence a esta empresa."
                )

    def save(self, *args, **kwargs):
        # Movimentações já existentes não podem ser alteradas.
        if self.pk:
            raise ValidationError(
                "Uma movimentação de estoque não pode ser alterada após ser criada."
            )

        self.full_clean()

        with transaction.atomic():
            variacao = VariacaoProduto.objects.select_for_update().get(
                pk=self.variacao_id
            )

            if self.tipo == self.TIPO_SAIDA:
                if variacao.estoque_atual < self.quantidade:
                    raise ValidationError(
                        "Estoque insuficiente para realizar esta saída."
                    )

                VariacaoProduto.objects.filter(
                    pk=variacao.pk
                ).update(
                    estoque_atual=F("estoque_atual") - self.quantidade
                )

            elif self.tipo == self.TIPO_ENTRADA:
                VariacaoProduto.objects.filter(
                    pk=variacao.pk
                ).update(
                    estoque_atual=F("estoque_atual") + self.quantidade
                )

            super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.variacao} - "
            f"{self.quantidade}"
        )