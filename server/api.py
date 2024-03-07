from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base

from .routes_invoices import router as InvoicesRouter
from .routes_orders import router as OrdersRouter
from .settings import templates

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(InvoicesRouter, prefix="/invoices")
app.include_router(OrdersRouter, prefix="/orders")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
