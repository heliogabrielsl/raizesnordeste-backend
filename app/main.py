from fastapi import FastAPI

from .database import engine, SessionLocal
from .models import Base
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Raízes",
    description="Gerenciamento de pedidos, estoque e pagamentos.",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"mensagem": "API Raízes em pleno funcionamento"}


@app.get(
    "/usuarios",
    tags=["Usuários"],
    summary="Listar usuários"
)
def listar_usuarios():

    db = SessionLocal()

    usuarios = db.query(models.Usuario).all()

    return usuarios


@app.get(
    "/usuarios/{usuario_id}",
    tags=["Usuários"],
    summary="Buscar usuário por ID"
)
def buscar_usuario(usuario_id: int):

    db = SessionLocal()

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

    if not usuario:
        return {"erro": "Usuário não encontrado"}

    return usuario


@app.post(
    "/usuarios",
    tags=["Usuários"],
    summary="Criar usuário"
)
def criar_usuario(usuario: schemas.UsuarioCreate):

    db = SessionLocal()

    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=usuario.senha
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return {
        "mensagem": "Sucesso ao criar usuário",
        "usuario": {
            "id": novo_usuario.id,
            "nome": novo_usuario.nome,
            "email": novo_usuario.email
        }
    }


@app.put(
    "/usuarios/{usuario_id}",
    tags=["Usuários"],
    summary="Atualizar usuário"
)
def atualizar_usuario(usuario_id: int, usuario: schemas.UsuarioCreate):

    db = SessionLocal()

    usuario_db = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

    if not usuario_db:
        return {"erro": "Usuário não encontrado"}

    usuario_db.nome = usuario.nome
    usuario_db.email = usuario.email
    usuario_db.senha = usuario.senha

    db.commit()
    db.refresh(usuario_db)

    return {
        "mensagem": "Usuário atualizado com sucesso",
        "usuario": usuario_db
    }
@app.delete(
    "/usuarios/{usuario_id}",
    tags=["Usuários"],
    summary="Deletar usuário"
)
def deletar_usuario(usuario_id: int):

    db = SessionLocal()

    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == usuario_id
    ).first()

    if not usuario:
        return {"erro": "Usuário não encontrado"}

    db.delete(usuario)
    db.commit()

    return {
        "mensagem": "Usuário deletado com sucesso"
    }