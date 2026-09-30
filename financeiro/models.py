from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from compras.models import Compra
from empresas.models import Empresa
from vendas.models import Venda


class LancamentoFinanceiro(models.Model):
    TIPO_RECEITA = "RECEITA"
    TIPO_DESPESA = "DESPESA"

    TIPOS = [
        (TIPO_RECEITA, "Receita"),
        (TIPO_DESPESA, "Despesa"),
    ]

    STATUS_PENDENTE = "PENDENTE"
    STATUS_PAGO = "PAGO"
    STATUS_CANCELADO = "CANCELADO"

    STATUS = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_PAGO, "Pago"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="lancamentos_financeiros",
    )

    venda = models.OneToOneField(
        Venda,
        on_delete=models.PROTECT,
        related_name="lancamento_financeiro",
        null=True,
        blank=True,
    )

    compra = models.OneToOneField(
        Compra,
        on_delete=models.PROTECT,
        related_name="lancamento_financeiro",
        null=True,
        blank=True,
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
    )

    descricao = models.CharField(max_length=200)

    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default=STATUS_PENDENTE,
    )

    data_vencimento = models.DateField()

    data_pagamento = models.DateField(
        null=True,
        blank=True,
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lancamentos_financeiros",
    )

    observacao = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.valor <= 0:
            raise ValidationError(
                {"valor": "O valor deve ser maior que zero."}
            )

        if self.venda_id and self.compra_id:
            raise ValidationError(
                "Um lançamento não pode estar ligado a uma venda "
                "e a uma compra ao mesmo tempo."
            )

        if self.venda_id:
            if self.tipo != self.TIPO_RECEITA:
                raise ValidationError(
                    "Um lançamento de venda deve ser uma receita."
                )

            if self.venda.empresa_id != self.empresa_id:
                raise ValidationError(
                    "A venda não pertence à empresa do lançamento."
                )

        if self.compra_id:
            if self.tipo != self.TIPO_DESPESA:
                raise ValidationError(
                    "Um lançamento de compra deve ser uma despesa."
                )

            if self.compra.empresa_id != self.empresa_id:
                raise ValidationError(
                    "A compra não pertence à empresa do lançamento."
                )

        if self.status == self.STATUS_PAGO and not self.data_pagamento:
            self.data_pagamento = timezone.localdate()

        if self.status != self.STATUS_PAGO:
            self.data_pagamento = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao}"