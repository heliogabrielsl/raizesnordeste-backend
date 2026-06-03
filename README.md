# API Raízes do Nordeste

Projeto desenvolvido para a atividade prática do Projeto Multidisciplinar – Trilha Back-End.

A proposta do projeto é criar uma API para uma rede de lanchonetes com controle de usuários, unidades, produtos, estoque, pedidos, pagamentos mock, fidelidade e auditoria.

O sistema foi desenvolvido em Python utilizando FastAPI, PostgreSQL, SQLAlchemy, Pydantic, JWT e documentação automática via Swagger/OpenAPI.

---

## Objetivo do projeto

O objetivo da API é simular o funcionamento básico de um sistema back-end para uma rede de lanchonetes que atende por diferentes canais, como aplicativo, totem, balcão, retirada e web.

A aplicação permite:

- Cadastrar usuários;
- Autenticar usuários com JWT;
- Controlar permissões por perfil;
- Cadastrar unidades;
- Cadastrar produtos;
- Controlar estoque;
- Criar pedidos;
- Processar pagamento mock;
- Gerar pontos de fidelidade;
- Registrar ações importantes em auditoria;
- Retornar erros em formato JSON padronizado.

---

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
- Insomnia
- Git e GitHub

---

## Estrutura do projeto

```text
raizesnordeste-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── database.py
│
├── requirements.txt
├── .env
├── .gitignore
├── raizes-api-testes.json
└── README.md
```

---

## Funcionalidades implementadas

### Autenticação

A API possui autenticação com JWT.

Endpoints:

```http
POST /auth/login
GET /auth/me
```

O endpoint de login valida e-mail e senha. Caso os dados estejam corretos, a API retorna um token JWT.

Exemplo de login:

```json
{
  "email": "sofia@gmail.com",
  "senha": "123456"
}
```

Exemplo de resposta:

```json
{
  "access_token": "token_jwt_gerado",
  "token_type": "bearer",
  "usuario": {
    "id": 17,
    "nome": "Sofia",
    "email": "sofia@gmail.com",
    "perfil": "CLIENTE",
    "consentimento_lgpd": true
  }
}
```

---

### Usuários

O sistema permite cadastrar, listar, consultar, atualizar e deletar usuários.

Endpoints:

```http
GET /usuarios
POST /usuarios
GET /usuarios/{usuario_id}
PUT /usuarios/{usuario_id}
DELETE /usuarios/{usuario_id}
```

Funcionalidades:

- Cadastro de usuário;
- Login com e-mail e senha;
- Senha armazenada com hash;
- Validação de e-mail duplicado;
- Controle de perfil;
- Consentimento LGPD;
- Retorno dos dados sem expor a senha.

Perfis disponíveis:

```text
CLIENTE
ATENDENTE
GERENTE
ADMIN
```

Exemplo de criação de usuário:

```json
{
  "nome": "Sofia",
  "email": "sofia@gmail.com",
  "senha": "123456",
  "perfil": "CLIENTE",
  "consentimento_lgpd": true
}
```

---

### Controle de permissões

A API possui controle de permissões por perfil.

Perfis existentes:

| Perfil | Permissões principais |
|---|---|
| `CLIENTE` | Pode criar pedidos e consultar seus próprios dados/pedidos |
| `ATENDENTE` | Pode consultar e atualizar pedidos e processar pagamentos |
| `GERENTE` | Pode gerenciar unidades, produtos, estoque, pedidos, pagamentos, fidelidade e auditoria |
| `ADMIN` | Possui acesso administrativo completo |

Quando um usuário tenta acessar uma funcionalidade sem permissão, a API retorna erro `403`.

Exemplo:

```json
{
  "erro": "SEM_PERMISSAO",
  "mensagem": "Usuário sem permissão para realizar esta operação",
  "status": 403,
  "path": "/auditoria",
  "timestamp": "2026-06-03T21:30:00"
}
```

---

