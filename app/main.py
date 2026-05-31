from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt

from .database import engine, SessionLocal
from .models import Base
from . import models, schemas


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Raízes",
    description="Gerenciamento de pedidos, produtos, estoque e pagamentos.",
    version="1.0.0"
)


# =========================
# CONSTANTES
# =========================

PERFIS_VALIDOS = {"CLIENTE", "ATENDENTE", "GERENTE", "ADMIN"}
CANAIS_VALIDOS = {"APP", "TOTEM", "BALCAO", "PICKUP", "WEB"}
FORMAS_PAGAMENTO_VALIDAS = {"MOCK"}
STATUS_PAGAMENTO_VALIDOS = {"APROVADO", "RECUSADO"}

STATUS_PEDIDO_VALIDOS = {
    "CRIADO",
    "AGUARDANDO_PAGAMENTO",
    "PAGO",
    "PAGAMENTO_RECUSADO",
    "EM_PREPARO",
    "PRONTO",
    "ENTREGUE",
    "CANCELADO"
}

STATUS_EXIGEM_PAGAMENTO = {"EM_PREPARO", "PRONTO", "ENTREGUE"}
STATUS_SEM_PAGAMENTO_CONFIRMADO = {"CRIADO", "AGUARDANDO_PAGAMENTO", "PAGAMENTO_RECUSADO"}
STATUS_PERMITIDOS_PAGAMENTO = {"CRIADO", "AGUARDANDO_PAGAMENTO", "PAGAMENTO_RECUSADO"}


# =========================
# BANCO DE DADOS
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# PADRÃO DE ERRO
# =========================

def agora():
    return datetime.utcnow()


def codigo_erro(status_code: int):
    codigos = {
        400: "REQUISICAO_INVALIDA",
        401: "NAO_AUTENTICADO",
        403: "SEM_PERMISSAO",
        404: "RECURSO_NAO_ENCONTRADO",
        409: "CONFLITO_REGRA_NEGOCIO",
        422: "DADOS_INVALIDOS",
        500: "ERRO_INTERNO"
    }

    return codigos.get(status_code, "ERRO_API")


@app.exception_handler(HTTPException)
async def tratar_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": codigo_erro(exc.status_code),
            "mensagem": exc.detail,
            "status": exc.status_code,
            "path": request.url.path,
            "timestamp": agora().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def tratar_validacao(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "erro": "DADOS_INVALIDOS",
            "mensagem": "Os dados enviados são inválidos.",
            "status": 422,
            "path": request.url.path,
            "timestamp": agora().isoformat(),
            "detalhes": exc.errors()
        })
    )


# =========================
# FUNÇÕES AUXILIARES
# =========================

def calcular_offset(page: int, limit: int):
    return (page - 1) * limit


def resposta_paginada(page: int, limit: int, dados: list):
    return {
        "page": page,
        "limit": limit,
        "dados": dados
    }


def normalizar(valor: str):
    return valor.strip().upper()


def validar_valor(valor: str, permitidos: set, mensagem: str):
    valor_normalizado = normalizar(valor)

    if valor_normalizado not in permitidos:
        raise HTTPException(
            status_code=400,
            detail=mensagem
        )

    return valor_normalizado


def validar_perfil(perfil: str):
    return validar_valor(
        perfil,
        PERFIS_VALIDOS,
        "Perfil inválido. Use CLIENTE, ATENDENTE, GERENTE ou ADMIN."
    )


def validar_canal(canal: str):
    return validar_valor(
        canal,
        CANAIS_VALIDOS,
        "Canal do pedido inválido"
    )


def validar_status_pedido(status_pedido: str):
    return validar_valor(
        status_pedido,
        STATUS_PEDIDO_VALIDOS,
        "Status inválido"
    )


def validar_forma_pagamento(forma_pagamento: str):
    return validar_valor(
        forma_pagamento,
        FORMAS_PAGAMENTO_VALIDAS,
        "Forma de pagamento inválida. Neste projeto, use MOCK."
    )


def validar_status_pagamento(status_pagamento: str):
    return validar_valor(
        status_pagamento,
        STATUS_PAGAMENTO_VALIDOS,
        "Status de pagamento inválido. Use APROVADO ou RECUSADO."
    )


def validar_unidade(unidade_id: int):
    if unidade_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="A unidade deve ser válida"
        )


def validar_preco(preco: float):
    if preco < 0:
        raise HTTPException(
            status_code=400,
            detail="O preço não pode ser negativo"
        )


def validar_quantidade(quantidade: int, mensagem: str):
    if quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail=mensagem
        )


# =========================
# RESPOSTAS
# =========================

def usuario_resposta(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "perfil": usuario.perfil,
        "consentimento_lgpd": usuario.consentimento_lgpd
    }


def produto_resposta(produto):
    return {
        "id": produto.id,
        "unidade_id": produto.unidade_id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco,
        "categoria": produto.categoria,
        "ativo": produto.ativo
    }


def estoque_resposta(estoque):
    return {
        "id": estoque.id,
        "unidade_id": estoque.unidade_id,
        "produto_id": estoque.produto_id,
        "quantidade": estoque.quantidade
    }


def item_pedido_resposta(item):
    return {
        "produto_id": item.produto_id,
        "quantidade": item.quantidade,
        "preco_unitario": item.preco_unitario,
        "subtotal": item.subtotal
    }


def pedido_resposta(pedido, itens=None):
    itens = itens or []

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "unidade_id": pedido.unidade_id,
        "canalPedido": pedido.canalPedido,
        "status": pedido.status,
        "valor_total": pedido.valor_total,
        "formaPagamento": pedido.formaPagamento,
        "itens": [item_pedido_resposta(item) for item in itens]
    }


def pagamento_resposta(pagamento):
    return {
        "id": pagamento.id,
        "pedido_id": pagamento.pedido_id,
        "forma_pagamento": pagamento.forma_pagamento,
        "status_pagamento": pagamento.status_pagamento,
        "valor": pagamento.valor,
        "data_pagamento": pagamento.data_pagamento
    }


# =========================
# BUSCAS NO BANCO
# =========================

def buscar_usuario_db(db, usuario_id: int):
    usuario = db.get(models.Usuario, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


def buscar_produto_db(db, produto_id: int):
    produto = db.get(models.Produto, produto_id)

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


def buscar_estoque_db(db, estoque_id: int):
    estoque = db.get(models.Estoque, estoque_id)

    if not estoque:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")

    return estoque


def buscar_pedido_db(db, pedido_id: int):
    pedido = db.get(models.Pedido, pedido_id)

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return pedido


def buscar_pagamento_db(db, pagamento_id: int):
    pagamento = db.get(models.Pagamento, pagamento_id)

    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")

    return pagamento


def buscar_itens_por_pedido(db, pedido_id: int):
    return db.query(models.ItemPedido).filter(
        models.ItemPedido.pedido_id == pedido_id
    ).all()


def agrupar_itens_por_pedido(db, pedidos):
    if not pedidos:
        return {}

    pedidos_ids = [pedido.id for pedido in pedidos]

    itens = db.query(models.ItemPedido).filter(
        models.ItemPedido.pedido_id.in_(pedidos_ids)
    ).all()

    itens_por_pedido = defaultdict(list)

    for item in itens:
        itens_por_pedido[item.pedido_id].append(item)

    return itens_por_pedido


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {"mensagem": "API Raízes em pleno funcionamento"}


# =========================
# USUÁRIOS
# =========================

@app.get("/usuarios", tags=["Usuários"], summary="Listar usuários")
def listar_usuarios(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    offset = calcular_offset(page, limit)

    usuarios = db.query(models.Usuario).offset(offset).limit(limit).all()
    dados = [usuario_resposta(usuario) for usuario in usuarios]

    return resposta_paginada(page, limit, dados)


@app.get("/usuarios/{usuario_id}", tags=["Usuários"], summary="Buscar usuário por ID")
def buscar_usuario(usuario_id: int, db=Depends(get_db)):
    usuario = buscar_usuario_db(db, usuario_id)

    return usuario_resposta(usuario)


@app.post("/usuarios", tags=["Usuários"], summary="Criar usuário", status_code=201)
def criar_usuario(usuario: schemas.UsuarioCreate, db=Depends(get_db)):
    perfil = validar_perfil(usuario.perfil)

    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=bcrypt.hash(usuario.senha),
        perfil=perfil,
        consentimento_lgpd=usuario.consentimento_lgpd
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário criado com sucesso",
        "usuario": usuario_resposta(novo_usuario)
    }


@app.put("/usuarios/{usuario_id}", tags=["Usuários"], summary="Atualizar usuário")
def atualizar_usuario(
    usuario_id: int,
    usuario: schemas.UsuarioCreate,
    db=Depends(get_db)
):
    usuario_db = buscar_usuario_db(db, usuario_id)
    perfil = validar_perfil(usuario.perfil)

    email_em_uso = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email,
        models.Usuario.id != usuario_id
    ).first()

    if email_em_uso:
        raise HTTPException(
            status_code=409,
            detail="E-mail já está sendo usado por outro usuário"
        )

    usuario_db.nome = usuario.nome
    usuario_db.email = usuario.email
    usuario_db.senha = bcrypt.hash(usuario.senha)
    usuario_db.perfil = perfil
    usuario_db.consentimento_lgpd = usuario.consentimento_lgpd

    db.commit()
    db.refresh(usuario_db)

    return {
        "mensagem": "Usuário atualizado com sucesso",
        "usuario": usuario_resposta(usuario_db)
    }


