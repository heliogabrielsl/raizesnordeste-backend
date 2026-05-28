from fastapi import Depends, FastAPI, HTTPException
from passlib.hash import bcrypt

from .database import engine, SessionLocal
from .models import Base
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Raízes",
    description="Gerenciamento de pedidos, estoque e pagamentos.",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def usuario_resposta(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email
    }


def produto_resposta(produto):
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco
    }


def estoque_resposta(estoque):
    return {
        "id": estoque.id,
        "produto_id": estoque.produto_id,
        "quantidade": estoque.quantidade
    }


def buscar_usuario_db(db, usuario_id: int):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


def buscar_produto_db(db, produto_id: int):
    produto = db.query(models.Produto).filter(
        models.Produto.id == produto_id
    ).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


def buscar_estoque_db(db, estoque_id: int):
    estoque = db.query(models.Estoque).filter(
        models.Estoque.id == estoque_id
    ).first()

    if not estoque:
        raise HTTPException(status_code=404, detail="Estoque não encontrado")

    return estoque


def buscar_pedido_db(db, pedido_id: int):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return pedido


def pedido_resposta(db, pedido):
    itens = db.query(models.ItemPedido).filter(
        models.ItemPedido.pedido_id == pedido.id
    ).all()

    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "status": pedido.status,
        "valor_total": pedido.valor_total,
        "canalPedido": pedido.canalPedido,
        "itens": [
            {
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario
            }
            for item in itens
        ]
    }


@app.get("/")
def home():
    return {"mensagem": "API Raízes em pleno funcionamento"}


# =========================
# USUÁRIOS
# =========================

@app.get("/usuarios", tags=["Usuários"], summary="Listar usuários")
def listar_usuarios(db=Depends(get_db)):
    usuarios = db.query(models.Usuario).all()

    return [usuario_resposta(usuario) for usuario in usuarios]


@app.get("/usuarios/{usuario_id}", tags=["Usuários"], summary="Buscar usuário por ID")
def buscar_usuario(usuario_id: int, db=Depends(get_db)):
    usuario = buscar_usuario_db(db, usuario_id)

    return usuario_resposta(usuario)


@app.post("/usuarios", tags=["Usuários"], summary="Criar usuário")
def criar_usuario(usuario: schemas.UsuarioCreate, db=Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email
    ).first()

    if usuario_existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=bcrypt.hash(usuario.senha)
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Usuário criado com sucesso",
        "usuario": usuario_resposta(novo_usuario)
    }


@app.put("/usuarios/{usuario_id}", tags=["Usuários"], summary="Atualizar usuário")
def atualizar_usuario(usuario_id: int, usuario: schemas.UsuarioCreate, db=Depends(get_db)):
    usuario_db = buscar_usuario_db(db, usuario_id)

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
def listar_produtos(db=Depends(get_db)):
    produtos = db.query(models.Produto).all()

    return [produto_resposta(produto) for produto in produtos]


@app.get("/produtos/{produto_id}", tags=["Produtos"], summary="Buscar produto por ID")
def buscar_produto(produto_id: int, db=Depends(get_db)):
    produto = buscar_produto_db(db, produto_id)

    return produto_resposta(produto)


@app.post("/produtos", tags=["Produtos"], summary="Criar produto")
def criar_produto(produto: schemas.ProdutoCreate, db=Depends(get_db)):
    if produto.preco < 0:
        raise HTTPException(status_code=400, detail="O preço não pode ser negativo")

    novo_produto = models.Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)

    return {
        "mensagem": "Produto criado com sucesso",
        "produto": produto_resposta(novo_produto)
    }


@app.put("/produtos/{produto_id}", tags=["Produtos"], summary="Atualizar produto")
def atualizar_produto(produto_id: int, produto: schemas.ProdutoCreate, db=Depends(get_db)):
    produto_db = buscar_produto_db(db, produto_id)

    if produto.preco < 0:
        raise HTTPException(status_code=400, detail="O preço não pode ser negativo")

    produto_db.nome = produto.nome
    produto_db.descricao = produto.descricao
    produto_db.preco = produto.preco

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
def listar_estoque(db=Depends(get_db)):
    estoque = db.query(models.Estoque).all()

    return [estoque_resposta(item) for item in estoque]


@app.get("/estoque/{estoque_id}", tags=["Estoque"], summary="Buscar estoque por ID")
def buscar_estoque(estoque_id: int, db=Depends(get_db)):
    estoque = buscar_estoque_db(db, estoque_id)

    return estoque_resposta(estoque)