### Criação do primeiro administrador

Quando o banco de dados está vazio, o primeiro usuário pode ser criado com qualquer perfil, inclusive `ADMIN`.

Exemplo:

```json
{
  "nome": "Administrador",
  "email": "admin@gmail.com",
  "senha": "123456",
  "perfil": "ADMIN",
  "consentimento_lgpd": true
}
```

Após existir pelo menos um usuário no banco, o cadastro público permite apenas usuários com perfil `CLIENTE`.

Caso seja necessário promover um usuário para `ADMIN` em ambiente de teste, pode ser utilizado o comando SQL abaixo no pgAdmin:

```sql
UPDATE usuarios
SET perfil = 'ADMIN'
WHERE email = 'admin@gmail.com';
```

Depois, confirme a alteração:

```sql
SELECT id, nome, email, perfil
FROM usuarios
ORDER BY id ASC;
```

---

### Unidades

O sistema permite cadastrar e gerenciar unidades da rede.

Endpoints:

```http
GET /unidades
POST /unidades
GET /unidades/{unidade_id}
PUT /unidades/{unidade_id}
DELETE /unidades/{unidade_id}
```

Exemplo de criação de unidade:

```json
{
  "nome": "Raízes",
  "cidade": "João Pessoa",
  "estado": "PB",
  "endereco": "Rua Principal, 100",
  "ativa": true
}
```

O endpoint de exclusão funciona como desativação lógica da unidade, mantendo o histórico no banco.

---

### Produtos

O sistema permite cadastrar produtos vinculados a uma unidade.

Endpoints:

```http
GET /produtos
POST /produtos
GET /produtos/{produto_id}
PUT /produtos/{produto_id}
DELETE /produtos/{produto_id}
```

Exemplo de criação de produto:

```json
{
  "unidade_id": 1,
  "nome": "Cuzcuz",
  "descricao": "Cuzcuz Nordestino",
  "preco": 15.0,
  "categoria": "GERAL",
  "ativo": true
}
```

---

### Estoque

O estoque controla a quantidade disponível de cada produto em uma unidade.

Endpoints:

```http
GET /estoque
POST /estoque
GET /estoque/{estoque_id}
PUT /estoque/{estoque_id}
DELETE /estoque/{estoque_id}
```

Exemplo de cadastro de estoque:

```json
{
  "unidade_id": 1,
  "produto_id": 1,
  "quantidade": 100
}
```

Regras aplicadas:

- A quantidade não pode ser negativa;
- Não pode existir estoque duplicado para o mesmo produto na mesma unidade;
- O estoque é reduzido automaticamente ao criar um pedido.

---

### Pedidos

O pedido pode conter um ou mais itens.

Endpoints:

```http
GET /pedidos
POST /pedidos
GET /pedidos/{pedido_id}
PUT /pedidos/{pedido_id}/status
```

Canais de pedido aceitos:

```text
APP
TOTEM
BALCAO
PICKUP
WEB
```

Exemplo de criação de pedido:

```json
{
  "usuario_id": 17,
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

Ao criar um pedido, a API:

- Verifica se o usuário existe;
- Verifica se a unidade existe e está ativa;
- Verifica se o produto existe;
- Verifica se o produto pertence à unidade informada;
- Verifica se existe estoque suficiente;
- Calcula o valor total;
- Reduz a quantidade do estoque;
- Cria o pedido com status `AGUARDANDO_PAGAMENTO`;
- Registra a ação em auditoria.

Status disponíveis para pedido:

```text
CRIADO
AGUARDANDO_PAGAMENTO
PAGO
PAGAMENTO_RECUSADO
EM_PREPARO
PRONTO
ENTREGUE
CANCELADO
```

---

### Pagamentos

Foi implementado pagamento mock para simular aprovação ou recusa de pagamento.

Endpoints:

```http
GET /pagamentos
POST /pagamentos
GET /pagamentos/{pagamento_id}
```

Exemplo de pagamento aprovado:

```json
{
  "pedido_id": 6,
  "forma_pagamento": "MOCK",
  "status_pagamento": "APROVADO"
}
```

Status aceitos:

```text
APROVADO
RECUSADO
```

Quando o pagamento é aprovado:

- O pagamento é registrado;
- O pedido é alterado para `PAGO`;
- São gerados pontos de fidelidade;
- A ação é registrada na auditoria.

Quando o pagamento é recusado:

- O pagamento é registrado;
- O pedido é alterado para `PAGAMENTO_RECUSADO`;
- A ação é registrada na auditoria.

---

### Fidelidade

O sistema possui controle de pontos de fidelidade.

Endpoints:

```http
GET /fidelidade/{usuario_id}
POST /fidelidade/resgatar
```

Exemplo de resgate:

```json
{
  "usuario_id": 17,
  "pontos": 10
}
```

Regras aplicadas:

- O usuário precisa existir;
- A quantidade de pontos para resgate deve ser maior que zero;
- O usuário precisa possuir saldo suficiente;
- O resgate gera registro de auditoria.

---

### Auditoria

A auditoria registra ações importantes realizadas na API.

Endpoint:

```http
GET /auditoria
```

Ações registradas:

```text
LOGIN_REALIZADO
USUARIO_CRIADO
USUARIO_ATUALIZADO
USUARIO_DELETADO
UNIDADE_CRIADA
UNIDADE_ATUALIZADA
UNIDADE_DESATIVADA
PRODUTO_CRIADO
PRODUTO_ATUALIZADO
PRODUTO_DELETADO
ESTOQUE_CRIADO
ESTOQUE_ATUALIZADO
ESTOQUE_DELETADO
PEDIDO_CRIADO
STATUS_PEDIDO_ALTERADO
PAGAMENTO_APROVADO
PAGAMENTO_RECUSADO
PONTOS_RESGATADOS
```

Exemplo de retorno:

```json
{
  "page": 1,
  "limit": 10,
  "dados": [
    {
      "id": 1,
      "usuario_id": 17,
      "acao": "PEDIDO_CRIADO",
      "recurso": "pedidos",
      "detalhes": "Pedido 6 criado no canal APP com valor total 30.0",
      "data_registro": "2026-06-03T21:30:00"
    }
  ]
}
```

---

## Padrão de erro

A API retorna erros em formato JSON padronizado.

Exemplo:

```json
{
  "erro": "CONFLITO_REGRA_NEGOCIO",
  "mensagem": "E-mail já cadastrado",
  "status": 409,
  "path": "/usuarios",
  "timestamp": "2026-06-03T21:26:40"
}
```

Principais códigos tratados:

| Código | Significado |
|---|---|
| `400` | Requisição inválida |
| `401` | Não autenticado |
| `403` | Sem permissão |
| `404` | Recurso não encontrado |
| `409` | Conflito de regra de negócio |
| `422` | Dados inválidos |
| `500` | Erro interno |

---

## Como executar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/heliogabrielsl/raizesnordeste-backend.git
```

Entrar na pasta:

```bash
cd raizesnordeste-backend
```

---

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

Ativar no Windows:

```bash
venv\Scripts\activate
```

---

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

---

### 4. Configurar o banco de dados

