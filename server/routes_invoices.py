from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse, Response

from sqlalchemy.orm import Session

from .settings import templates, get_db
from .models import Invoices, PaymentMethods, Products, Sellers, Buyers, Orders

from datetime import date
from calendar import monthrange

from .utils import generate_pdf


router = APIRouter()


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(Invoices).all()
    orders = db.query(Orders).all()
    return templates.TemplateResponse(
        "invoices.html", {"request": request, "invoices": invoices, "orders": orders}
    )


@router.post("/add")
async def add(
    request: Request,
    order_id: int = Form(...),
    product_price: float = Form(...),
    sale_date: str = Form(...),
    payment_method: str = Form(...),
    place_of_issue: str = Form(...),
    db: Session = Depends(get_db),
):
    order = db.query(Orders).filter(Orders.id == order_id).first()
    buyer = db.query(Buyers).filter(Buyers.id == order.buyer_id).first()
    product = db.query(Products).filter(Products.id == order.product_id).first()
    product_quantity = order.quantity
    payment = db.query(PaymentMethods).filter(PaymentMethods.name == payment_method).first()
    seller = db.query(Sellers).filter(Sellers.id == 1).first()
    date_of_issue = date.today()
    total_price = product_price * product_quantity

    number_of_invoices_in_month = (
        db.query(Invoices)
        .filter(
            Invoices.date_of_issue >= date_of_issue.replace(day=1),
            Invoices.date_of_issue
            <= date_of_issue.replace(day=monthrange(date_of_issue.year, date_of_issue.month)[1]),
        )
        .count()
    )

    invoice_number = (
        f"FV/{number_of_invoices_in_month + 1:03}/{date_of_issue.month:02}/{date_of_issue.year}"
    )

    invoice = Invoices(
        number=invoice_number,
        order_id=order.id,
        buyer_id=buyer.id,
        seller_id=seller.id,
        product_id=product.id,
        payment_method_id=payment.id,
        quantity=product_quantity,
        price_per_unit=product_price,
        total_amount=total_price,
        date_of_issue=date_of_issue,
        date_of_purchase=sale_date,
        place_of_issue=place_of_issue,
    )

    db.add(invoice)
    db.commit()

    return RedirectResponse(url="/invoices", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{id}")
async def delete(request: Request, id: int, db: Session = Depends(get_db)):
    highest_id = db.query(Invoices).order_by(Invoices.id.desc()).first().id
    if id != highest_id:
        return Response(
            status_code=status.HTTP_403_FORBIDDEN, content="You can only delete the last invoice"
        )

    invoice = db.query(Invoices).filter(Invoices.id == id).first()
    db.delete(invoice)
    db.commit()

    return RedirectResponse(url="/invoices", status_code=status.HTTP_302_FOUND)


@router.get("/download/{id}")
async def download(request: Request, id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoices).filter(Invoices.id == id).first()
    seller = db.query(Sellers).filter(Sellers.id == invoice.seller_id).first()
    buyer = db.query(Buyers).filter(Buyers.id == invoice.buyer_id).first()
    product = db.query(Products).filter(Products.id == invoice.product_id).first()
    payment_method = (
        db.query(PaymentMethods).filter(PaymentMethods.id == invoice.payment_method_id).first()
    )

    buffer = generate_pdf(invoice, seller, buyer, product, payment_method)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    headers = {"Content-Disposition": f"attachment; filename=invoice_{id}.pdf"}
    return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")


@router.get("/display/{id}")
async def display(request: Request, id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoices).filter(Invoices.id == id).first()
    order = db.query(Orders).filter(Orders.id == invoice.order_id).first()
    seller = db.query(Sellers).filter(Sellers.id == invoice.seller_id).first()
    buyer = db.query(Buyers).filter(Buyers.id == invoice.buyer_id).first()
    product = db.query(Products).filter(Products.id == invoice.product_id).first()
    payment_method = (
        db.query(PaymentMethods).filter(PaymentMethods.id == invoice.payment_method_id).first()
    )

    buffer = generate_pdf(invoice, order, seller, buyer, product, payment_method)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    headers = {"Content-Disposition": "inline; filename=invoice.pdf"}
    return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
