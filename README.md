# TINN Gestão

Sistema de gestão comercial desenvolvido para centralizar operações de vendas, compras, estoque e financeiro em uma única plataforma.

O projeto está sendo desenvolvido com foco em uma arquitetura multiempresa, permitindo que a mesma aplicação possa futuramente atender diferentes negócios.

## Status

🚧 Em desenvolvimento

A versão atual já possui os principais módulos operacionais e está passando pela etapa de refinamento, testes e preparação para produção.

## Funcionalidades

### Produtos
- Cadastro de produtos
- Categorias
- Variações de produtos
- SKU
- Controle de produtos ativos

### Estoque
- Controle de estoque por variação
- Entradas e saídas
- Histórico de movimentações
- Movimentações vinculadas a compras e vendas
- Controle de estoque por empresa

### Vendas
- Criação de vendas
- Adição e edição de itens
- Clientes
- Formas de pagamento
- Descontos
- Finalização de vendas
- Cancelamento de vendas
- Integração com estoque e financeiro

### Compras
- Cadastro de fornecedores
- Criação de compras
- Itens e custos de aquisição
- Frete e desconto
- Finalização de compras
- Cancelamento de compras
- Integração com estoque e financeiro

### Financeiro
- Receitas
- Despesas
- Contas a receber
- Contas a pagar
- Lançamentos manuais
- Controle de pagamentos e recebimentos
- Cancelamento sem exclusão do histórico
- Integração com vendas e compras
- Resumo financeiro

### Dashboard
- Vendas
- Faturamento
- Receitas recebidas
- Despesas pagas
- Saldo realizado
- Contas a receber
- Contas a pagar
- Indicadores de estoque

## Tecnologias

- Python
- Django
- PostgreSQL
- Bootstrap 5
- HTML5
- CSS3
- JavaScript

## Arquitetura

O sistema foi estruturado em módulos independentes dentro do Django:

```text
tinn-gestao/
├── accounts/
├── clientes/
├── compras/
├── config/
├── dashboard/
├── empresas/
├── estoque/
├── financeiro/
├── fornecedores/
├── produtos/
├── vendas/
├── manage.py
├── requirements.txt
└── README.md