Criar um arquivo `.env` na raiz do projeto com a variável `DATABASE_URL`.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/raizes_db
```

O banco utilizado no projeto foi:

```text
raizes_db
```

---

### 5. Executar a API

```bash
uvicorn app.main:app --reload
```

Se estiver tudo correto, o terminal exibirá:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

### 6. Acessar a documentação Swagger

Abrir no navegador:

```text
http://127.0.0.1:8000/docs
```

A documentação Swagger permite visualizar e testar todos os endpoints da API.

---

## Ordem recomendada para preparar o ambiente de testes

Antes de executar a coleção principal do Insomnia, é necessário garantir que existam registros básicos no banco.

Ordem de preparação:

```text
1. Criar ou garantir um usuário ADMIN, GERENTE ou ATENDENTE para operações protegidas.
2. Fazer login e copiar o token JWT.
3. Criar uma unidade.
4. Criar um produto vinculado à unidade.
5. Criar estoque para o produto.
```

Exemplo de dados utilizados durante os testes realizados:

```text
Unidade: id 1
Produto: id 1
Estoque: 100 unidades
Usuário testado: Sofia
Pedido testado: id 6
```

Caso os IDs sejam diferentes em outro banco, basta ajustar os valores no corpo das requisições do Insomnia.

---

## Coleção de testes no Insomnia

A API foi validada com uma coleção do Insomnia exportada no formato JSON.

Arquivo:

```text
raizes-api-testes.json
```

A coleção contém 10 cenários de teste, sendo 6 positivos e 4 negativos.

Os testes validam:

- Autenticação;
- Consulta de usuário autenticado;
- Criação de usuário;
- Criação de pedido;
- Pagamento mock;
- Consulta de pedido;
- Login inválido;
- Acesso sem token;
- Usuário duplicado;
- Estoque insuficiente.

---

## Ordem correta de execução dos testes

A ordem correta usada na validação foi:

```text
T03 - Criar usuário válido
T01 - Login válido
T02 - Consultar usuário autenticado
T04 - Criar pedido válido
T05 - Pagamento aprovado
T06 - Consultar pedido existente
T07 - Login inválido
T08 - Acesso sem token
T09 - Usuário duplicado
T10 - Estoque insuficiente
```

Essa sequência foi utilizada porque alguns testes dependem de dados criados nos testes anteriores.

---

## Cenários de teste executados

| ID | Cenário | Endpoint | Pré-condição | Entrada | Saída esperada | Evidência |
|---|---|---|---|---|---|---|
| T03 | Criar usuário válido | `POST /usuarios` | E-mail ainda não cadastrado | Dados válidos do usuário | `201 Created` + usuário criado | T03 - Criar usuário válido |
| T01 | Login válido | `POST /auth/login` | Usuário cadastrado | E-mail e senha válidos | `200 OK` + access_token | T01 - Login válido |
| T02 | Consultar usuário autenticado | `GET /auth/me` | Token JWT válido | Bearer Token | `200 OK` + dados do usuário | T02 - Consultar usuário autenticado |
| T04 | Criar pedido válido | `POST /pedidos` | Usuário, unidade, produto e estoque existentes | Pedido com quantidade válida | `201 Created` + pedido criado | T04 - Criar pedido válido |
| T05 | Pagamento aprovado | `POST /pagamentos` | Pedido em `AGUARDANDO_PAGAMENTO` | Pagamento `APROVADO` | `201 Created` + pedido `PAGO` | T05 - Pagamento aprovado |
| T06 | Consultar pedido existente | `GET /pedidos/{id}` | Pedido existente | ID do pedido | `200 OK` + dados do pedido | T06 - Consultar pedido existente |
| T07 | Login inválido | `POST /auth/login` | Usuário cadastrado | Senha incorreta | `401 Unauthorized` + erro de autenticação | T07 - Login inválido |
| T08 | Acesso sem token | `GET /auth/me` | Nenhuma | Sem Authorization | `401 Unauthorized` + token não informado | T08 - Acesso sem token |
| T09 | Usuário duplicado | `POST /usuarios` | E-mail já cadastrado | Mesmo e-mail do usuário existente | `409 Conflict` + e-mail já cadastrado | T09 - Usuário duplicado |
| T10 | Estoque insuficiente | `POST /pedidos` | Produto com estoque menor que a quantidade solicitada | Quantidade maior que o estoque | `409 Conflict` + estoque insuficiente | T10 - Estoque insuficiente |

---

## Exemplos dos corpos usados nos testes

### T03 - Criar usuário válido

```json
{
  "nome": "Sofia",
  "email": "sofia@gmail.com",
  "senha": "123456",
  "perfil": "CLIENTE",
  "consentimento_lgpd": true
}
```

---

### T01 - Login válido

```json
{
  "email": "sofia@gmail.com",
  "senha": "123456"
}
```

---

### T07 - Login inválido

```json
{
  "email": "sofia@gmail.com",
  "senha": "senha_errada"
}
```

---

### T04 - Criar pedido válido

```json
{
  "usuario_id": 17,
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

---

### T05 - Pagamento aprovado

```json
{
  "pedido_id": 6,
  "forma_pagamento": "MOCK",
  "status_pagamento": "APROVADO"
}
```

---

### T10 - Estoque insuficiente

```json
{
  "usuario_id": 17,
  "unidade_id": 1,
  "canalPedido": "APP",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 999
    }
  ],
  "formaPagamento": "MOCK"
}
```

---

## Como importar a coleção no Insomnia

1. Abrir o Insomnia.
2. Clicar em **Import**.
3. Selecionar o arquivo:

```text
raizes-api-testes.json
```

4. Importar a coleção.
5. Conferir se a API está rodando em:

```text
http://127.0.0.1:8000
```

6. Executar os testes na ordem indicada neste README.

---

## Regras de negócio implementadas

- O e-mail do usuário não pode ser duplicado.
- A senha do usuário é armazenada com hash.
- O cadastro público permite apenas usuários `CLIENTE` após existir ao menos um usuário no banco.
- O token JWT é exigido para endpoints protegidos.
- Perfis sem permissão recebem erro `403`.
- O pedido deve possuir pelo menos um item.
- O canal do pedido deve ser válido.
- A forma de pagamento aceita no projeto é `MOCK`.
- O produto precisa estar ativo para entrar em um pedido.
- A unidade precisa estar ativa para receber pedidos.
- O estoque precisa ser suficiente para criar o pedido.
- Ao criar um pedido, o estoque é reduzido automaticamente.
- Pedido sem pagamento confirmado não pode avançar para preparo, pronto ou entregue.
- Pagamento aprovado altera o pedido para `PAGO`.
- Pagamento recusado altera o pedido para `PAGAMENTO_RECUSADO`.
- Pagamento aprovado gera pontos de fidelidade.
- Resgate de pontos só é permitido quando há saldo suficiente.
- Ações importantes são registradas em auditoria.

---

## Segurança e LGPD

O projeto inclui cuidados básicos de segurança e privacidade:

- Senhas armazenadas com hash usando bcrypt;
- Login com token JWT;
- Campo de consentimento LGPD no cadastro do usuário;
- A senha não é retornada nas respostas da API;
- Controle de acesso por perfil;
- Bloqueio de endpoints administrativos para usuários sem permissão;
- Registro de ações importantes em auditoria.

---

## Observações sobre o pagamento mock

O pagamento mock foi utilizado para simular o resultado de um pagamento sem integração com serviços externos.

Neste projeto, ele aceita dois resultados:

```text
APROVADO
RECUSADO
```

Isso permite testar o fluxo do pedido, a atualização de status e a geração de pontos de fidelidade sem depender de uma operadora de pagamento real.

---

## Status do projeto

Funcionalidades principais implementadas:

- API com FastAPI;
- Banco PostgreSQL;
- CRUD de usuários;
- CRUD de unidades;
- CRUD de produtos;
- CRUD de estoque;
- Criação e consulta de pedidos;
- Atualização de status de pedidos;
- Pagamento mock;
- Sistema de fidelidade;
- Auditoria de ações;
- Login com JWT;
- Controle de permissões por perfil;
- Documentação automática pelo Swagger;
- Coleção de testes do Insomnia.

---

## Autor

Projeto acadêmico desenvolvido por Hélio Gabriel para a atividade prática de Projeto Multidisciplinar – Trilha Back-End.
