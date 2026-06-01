# API Raízes do Nordeste

Projeto desenvolvido para a atividade prática do Projeto Multidisciplinar.

A proposta é criar uma API para uma rede de lanchonetes com controle de usuários, unidades, produtos, estoque, pedidos, pagamento, fidelidade e auditoria.

O sistema foi desenvolvido em Python usando FastAPI e PostgreSQL, com documentação automática pelo Swagger.

## Objetivo do projeto

O objetivo da API é simular o funcionamento básico de um sistema back-end para uma rede de lanchonetes que atende por diferentes canais, como aplicativo, totem, balcão, pickup e web.

A aplicação permite cadastrar usuários, unidades da rede, produtos, controlar estoque, criar pedidos, processar pagamento mock, gerar pontos de fidelidade e registrar ações importantes em auditoria.

## Tecnologias utilizadas

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Uvicorn
- Passlib
- Bcrypt
- JWT com python-jose
- Swagger / OpenAPI
- Git e GitHub

## Funcionalidades implementadas

### Usuários

O sistema permite:

- Cadastrar usuário
- Listar usuários
- Buscar usuário por ID
- Atualizar usuário
- Deletar usuário
- Armazenar senha com hash
- Controlar perfil do usuário
- Registrar consentimento LGPD

Perfis disponíveis:

- `CLIENTE`
- `ATENDENTE`
- `GERENTE`
- `ADMIN`

### Autenticação

Foi implementado login com JWT.

Endpoints principais:

- `POST /auth/login`
- `GET /auth/me`

O login verifica o e-mail e a senha cadastrados. Se os dados estiverem corretos, o sistema retorna um token de acesso.

Exemplo de login:

```json
{
  "email": "rafaela@gmail.com",
  "senha": "123456"
}
```

Exemplo de resposta:

```json
{
  "access_token": "token_jwt_gerado",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nome": "Rafaela",
    "email": "rafaela@gmail.com",
    "perfil": "CLIENTE",
    "consentimento_lgpd": false
  }
}
```

### Unidades

O sistema possui cadastro de unidades da rede.

Endpoints:

- `GET /unidades`
- `POST /unidades`
- `GET /unidades/{unidade_id}`
- `PUT /unidades/{unidade_id}`
- `DELETE /unidades/{unidade_id}`

Exemplo de cadastro de unidade:

```json
{
  "nome": "Unidade Centro",
  "cidade": "Catalão",
  "estado": "GO",
  "endereco": "Rua Principal, 100",
  "ativa": true
}
```

O delete de unidade funciona como desativação, mantendo o histórico dos registros relacionados.

### Produtos

O sistema permite cadastrar produtos vinculados a uma unidade.

Endpoints:

- `GET /produtos`
- `POST /produtos`
- `GET /produtos/{produto_id}`
- `PUT /produtos/{produto_id}`
- `DELETE /produtos/{produto_id}`

Exemplo de cadastro de produto:

```json
{
  "unidade_id": 1,
  "nome": "Cuzcuz",
  "descricao": "Cuzcuz Nordestino com carne seca",
  "preco": 30.0,
  "categoria": "LANCHE",
  "ativo": true
}
```

### Estoque

O estoque controla a quantidade de produtos disponíveis por unidade.

Endpoints:

- `GET /estoque`
- `POST /estoque`
- `GET /estoque/{estoque_id}`
- `PUT /estoque/{estoque_id}`
- `DELETE /estoque/{estoque_id}`

Exemplo de cadastro de estoque:

```json
{
  "unidade_id": 1,
  "produto_id": 1,
  "quantidade": 50
}
```

O sistema impede o cadastro de estoque duplicado para o mesmo produto na mesma unidade.

### Pedidos

O pedido pode conter um ou mais itens.

Ao criar um pedido, o sistema verifica se o usuário existe, se a unidade está ativa, se o produto pertence à unidade e se existe estoque suficiente.

Endpoints:

