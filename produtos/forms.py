from django import forms

from .models import Produto, VariacaoProduto


class ProdutoForm(forms.ModelForm):

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["categoria"].queryset = (
                self.fields["categoria"].queryset.filter(
                    empresa=empresa,
                    ativa=True,
                )
            )

    class Meta:
        model = Produto

        fields = [
            "categoria",
            "nome",
            "descricao",
            "preco_custo",
            "preco_venda",
            "ativo",
        ]

        widgets = {
            "categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do produto",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição do produto",
                }
            ),
            "preco_custo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "preco_venda": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

class VariacaoProdutoForm(forms.ModelForm):

    class Meta:
        model = VariacaoProduto

        fields = [
            "sku",
            "tamanho",
            "cor",
            "estoque_minimo",
            "ativa",
        ]

        widgets = {
            "sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: CAM-PRE-M",
                }
            ),
            "tamanho": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: M",
                }
            ),
            "cor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Preto",
                }
            ),
            "estoque_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
            "ativa": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
