from fastapi import FastAPI, Request, Depends, Form, status

from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Invoices, PaymentMethods, Products, Sellers, Buyers, Base

from datetime import date
from calendar import monthrange

from .utils import generate_pdf

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(Invoices).all()
    return templates.TemplateResponse("index.html", {"request": request, "invoices": invoices})


@app.post("/add")
async def add(
    request: Request,
    buyer_name: str = Form(...),
    buyer_last_name: str = Form(...),
    product_name: str = Form(...),
    product_price: float = Form(...),
    product_quantity: int = Form(...),
    sale_date: str = Form(...),
    payment_method: str = Form(...),
    place_of_issue: str = Form(...),
    db: Session = Depends(get_db),
):
    buyer = (
        db.query(Buyers)
        .filter(Buyers.first_name == buyer_name, Buyers.last_name == buyer_last_name)
        .first()
    )
    product = (
        db.query(Products)
        .filter(Products.name == product_name, Products.price_per_unit == product_price)
        .first()
    )
    if not buyer:
        buyer = Buyers(first_name=buyer_name, last_name=buyer_last_name)
        db.add(buyer)
        db.commit()
        db.refresh(buyer)
    if not product:
        product = Products(name=product_name, price_per_unit=product_price)
        db.add(product)
        db.commit()
        db.refresh(product)

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
        buyer_id=buyer.id,
        seller_id=seller.id,
        product_id=product.id,
        payment_method_id=payment.id,
        quantity=product_quantity,
        total_amount=total_price,
        date_of_issue=date_of_issue,
        date_of_purchase=sale_date,
        place_of_issue=place_of_issue,
    )

    db.add(invoice)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{id}")
async def delete(request: Request, id: int, db: Session = Depends(get_db)):
    highest_id = db.query(Invoices).order_by(Invoices.id.desc()).first().id
    if id != highest_id:
        return Response(
            status_code=status.HTTP_403_FORBIDDEN, content="You can only delete the last invoice"
        )

    invoice = db.query(Invoices).filter(Invoices.id == id).first()
    db.delete(invoice)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/download/{id}")
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


@app.get("/display/{id}")
async def display(request: Request, id: int, db: Session = Depends(get_db)):
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

    headers = {"Content-Disposition": "inline; filename=invoice.pdf"}
    return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
