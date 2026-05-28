from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    preco: float

class EstoqueCreate(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    usuario_id: int
    produto_id: int
    quantidade: int
    canalPedido: str

class PedidoStatusUpdate(BaseModel):
    status: str