from django import forms

from clientes.models import Cliente
from produtos.models import VariacaoProduto

from .models import ItemVenda, Venda


class VendaForm(forms.ModelForm):
    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["cliente"].queryset = Cliente.objects.filter(
                empresa=empresa,
                ativo=True,
            ).order_by("nome")

    class Meta:
        model = Venda

        fields = [
            "cliente",
            "forma_pagamento",
            "desconto",
            "observacao",
        ]

        widgets = {
            "cliente": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "forma_pagamento": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "desconto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observação opcional",
                }
            ),
        }


class ItemVendaForm(forms.ModelForm):
    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            variacoes = (
                VariacaoProduto.objects.filter(
                    empresa=empresa,
                    ativa=True,
                    produto__ativo=True,
                )
                .select_related("produto")
                .order_by("produto__nome", "sku")
            )

            self.fields["variacao"].queryset = variacoes

            precos = {
                str(variacao.id): str(variacao.produto.preco_venda)
                for variacao in variacoes
            }

            self.precos_variacoes = precos

    def clean(self):
        cleaned_data = super().clean()

        variacao = cleaned_data.get("variacao")
        quantidade = cleaned_data.get("quantidade")

        if variacao and quantidade:
            if quantidade > variacao.estoque_atual:
                self.add_error(
                    "quantidade",
                    (
                        "Estoque insuficiente. "
                        f"Disponível: {variacao.estoque_atual} unidade(s)."
                    ),
                )

        return cleaned_data

    class Meta:
        model = ItemVenda

        fields = [
            "variacao",
            "quantidade",
            "preco_unitario",
        ]

        widgets = {
            "variacao": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_variacao",
                }
            ),
            "quantidade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "preco_unitario": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "id": "id_preco_unitario",
                }
            ),
        }