@app.post("/estoque", tags=["Estoque"], summary="Cadastrar estoque")
def criar_estoque(estoque: schemas.EstoqueCreate, db=Depends(get_db)):
    buscar_produto_db(db, estoque.produto_id)

    if estoque.quantidade < 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade não pode ser negativa"
        )

    estoque_existente = db.query(models.Estoque).filter(
        models.Estoque.produto_id == estoque.produto_id
    ).first()

    if estoque_existente:
        raise HTTPException(
            status_code=409,
            detail="Este produto já possui estoque cadastrado"
        )

    novo_estoque = models.Estoque(
        produto_id=estoque.produto_id,
        quantidade=estoque.quantidade
    )

    db.add(novo_estoque)
    db.commit()
    db.refresh(novo_estoque)

    return {
        "mensagem": "Estoque cadastrado com sucesso",
        "estoque": estoque_resposta(novo_estoque)
    }


@app.put("/estoque/{estoque_id}", tags=["Estoque"], summary="Atualizar estoque")
def atualizar_estoque(estoque_id: int, estoque: schemas.EstoqueCreate, db=Depends(get_db)):
    estoque_db = buscar_estoque_db(db, estoque_id)

    buscar_produto_db(db, estoque.produto_id)

    if estoque.quantidade < 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade não pode ser negativa"
        )

    estoque_db.produto_id = estoque.produto_id
    estoque_db.quantidade = estoque.quantidade

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
def listar_pedidos(db=Depends(get_db)):
    pedidos = db.query(models.Pedido).all()

    return [pedido_resposta(db, pedido) for pedido in pedidos]


@app.get("/pedidos/{pedido_id}", tags=["Pedidos"], summary="Buscar pedido por ID")
def buscar_pedido(pedido_id: int, db=Depends(get_db)):
    pedido = buscar_pedido_db(db, pedido_id)

    return pedido_resposta(db, pedido)


@app.post("/pedidos", tags=["Pedidos"], summary="Criar pedido")
def criar_pedido(pedido: schemas.PedidoCreate, db=Depends(get_db)):
    buscar_usuario_db(db, pedido.usuario_id)

    produto = buscar_produto_db(db, pedido.produto_id)

    estoque = db.query(models.Estoque).filter(
        models.Estoque.produto_id == pedido.produto_id
    ).first()

    if not estoque:
        raise HTTPException(
            status_code=404,
            detail="Estoque do produto não encontrado"
        )

    if pedido.quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade deve ser maior que zero"
        )

    if estoque.quantidade < pedido.quantidade:
        raise HTTPException(
            status_code=400,
            detail="Estoque insuficiente para realizar o pedido"
        )

    canais_validos = ["APP", "TOTEM", "BALCAO", "PICKUP", "WEB"]

    canal = pedido.canalPedido.upper()

    if canal not in canais_validos:
        raise HTTPException(
            status_code=400,
            detail="Canal do pedido inválido"
        )

    valor_total = produto.preco * pedido.quantidade

    novo_pedido = models.Pedido(
        usuario_id=pedido.usuario_id,
        status="CRIADO",
        valor_total=valor_total,
        canalPedido=canal
    )

    db.add(novo_pedido)
    db.flush()

    item_pedido = models.ItemPedido(
        pedido_id=novo_pedido.id,
        produto_id=pedido.produto_id,
        quantidade=pedido.quantidade,
        preco_unitario=produto.preco
    )

    estoque.quantidade -= pedido.quantidade

    db.add(item_pedido)
    db.commit()
    db.refresh(novo_pedido)
    db.refresh(item_pedido)

    return {
        "mensagem": "Pedido criado com sucesso",
        "pedido": {
            "id": novo_pedido.id,
            "usuario_id": novo_pedido.usuario_id,
            "status": novo_pedido.status,
            "valor_total": novo_pedido.valor_total,
            "canalPedido": novo_pedido.canalPedido,
            "item": {
                "produto_id": item_pedido.produto_id,
                "quantidade": item_pedido.quantidade,
                "preco_unitario": item_pedido.preco_unitario
            }
        }
    }


@app.put("/pedidos/{pedido_id}/status", tags=["Pedidos"], summary="Atualizar status do pedido")
def atualizar_status_pedido(pedido_id: int, dados: schemas.PedidoStatusUpdate, db=Depends(get_db)):
    pedido = buscar_pedido_db(db, pedido_id)

    status_validos = ["CRIADO", "PAGO", "RECUSADO", "CANCELADO", "ENTREGUE"]

    novo_status = dados.status.upper()

    if novo_status not in status_validos:
        raise HTTPException(
            status_code=400,
            detail="Status inválido"
        )

    pedido.status = novo_status

    db.commit()
    db.refresh(pedido)

    return {
        "mensagem": "Status do pedido atualizado com sucesso",
        "pedido": {
            "id": pedido.id,
            "status": pedido.status,
            "valor_total": pedido.valor_total,
            "canalPedido": pedido.canalPedido
        }
    }