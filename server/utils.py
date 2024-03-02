from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import io


def generate_pdf(invoice, seller, buyer, product, payment_method):
    pagesize = (595, 842)
    left_margin = 50
    top_margin = 50

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=pagesize)

    font = "Verdana"
    bold_font = f"{font}B"
    pdfmetrics.registerFont(TTFont(font, "Verdana.ttf"))
    pdfmetrics.registerFont(TTFont(bold_font, "VerdanaB.ttf"))

    c.setFont(font, 10)

    c.drawString(left_margin, pagesize[1] - top_margin, "Miejsce wystawienia:")
    c.drawString(left_margin, pagesize[1] - top_margin - 20, "Data wystawienia:")
    c.drawString(left_margin, pagesize[1] - top_margin - 40, "Data sprzedaży:")

    c.setFont(bold_font, 10)

    c.drawString(
        left_margin + stringWidth("Miejsce wystawienia:", font, 10) + 10,
        pagesize[1] - top_margin,
        invoice.place_of_issue,
    )
    c.drawString(
        left_margin + stringWidth("Data wystawienia:", font, 10) + 10,
        pagesize[1] - top_margin - 20,
        invoice.date_of_issue.strftime("%Y-%m-%d"),
    )
    c.drawString(
        left_margin + stringWidth("Data sprzedaży:", font, 10) + 10,
        pagesize[1] - top_margin - 40,
        invoice.date_of_purchase.strftime("%Y-%m-%d"),
    )

    c.setFont(font, 10)

    c.drawString(pagesize[0] / 2 + 25, pagesize[1] - top_margin, "Sprzedawca:")
    c.drawString(pagesize[0] / 2 + 25, pagesize[1] - top_margin - 20, "Nabywca:")

    c.setFont(bold_font, 10)
    c.drawString(
        pagesize[0] / 2 + 25 + stringWidth("Sprzedawca:", font, 10) + 10,
        pagesize[1] - top_margin,
        f"{seller.first_name} {seller.last_name}",
    )
    c.drawString(
        pagesize[0] / 2 + 25 + stringWidth("Nabywsa:", font, 10) + 10,
        pagesize[1] - top_margin - 20,
        f"{buyer.first_name} {buyer.last_name}",
    )

    c.setFont(bold_font, 14)
    c.drawString(
        pagesize[0] / 2 - stringWidth(invoice.number, bold_font, 14) + left_margin / 2,
        pagesize[1] - top_margin - 180,
        f"Faktura {invoice.number}",
    )
    c.setFont(font, 10)

    left_margin += 5
    c.drawString(left_margin, pagesize[1] - top_margin - 220, "Lp.")
    c.drawString(left_margin + 30, pagesize[1] - top_margin - 220, "Nazwa towaru")
    c.drawString(left_margin + 260, pagesize[1] - top_margin - 220, "Ilość (szt.)")
    c.drawString(left_margin + 330, pagesize[1] - top_margin - 220, "Cena (PLN)")
    c.drawString(left_margin + 400, pagesize[1] - top_margin - 220, "Wartość (PLN)")

    row_height = 15
    left_margin -= 5

    y_pos = pagesize[1] - top_margin - 220 - row_height
    c.line(left_margin, y_pos + 5, pagesize[0] - left_margin, y_pos + 5)

    total_amount = f"{int(invoice.quantity) * int(product.price_per_unit):.2f}"

    left_margin += 5

    y_pos -= row_height
    c.drawString(left_margin, y_pos, "1.")
    c.drawString(left_margin + 30, y_pos, product.name)
    c.drawString(left_margin + 280, y_pos, str(invoice.quantity))
    c.drawString(left_margin + 340, y_pos, f"{product.price_per_unit:.2f}")

    c.setFont(bold_font, 10)

    c.drawString(
        pagesize[0] - left_margin - stringWidth("Wartość (PLN)", font, 10), y_pos, total_amount
    )

    c.setFont(font, 10)

    left_margin -= 5

    y_pos -= row_height
    c.line(left_margin, y_pos + 5, pagesize[0] - left_margin, y_pos + 5)

    c.drawString(left_margin, pagesize[1] - top_margin - 350, "Sposób płatności:")
    payment_method_name = "przelew" if payment_method.name == "transfer" else "BLIK"
    c.drawString(left_margin + 100, pagesize[1] - top_margin - 350, payment_method_name)
    c.line(
        left_margin,
        pagesize[1] - top_margin - 360,
        pagesize[0] / 2 - 25,
        pagesize[1] - top_margin - 360,
    )

    c.setFont(bold_font, 12)
    c.drawString(pagesize[0] / 2 + 25, pagesize[1] - top_margin - 350, f"Razem: {total_amount} PLN")
    c.line(
        pagesize[0] / 2 + 25,
        pagesize[1] - top_margin - 360,
        pagesize[0] - left_margin,
        pagesize[1] - top_margin - 360,
    )

    c.save()

    return buffer
