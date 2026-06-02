from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha = Column(String)
    perfil = Column(String, default="CLIENTE")
    consentimento_lgpd = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer)
    nome = Column(String)
    descricao = Column(String)
    preco = Column(Float)
    categoria = Column(String, default="GERAL")
    ativo = Column(Boolean, default=True)


class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer)
    produto_id = Column(Integer)
    quantidade = Column(Integer)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    unidade_id = Column(Integer)
    canalPedido = Column(String)
    status = Column(String)
    valor_total = Column(Float)
    formaPagamento = Column(String, default="MOCK")
    data_pedido = Column(DateTime, default=datetime.utcnow)


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer)
    produto_id = Column(Integer)
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    subtotal = Column(Float)

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer)
    forma_pagamento = Column(String)
    status_pagamento = Column(String)
    valor = Column(Float)
    data_pagamento = Column(DateTime, default=datetime.utcnow)

class Fidelidade(Base):
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    pontos = Column(Integer, default=0)
    data_atualizacao = Column(DateTime, default=datetime.utcnow)

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True)
    acao = Column(String)
    recurso = Column(String)
    detalhes = Column(String)
    data_registro = Column(DateTime, default=datetime.utcnow)

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cidade = Column(String)
    estado = Column(String)
    endereco = Column(String)
    ativa = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)