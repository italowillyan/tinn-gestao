from django.conf import settings

from django.db import models

from empresas.models import Empresa


class PerfilUsuario(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="usuarios",
    )

    cargo = models.CharField(
        max_length=100,
        blank=True,
    )

    ativo = models.BooleanField(
        default=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )


    class Meta:
        permissions = [
            (
                "acessar_dashboard",
                "Pode acessar o dashboard",
            ),
            (
                "acessar_vendas",
                "Pode acessar vendas",
            ),
            (
                "acessar_produtos",
                "Pode acessar produtos",
            ),
            (
                "acessar_estoque",
                "Pode acessar estoque",
            ),
            (
                "acessar_clientes",
                "Pode acessar clientes",
            ),
            (
                "acessar_compras",
                "Pode acessar compras",
            ),
            (
                "acessar_fornecedores",
                "Pode acessar fornecedores",
            ),
            (
                "acessar_financeiro",
                "Pode acessar financeiro",
            ),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.empresa}"
