from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class StockInsuficienteError(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id

class PagoRechazadoError(Exception):
    def __init__(self, motivo: str):
        self.motivo = motivo

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StockInsuficienteError)
    async def stock_handler(request: Request, exc: StockInsuficienteError):
        return JSONResponse(status_code=422, content={
            "detail": f"Sin stock para el producto {exc.product_id}"
        })

    @app.exception_handler(PagoRechazadoError)
    async def pago_handler(request: Request, exc: PagoRechazadoError):
        return JSONResponse(status_code=402, content={
            "detail": f"Pago rechazado: {exc.motivo}"
        })
