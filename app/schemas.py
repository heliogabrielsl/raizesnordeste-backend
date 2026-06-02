from typing import List
from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str = "CLIENTE"
    consentimento_lgpd: bool = False

class ProdutoCreate(BaseModel):
    unidade_id: int
    nome: str
    descricao: str
    preco: float
    categoria: str = "GERAL"
    ativo: bool = True

class EstoqueCreate(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    usuario_id: int
    unidade_id: int
    canalPedido: str
    itens: List[ItemPedidoCreate]
    formaPagamento: str = "MOCK"

class PedidoStatusUpdate(BaseModel):
    status: str

class PagamentoCreate(BaseModel):
    pedido_id: int
    forma_pagamento: str = "MOCK"
    status_pagamento: str

class FidelidadeResgate(BaseModel):
    usuario_id: int
    pontos: int

class UnidadeCreate(BaseModel):
    nome: str
    cidade: str
    estado: str
    endereco: str
    ativa: bool = True

class LoginCreate(BaseModel):
    email: str
    senha: str





