from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente

        fields = [
            "nome",
            "telefone",
            "email",
            "instagram",
            "cpf",
            "endereco",
            "observacao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do cliente",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(84) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "cliente@email.com",
                }
            ),
            "instagram": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "@usuario",
                }
            ),
            "cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "000.000.000-00",
                }
            ),
            "endereco": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Endereço do cliente",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observações opcionais",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }