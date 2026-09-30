from django import forms

from produtos.models import VariacaoProduto

from .models import MovimentacaoEstoque


class MovimentacaoEstoqueForm(forms.ModelForm):

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["variacao"].queryset = (
                VariacaoProduto.objects
                .filter(
                    empresa=empresa,
                    ativa=True,
                    produto__ativo=True,
                )
                .select_related("produto")
                .order_by("produto__nome", "sku")
            )

    class Meta:
        model = MovimentacaoEstoque

        fields = [
            "variacao",
            "tipo",
            "motivo",
            "quantidade",
            "observacao",
        ]

        widgets = {
            "variacao": forms.Select(
                attrs={"class": "form-select"}
            ),
            "tipo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "motivo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "quantidade": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "observacao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Observação opcional",
                }
            ),
        }