- `GET /pedidos`
- `POST /pedidos`
- `GET /pedidos/{pedido_id}`
- `PUT /pedidos/{pedido_id}/status`

Canais de pedido disponíveis:

- `APP`
- `TOTEM`
- `BALCAO`
- `PICKUP`
- `WEB`

Exemplo de criação de pedido:

```json
{
  "usuario_id": 1,
  "unidade_id": 1,
  "canalPedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2
    }
  ],
  "formaPagamento": "MOCK"
}
```

Ao criar o pedido, o sistema calcula o valor total e reduz a quantidade do estoque.

### Pagamentos

Foi implementado um pagamento mock para simular aprovação ou recusa de pagamento.

Endpoints:

- `GET /pagamentos`
- `POST /pagamentos`
- `GET /pagamentos/{pagamento_id}`

Exemplo de pagamento aprovado:

```json
{
  "pedido_id": 1,
  "forma_pagamento": "MOCK",
  "status_pagamento": "APROVADO"
}
```

Status de pagamento disponíveis:

- `APROVADO`
- `RECUSADO`

Quando o pagamento é aprovado, o pedido muda para `PAGO` e o sistema gera pontos de fidelidade para o usuário.

### Fidelidade

O sistema possui controle de pontos de fidelidade.

Endpoints:

- `GET /fidelidade/{usuario_id}`
- `POST /fidelidade/resgatar`

Exemplo de resgate de pontos:

```json
{
  "usuario_id": 1,
  "pontos": 10
}
```

O sistema valida se o usuário possui pontos suficientes antes de permitir o resgate.

### Auditoria

A auditoria registra ações importantes realizadas no sistema.

Endpoint:

- `GET /auditoria`

Ações registradas:

- `USUARIO_CRIADO`
- `USUARIO_ATUALIZADO`
- `USUARIO_DELETADO`
- `LOGIN_REALIZADO`
- `UNIDADE_CRIADA`
- `UNIDADE_ATUALIZADA`
- `UNIDADE_DESATIVADA`
- `PRODUTO_CRIADO`
- `PRODUTO_ATUALIZADO`
- `PRODUTO_DELETADO`
- `ESTOQUE_CRIADO`
- `ESTOQUE_ATUALIZADO`
- `ESTOQUE_DELETADO`
- `PEDIDO_CRIADO`
- `STATUS_PEDIDO_ALTERADO`
- `PAGAMENTO_APROVADO`
- `PAGAMENTO_RECUSADO`
- `PONTOS_RESGATADOS`

Exemplo de retorno:

```json
{
  "page": 1,
  "limit": 10,
  "dados": [
    {
      "id": 1,
      "usuario_id": 1,
      "acao": "PEDIDO_CRIADO",
      "recurso": "pedidos",
      "detalhes": "Pedido 1 criado no canal APP com valor total 30.0",
      "data_registro": "2026-06-01T18:27:23"
    }
  ]
}
```

## Padrão de erro

A API retorna erros em formato JSON padronizado.

Exemplo:

```json
{
  "erro": "RECURSO_NAO_ENCONTRADO",
  "mensagem": "Usuário não encontrado",
  "status": 404,
  "path": "/usuarios/99",
  "timestamp": "2026-06-01T18:30:00"
}
```

Principais códigos tratados:

- `400`: requisição inválida
- `401`: não autenticado
- `404`: recurso não encontrado
- `409`: conflito de regra de negócio
- `422`: dados inválidos
- `500`: erro interno

## Estrutura do projeto

```text
raizes-backend/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── __init__.py
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/heliogabrielsl/raizesnordeste-backend.git
```

Entrar na pasta do projeto:

```bash
cd raizesnordeste-backend
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

Ativar o ambiente virtual no Windows:

```bash
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Dependências principais:

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
passlib==1.7.4
bcrypt==4.0.1
python-jose[cryptography]
```

### 4. Configurar o banco de dados

Criar um arquivo `.env` na raiz do projeto com a URL do banco PostgreSQL.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/raizes_db
```

O nome do banco usado no projeto foi:

