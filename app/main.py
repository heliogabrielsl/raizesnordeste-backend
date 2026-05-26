from fastapi import FastAPI

app = FastAPI(
    title="API Raízes",
    description="Gerenciamento de pedidos, produtos, estoque e pagamentos.",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"mensagem": "API Raízes do Nordeste funcionando"}