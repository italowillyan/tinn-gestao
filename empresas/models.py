from django.db import models

class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    nome_fantasia = models.CharField(max_length=150, blank=True)
    documento = models.CharField(max_length=20, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    ativa = models.BooleanField(default=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_fantasia or self.nome