```text
raizes_db
```

### 5. Executar a API

```bash
uvicorn app.main:app --reload
```

Se tudo estiver correto, aparecerá no terminal:

```text
Uvicorn running on http://127.0.0.1:8000
```

### 6. Acessar a documentação

Abrir no navegador:

```text
http://127.0.0.1:8000/docs
```

A documentação Swagger permite testar todos os endpoints diretamente pelo navegador.

## Ordem sugerida para testar

Para testar o fluxo principal da aplicação, a ordem recomendada é:

1. Criar usuário
2. Criar unidade
3. Criar produto
4. Criar estoque
5. Criar pedido
6. Processar pagamento
7. Consultar fidelidade
8. Resgatar pontos
9. Consultar auditoria
10. Testar login JWT

## Exemplos de testes realizados

### Criar usuário

```json
{
  "nome": "Rafaela",
  "email": "rafaela@gmail.com",
  "senha": "123456",
  "perfil": "CLIENTE",
  "consentimento_lgpd": false
}
```

### Criar unidade

```json
{
  "nome": "Unidade Centro",
  "cidade": "Catalão",
  "estado": "GO",
  "endereco": "Rua Principal, 100",
  "ativa": true
}
```

### Criar produto

```json
{
  "unidade_id": 1,
  "nome": "X-Burger",
  "descricao": "Hambúrguer artesanal",
  "preco": 15.0,
  "categoria": "LANCHE",
  "ativo": true
}
```

### Criar estoque

```json
{
  "unidade_id": 1,
  "produto_id": 1,
  "quantidade": 50
}
```

### Criar pedido

```json
{
  "usuario_id": 1,
  "unidade_id": 1,
  "canalPedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2
    }
  ],
  "formaPagamento": "MOCK"
}
```

### Processar pagamento aprovado

```json
{
  "pedido_id": 1,
  "forma_pagamento": "MOCK",
  "status_pagamento": "APROVADO"
}
```

### Resgatar pontos

```json
{
  "usuario_id": 1,
  "pontos": 5
}
```

## Regras de negócio implementadas

- O e-mail do usuário não pode ser duplicado.
- A senha do usuário é salva com hash.
- O pedido deve possuir pelo menos um item.
- O canal do pedido deve ser válido.
- O produto precisa estar ativo para entrar em um pedido.
- A unidade precisa estar ativa para receber pedidos.
- O estoque precisa ser suficiente para criar o pedido.
- Ao criar pedido, o estoque é reduzido.
- Pedido sem pagamento não pode avançar para preparo ou entrega.
- Pagamento aprovado altera o pedido para pago.
- Pagamento recusado altera o pedido para pagamento recusado.
- Pagamento aprovado gera pontos de fidelidade.
- Resgate de pontos só é permitido se houver saldo suficiente.
- Ações importantes são registradas em auditoria.

## Segurança e LGPD

O projeto inclui alguns cuidados básicos de segurança:

- Senha armazenada com hash usando bcrypt.
- Login com token JWT.
- Campo de consentimento LGPD no cadastro do usuário.
- Não retorno da senha nas respostas da API.
- Registro de ações importantes por auditoria.

## Observações sobre o pagamento mock

O pagamento mock foi usado para simular o resultado de um pagamento sem integração com uma empresa real de pagamentos.

Neste projeto, ele aceita dois resultados:

- `APROVADO`
- `RECUSADO`

Isso permite testar o fluxo do pedido, atualização de status e geração de pontos sem depender de serviços externos.

## Status do projeto

Funcionalidades principais implementadas:

- API com FastAPI
- Banco PostgreSQL
- CRUD de usuários
- CRUD de unidades
- CRUD de produtos
- CRUD de estoque
- Criação e consulta de pedidos
- Pagamento mock
- Sistema de fidelidade
- Auditoria de ações
- Login com JWT
- Documentação pelo Swagger

## Autor

Projeto acadêmico desenvolvido por Hélio Gabriel para a atividade prática de Projeto de trilha Back-End.
