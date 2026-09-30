from django.db import models

from empresas.models import Empresa


class Fornecedor(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="fornecedores",
    )

    nome = models.CharField(max_length=150)

    nome_fantasia = models.CharField(
        max_length=150,
        blank=True,
    )

    documento = models.CharField(
        max_length=20,
        blank=True,
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(
        blank=True,
    )

    instagram = models.CharField(
        max_length=100,
        blank=True,
    )

    site = models.URLField(
        blank=True,
    )

    observacao = models.TextField(
        blank=True,
    )

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_fantasia or self.nome