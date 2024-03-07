from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse, Response

from sqlalchemy.orm import Session

from .settings import templates, get_db
from .models import Orders, Buyers, Products

router = APIRouter()


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Orders).all()
    products = db.query(Products).all()
    return templates.TemplateResponse(
        "orders.html", {"request": request, "orders": orders, "products": products}
    )


@router.post("/add")
async def add(
    request: Request,
    buyer_name: str = Form(...),
    buyer_last_name: str = Form(...),
    product_name: str = Form(...),
    product_quantity: int = Form(...),
    db: Session = Depends(get_db),
):
    buyer = (
        db.query(Buyers)
        .filter(Buyers.first_name == buyer_name, Buyers.last_name == buyer_last_name)
        .first()
    )
    product = db.query(Products).filter(Products.name == product_name).first()

    if not buyer:
        buyer = Buyers(first_name=buyer_name, last_name=buyer_last_name)
        db.add(buyer)
        db.commit()
        db.refresh(buyer)

    if not product:
        product = Products(name=product_name)
        db.add(product)
        db.commit()
        db.refresh(product)

    order = Orders(
        buyer_id=buyer.id,
        product_id=product.id,
        quantity=product_quantity,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    order = db.query(Orders).filter(Orders.id == order.id).first()
    order.number = f"#{order.id:06}"
    db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/update/{order_id}")
async def update(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    order.done = not order.done
    db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{order_id}")
async def delete(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    db.delete(order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_303_SEE_OTHER)