@app.delete("/usuarios/{usuario_id}", tags=["Usuários"], summary="Deletar usuário")
def deletar_usuario(usuario_id: int, db=Depends(get_db)):
    usuario = buscar_usuario_db(db, usuario_id)

    db.delete(usuario)
    db.commit()

    return {"mensagem": "Usuário deletado com sucesso"}


# =========================
# PRODUTOS
# =========================

@app.get("/produtos", tags=["Produtos"], summary="Listar produtos")
def listar_produtos(
    unidade_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    offset = calcular_offset(page, limit)
    consulta = db.query(models.Produto)

    if unidade_id is not None:
        consulta = consulta.filter(models.Produto.unidade_id == unidade_id)

    if ativo is not None:
        consulta = consulta.filter(models.Produto.ativo == ativo)

    produtos = consulta.offset(offset).limit(limit).all()
    dados = [produto_resposta(produto) for produto in produtos]

    return resposta_paginada(page, limit, dados)


@app.get("/produtos/{produto_id}", tags=["Produtos"], summary="Buscar produto por ID")
def buscar_produto(produto_id: int, db=Depends(get_db)):
    produto = buscar_produto_db(db, produto_id)

    return produto_resposta(produto)


@app.post("/produtos", tags=["Produtos"], summary="Criar produto", status_code=201)
def criar_produto(produto: schemas.ProdutoCreate, db=Depends(get_db)):
    validar_unidade(produto.unidade_id)
    validar_preco(produto.preco)

    novo_produto = models.Produto(
        unidade_id=produto.unidade_id,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        categoria=normalizar(produto.categoria),
        ativo=produto.ativo
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return {
        "mensagem": "Produto criado com sucesso",
        "produto": produto_resposta(novo_produto)
    }


@app.put("/produtos/{produto_id}", tags=["Produtos"], summary="Atualizar produto")
def atualizar_produto(
    produto_id: int,
    produto: schemas.ProdutoCreate,
    db=Depends(get_db)
):
    produto_db = buscar_produto_db(db, produto_id)

    validar_unidade(produto.unidade_id)
    validar_preco(produto.preco)

    produto_db.unidade_id = produto.unidade_id
    produto_db.nome = produto.nome
    produto_db.descricao = produto.descricao
    produto_db.preco = produto.preco
    produto_db.categoria = normalizar(produto.categoria)
    produto_db.ativo = produto.ativo

    db.commit()
    db.refresh(produto_db)

    return {
        "mensagem": "Produto atualizado com sucesso",
        "produto": produto_resposta(produto_db)
    }


@app.delete("/produtos/{produto_id}", tags=["Produtos"], summary="Deletar produto")
def deletar_produto(produto_id: int, db=Depends(get_db)):
    produto = buscar_produto_db(db, produto_id)

    db.delete(produto)
    db.commit()

    return {"mensagem": "Produto deletado com sucesso"}


# =========================
# ESTOQUE
# =========================

@app.get("/estoque", tags=["Estoque"], summary="Listar estoque")
def listar_estoque(
    unidade_id: Optional[int] = None,
    produto_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    offset = calcular_offset(page, limit)
    consulta = db.query(models.Estoque)

    if unidade_id is not None:
        consulta = consulta.filter(models.Estoque.unidade_id == unidade_id)

    if produto_id is not None:
        consulta = consulta.filter(models.Estoque.produto_id == produto_id)

    estoque = consulta.offset(offset).limit(limit).all()
    dados = [estoque_resposta(item) for item in estoque]

    return resposta_paginada(page, limit, dados)


@app.get("/estoque/{estoque_id}", tags=["Estoque"], summary="Buscar estoque por ID")
def buscar_estoque(estoque_id: int, db=Depends(get_db)):
    estoque = buscar_estoque_db(db, estoque_id)

    return estoque_resposta(estoque)


@app.post("/estoque", tags=["Estoque"], summary="Cadastrar estoque", status_code=201)
def criar_estoque(estoque: schemas.EstoqueCreate, db=Depends(get_db)):
    validar_unidade(estoque.unidade_id)
    buscar_produto_db(db, estoque.produto_id)

    if estoque.quantidade < 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade não pode ser negativa"
        )

    estoque_existente = db.query(models.Estoque).filter(
        models.Estoque.produto_id == estoque.produto_id,
        models.Estoque.unidade_id == estoque.unidade_id
    ).first()

    if estoque_existente:
        raise HTTPException(
            status_code=409,
            detail="Este produto já possui estoque cadastrado para esta unidade"
        )

    novo_estoque = models.Estoque(
        unidade_id=estoque.unidade_id,
        produto_id=estoque.produto_id,
        quantidade=estoque.quantidade,
        data_atualizacao=agora()
    )

    db.add(novo_estoque)
    db.commit()
    db.refresh(novo_estoque)

    return {
        "mensagem": "Estoque cadastrado com sucesso",
        "estoque": estoque_resposta(novo_estoque)
    }


@app.put("/estoque/{estoque_id}", tags=["Estoque"], summary="Atualizar estoque")
def atualizar_estoque(
    estoque_id: int,
    estoque: schemas.EstoqueCreate,
    db=Depends(get_db)
):
    estoque_db = buscar_estoque_db(db, estoque_id)

    validar_unidade(estoque.unidade_id)
    buscar_produto_db(db, estoque.produto_id)

    if estoque.quantidade < 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade não pode ser negativa"
        )

    estoque_duplicado = db.query(models.Estoque).filter(
        models.Estoque.produto_id == estoque.produto_id,
        models.Estoque.unidade_id == estoque.unidade_id,
        models.Estoque.id != estoque_id
    ).first()

    if estoque_duplicado:
        raise HTTPException(
            status_code=409,
            detail="Já existe estoque para este produto nesta unidade"
        )

    estoque_db.unidade_id = estoque.unidade_id
    estoque_db.produto_id = estoque.produto_id
    estoque_db.quantidade = estoque.quantidade
    estoque_db.data_atualizacao = agora()

    db.commit()
    db.refresh(estoque_db)

    return {
        "mensagem": "Estoque atualizado com sucesso",
        "estoque": estoque_resposta(estoque_db)
    }


@app.delete("/estoque/{estoque_id}", tags=["Estoque"], summary="Deletar estoque")
def deletar_estoque(estoque_id: int, db=Depends(get_db)):
    estoque = buscar_estoque_db(db, estoque_id)

    db.delete(estoque)
    db.commit()

    return {"mensagem": "Estoque deletado com sucesso"}


# =========================
# PEDIDOS
# =========================

@app.get("/pedidos", tags=["Pedidos"], summary="Listar pedidos")
def listar_pedidos(
    status: Optional[str] = None,
    canalPedido: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    offset = calcular_offset(page, limit)
    consulta = db.query(models.Pedido)

    if status is not None:
        status_normalizado = validar_status_pedido(status)
        consulta = consulta.filter(models.Pedido.status == status_normalizado)

    if canalPedido is not None:
        canal_normalizado = validar_canal(canalPedido)
        consulta = consulta.filter(models.Pedido.canalPedido == canal_normalizado)

    pedidos = consulta.offset(offset).limit(limit).all()
    itens_por_pedido = agrupar_itens_por_pedido(db, pedidos)

    dados = [
        pedido_resposta(pedido, itens_por_pedido.get(pedido.id, []))
        for pedido in pedidos
    ]

    return resposta_paginada(page, limit, dados)


@app.get("/pedidos/{pedido_id}", tags=["Pedidos"], summary="Buscar pedido por ID")
def buscar_pedido(pedido_id: int, db=Depends(get_db)):
    pedido = buscar_pedido_db(db, pedido_id)
    itens = buscar_itens_por_pedido(db, pedido.id)

    return pedido_resposta(pedido, itens)


@app.post("/pedidos", tags=["Pedidos"], summary="Criar pedido", status_code=201)
def criar_pedido(pedido: schemas.PedidoCreate, db=Depends(get_db)):
    buscar_usuario_db(db, pedido.usuario_id)
    validar_unidade(pedido.unidade_id)

    canal = validar_canal(pedido.canalPedido)
    forma_pagamento = validar_forma_pagamento(pedido.formaPagamento)

    if not pedido.itens:
        raise HTTPException(
            status_code=400,
            detail="O pedido deve possuir pelo menos um item"
        )

    quantidade_por_produto = defaultdict(int)

    for item in pedido.itens:
        validar_quantidade(
            item.quantidade,
            "A quantidade do item deve ser maior que zero"
        )
        quantidade_por_produto[item.produto_id] += item.quantidade

    produtos_ids = list(quantidade_por_produto.keys())

    produtos_lista = db.query(models.Produto).filter(
        models.Produto.id.in_(produtos_ids)
    ).all()

    produtos = {produto.id: produto for produto in produtos_lista}

    for produto_id in produtos_ids:
        if produto_id not in produtos:
            raise HTTPException(
                status_code=404,
                detail=f"Produto {produto_id} não encontrado"
            )

    estoques_lista = db.query(models.Estoque).filter(
        models.Estoque.produto_id.in_(produtos_ids),
        models.Estoque.unidade_id == pedido.unidade_id
    ).all()

    estoques = {estoque.produto_id: estoque for estoque in estoques_lista}

    valor_total = 0

    for produto_id, quantidade_total in quantidade_por_produto.items():
        produto = produtos[produto_id]

        if produto.ativo is False:
            raise HTTPException(
                status_code=409,
                detail=f"Produto {produto_id} está inativo e indisponível para pedido"
            )

        if produto.unidade_id is not None and produto.unidade_id != pedido.unidade_id:
            raise HTTPException(
                status_code=409,
                detail=f"Produto {produto_id} não pertence à unidade informada"
            )

        estoque = estoques.get(produto_id)

        if not estoque:
            raise HTTPException(
                status_code=404,
                detail=f"Estoque do produto {produto_id} não encontrado para esta unidade"
            )

        if estoque.quantidade < quantidade_total:
            raise HTTPException(
                status_code=409,
                detail=f"Estoque insuficiente para o produto {produto_id}"
            )

        valor_total += produto.preco * quantidade_total

    novo_pedido = models.Pedido(
        usuario_id=pedido.usuario_id,
        unidade_id=pedido.unidade_id,
        canalPedido=canal,
        status="AGUARDANDO_PAGAMENTO",
        valor_total=valor_total,
        formaPagamento=forma_pagamento,
        data_pedido=agora()
    )

    db.add(novo_pedido)
    db.flush()

    itens_criados = []

    for item in pedido.itens:
        produto = produtos[item.produto_id]
        estoque = estoques[item.produto_id]

        subtotal = produto.preco * item.quantidade

        item_pedido = models.ItemPedido(
            pedido_id=novo_pedido.id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal
        )

        estoque.quantidade -= item.quantidade
        estoque.data_atualizacao = agora()

        db.add(item_pedido)
        itens_criados.append(item_pedido)

    db.commit()
    db.refresh(novo_pedido)

    return {
        "mensagem": "Pedido criado com sucesso",
        "pedido": pedido_resposta(novo_pedido, itens_criados)
    }


@app.put("/pedidos/{pedido_id}/status", tags=["Pedidos"], summary="Atualizar status do pedido")
def atualizar_status_pedido(
    pedido_id: int,
    dados: schemas.PedidoStatusUpdate,
    db=Depends(get_db)
):
    pedido = buscar_pedido_db(db, pedido_id)
    novo_status = validar_status_pedido(dados.status)

    if novo_status in STATUS_EXIGEM_PAGAMENTO and pedido.status in STATUS_SEM_PAGAMENTO_CONFIRMADO:
        raise HTTPException(
            status_code=409,
            detail="O pedido só pode avançar após confirmação do pagamento"
        )

    itens = buscar_itens_por_pedido(db, pedido.id)

    if novo_status == "CANCELADO":
        if pedido.status == "ENTREGUE":
            raise HTTPException(
                status_code=409,
                detail="Pedido entregue não pode ser cancelado"
            )

        if pedido.status != "CANCELADO":
            produtos_ids = [item.produto_id for item in itens]

            estoques_lista = db.query(models.Estoque).filter(
                models.Estoque.produto_id.in_(produtos_ids),
                models.Estoque.unidade_id == pedido.unidade_id
            ).all()

            estoques = {estoque.produto_id: estoque for estoque in estoques_lista}

            for item in itens:
                estoque = estoques.get(item.produto_id)

                if estoque:
                    estoque.quantidade += item.quantidade
                    estoque.data_atualizacao = agora()

    pedido.status = novo_status

    db.commit()
    db.refresh(pedido)

    return {
        "mensagem": "Status do pedido atualizado com sucesso",
        "pedido": pedido_resposta(pedido, itens)
    }


# =========================
# PAGAMENTOS
# =========================

@app.get("/pagamentos", tags=["Pagamentos"], summary="Listar pagamentos")
def listar_pagamentos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    offset = calcular_offset(page, limit)

    pagamentos = db.query(models.Pagamento).offset(offset).limit(limit).all()
    dados = [pagamento_resposta(pagamento) for pagamento in pagamentos]

    return resposta_paginada(page, limit, dados)


@app.get("/pagamentos/{pagamento_id}", tags=["Pagamentos"], summary="Buscar pagamento por ID")
def buscar_pagamento(pagamento_id: int, db=Depends(get_db)):
    pagamento = buscar_pagamento_db(db, pagamento_id)

    return pagamento_resposta(pagamento)


@app.post("/pagamentos", tags=["Pagamentos"], summary="Processar pagamento mock", status_code=201)
def processar_pagamento(pagamento: schemas.PagamentoCreate, db=Depends(get_db)):
    pedido = buscar_pedido_db(db, pagamento.pedido_id)

    forma_pagamento = validar_forma_pagamento(pagamento.forma_pagamento)
    status_pagamento = validar_status_pagamento(pagamento.status_pagamento)

    if pedido.status not in STATUS_PERMITIDOS_PAGAMENTO:
        raise HTTPException(
            status_code=409,
            detail="Este pedido não está disponível para pagamento"
        )

    novo_pagamento = models.Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=forma_pagamento,
        status_pagamento=status_pagamento,
        valor=pedido.valor_total,
        data_pagamento=agora()
    )

    if status_pagamento == "APROVADO":
        pedido.status = "PAGO"
        mensagem = "Pagamento aprovado com sucesso"
    else:
        pedido.status = "PAGAMENTO_RECUSADO"
        mensagem = "Pagamento recusado"

    db.add(novo_pagamento)
    db.commit()
    db.refresh(novo_pagamento)
    db.refresh(pedido)

    itens = buscar_itens_por_pedido(db, pedido.id)

    return {
        "mensagem": mensagem,
        "pagamento": pagamento_resposta(novo_pagamento),
        "pedido": pedido_resposta(pedido, itens)
    }