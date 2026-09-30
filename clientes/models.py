from django.db import models

from empresas.models import Empresa


class Cliente(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="clientes",
    )

    nome = models.CharField(max_length=150)

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

    cpf = models.CharField(
        max_length=14,
        blank=True,
    )

    endereco = models.CharField(
        max_length=255,
        blank=True,
    )

    observacao = models.TextField(
        blank=True,
    )

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome