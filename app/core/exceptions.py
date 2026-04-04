from fastapi import Request, status
from fastapi.responses import JSONResponse

class EntidadeNaoEncontradaException(Exception):
    def __init__(self, entidade: str, id_ou_parametro: str | int):
        self.entidade = entidade
        self.id_ou_parametro = id_ou_parametro

class RegraNegocioException(Exception):
    def __init__(self, detalhe: str):
        self.detalhe = detalhe

# Funções para registrar os manipuladores no main.py
def configurar_excecoes(app):
    @app.exception_handler(EntidadeNaoEncontradaException)
    async def not_found_handler(request: Request, exc: EntidadeNaoEncontradaException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"erro": f"{exc.entidade} com valor '{exc.id_ou_parametro}' não foi encontrado(a)."},
        )

    @app.exception_handler(RegraNegocioException)
    async def regra_negocio_handler(request: Request, exc: RegraNegocioException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"erro": "Violação de regra de negócio", "detalhe": exc.detalhe},
        )