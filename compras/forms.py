from django import forms

from fornecedores.models import Fornecedor
from produtos.models import VariacaoProduto

from .models import Compra, ItemCompra


class CompraForm(forms.ModelForm):
    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["fornecedor"].queryset = Fornecedor.objects.filter(
                empresa=empresa,
                ativo=True,
            ).order_by("nome")

    class Meta:
        model = Compra

        fields = [
            "fornecedor",
            "frete",
            "desconto",
            "observacao",
        ]

        widgets = {
            "fornecedor": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "frete": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "desconto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Informações adicionais sobre a compra",
                }
            ),
        }


class ItemCompraForm(forms.ModelForm):
    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["variacao"].queryset = (
                VariacaoProduto.objects.filter(
                    empresa=empresa,
                    ativa=True,
                    produto__ativo=True,
                )
                .select_related("produto")
                .order_by(
                    "produto__nome",
                    "sku",
                )
            )

    class Meta:
        model = ItemCompra

        fields = [
            "variacao",
            "quantidade",
            "custo_unitario",
        ]

        widgets = {
            "variacao": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "quantidade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "custo_unitario": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0,00",
                }
            ),
        }
