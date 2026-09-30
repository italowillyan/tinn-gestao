from django import forms

from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor

        fields = [
            "nome",
            "nome_fantasia",
            "documento",
            "telefone",
            "email",
            "instagram",
            "site",
            "observacao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome ou razão social",
                }
            ),
            "nome_fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome fantasia",
                }
            ),
            "documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(00) 00000-0000",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "email@fornecedor.com",
                }
            ),
            "instagram": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "@usuario",
                }
            ),
            "site": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://...",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Informações adicionais",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
