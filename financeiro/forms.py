from django import forms

from .models import LancamentoFinanceiro


class LancamentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro

        fields = [
            "tipo",
            "descricao",
            "valor",
            "status",
            "data_vencimento",
            "data_pagamento",
            "observacao",
        ]

        widgets = {
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "descricao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Conta de energia",
                }
            ),
            "valor": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "data_vencimento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "data_pagamento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações opcionais",
                }
            ),
        }
