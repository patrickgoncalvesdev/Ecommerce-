from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from ecommerce.utils.consts import PuleType
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


class Modality(BaseModel):
    name: str


class Seller(BaseModel):
    name: str
    
    
class Placing(BaseModel):
    name: str
    
    
class Lottery(BaseModel):
    name: str
    
    
class LotteryDraw(BaseModel):
    name: str
    lottery: Lottery
    
    
class Pule(BaseModel):
    hash: str
    lottery_draw: LotteryDraw
    seller: Seller | None = None
    created_at: str
    modality: Modality
    placing: Placing
    guesses: list[str]
    value_total: str
    type: PuleType
    

class AffiliateReport(BaseModel):
    sales: Decimal
    commissions: Decimal
    awards: Decimal
    total: Decimal
    user_above_name: str
    name: str
    id: int
    query: dict


class ColorRGB(BaseModel):
    rgb: tuple[float, float, float]
    
    @property
    def red(self):
        return self.rgb[0]
    
    @property
    def green(self):
        return self.rgb[1]
    
    @property
    def blue(self):
        return self.rgb[2]
    

class CreatePDF:
    def __init__(self, canvas: canvas.Canvas, color_background: str = "#0f0921", color_border: str = "#7248b2", color_button: str = "#2a155b"):
        self.pdf = canvas
        self.width, self.height = self.pdf._pagesize
        self.background = ColorRGB(rgb=self.hex_to_rgb(color_background))
        self.border = ColorRGB(rgb=self.hex_to_rgb(color_border))
        self.button = ColorRGB(rgb=self.hex_to_rgb(color_button))
        
    def hex_to_rgb(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return r, g, b

    def set_new_page(self, red: float, green: float, blue: float):
        self.pdf.setFillColorRGB(red, green, blue)
        width, height = self.pdf._pagesize
        self.pdf.rect(0, 0, width, height, fill=True, stroke=False)
    
    def set_text(self, size: int = 14):
        self.pdf.setFont("Helvetica-Bold", size)
        self.pdf.setFillColorRGB(1, 1, 1)
        
    def new_page(self):
        self.pdf.showPage()
        self.set_new_page(self.background.red, self.background.green, self.background.blue)
        self.set_text()
        self.width, self.height = letter
        
    def draw_text(self, text: str, x: int, y: int):
        self.pdf.drawCentredString(x, y, text)
        
    def align_text_side_by_side(self, texts: list[str], spacing: int):
        texts = sorted(texts, key=lambda x: len(x), reverse=True)
        grouped_texts = [texts[i:i+2] for i in range(0, len(texts), 2)] 
        for letter in grouped_texts:
            self.height -= 30
            total_width = sum([self.pdf.stringWidth(text, "Helvetica-Bold", 14) for text in letter])
            x_start = self.width / 2 - (total_width / 2.8)
            if len(letter) == 1:
                x_start = self.width / 2
            for text in letter:
                self.pdf.setStrokeColorRGB(self.border.red, self.border.green, self.border.blue)
                self.pdf.setFillColorRGB(self.button.red, self.button.green, self.button.blue)
                text_width = self.pdf.stringWidth(text, "Helvetica-Bold", 14)
                self.pdf.roundRect(x_start - (text_width / 1.6), self.height - 5, text_width * 1.25, 19, 3, fill=True, stroke=True)
                self.pdf.setFillColorRGB(1, 1, 1)
                self.pdf.drawCentredString(x_start, self.height, text)
                x_start += text_width + spacing
                
    def create_pules_pdf(self, pules: list[Pule]):
        self.set_new_page(self.background.red, self.background.green, self.background.blue)
        self.set_text()
        for pule in pules:
            if self.height - 380 <= 0:
                self.new_page()
            self.height -= 100
            self.draw_text(f"--------- BILHETE #{pule.hash} ---------", self.width / 2, self.height)
            self.height -= 30
            self.draw_text(f"{pule.lottery_draw.lottery.name} - {pule.lottery_draw.name}", self.width / 2, self.height)
            self.height -= 20
            self.draw_text(f"VENDEDOR: {pule.seller.name if pule.seller else 'NÃO INFORMADO'}", self.width / 2, self.height)
            self.height -= 20
            self.draw_text(datetime.strptime(pule.created_at, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d/%m/%Y - %H:%M"), self.width / 2, self.height)
            self.height -= 30
            self.draw_text("-------------------------------------------", self.width / 2, self.height)
            self.height -= 30
            self.draw_text(f"{pule.modality.name} - {pule.placing.name}", self.width / 2, self.height)
            self.align_text_side_by_side(pule.guesses, 10)
            self.height -= 30
            self.draw_text(f"R$ {Decimal(pule.value_total) / len(pule.guesses) if pule.type == PuleType.EACH else pule.value_total} / {PuleType(pule.type).label.upper()}", self.width / 2, self.height)
            self.height -= 20
            self.draw_text(f"TOTAL: R${pule.value_total}", self.width / 2, self.height)
        if self.height - 150 <= 0:
            self.new_page()
        self.height -= 100
        self.draw_text("-------------------------------------------", self.width / 2, self.height)
        self.height -= 30
        self.draw_text(f"TOTAL: R${sum([Decimal(pule.value_total) for pule in pules])}", self.width / 2, self.height)
        self.pdf.save()
        
    def create_affiliate_report(self, report: AffiliateReport):
        self.set_new_page(self.background.red, self.background.green, self.background.blue)
        self.set_text(10)
        self.pdf.drawRightString(self.width - 20, self.height - 20, f"{report.query['quotation'].name if report.query.get('quotation') else 'TODAS AS COTAÇÕES'}" + f" - {report.query['created_at__date'] if report.query.get('created_at__date') else 'TODOS OS DIAS'}")
        self.set_text()
        self.pdf.drawCentredString(self.width / 2, self.height - 60, f"RELATÓRIO AFILIADO")
        
        fields = ["ID", "NOME", "GERENTE", "VENDAS", "COMISSÕES", "PREMIOS", "TOTAL"]
        values = [report.id, report.name, report.user_above_name, report.sales, report.commissions, report.awards, report.total]
        data = [fields, values]
        table = Table(data, colWidths=75, rowHeights=20)
        
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table.setStyle(style)
        
        table.wrapOn(self.pdf, self.width, self.height)
        table.drawOn(self.pdf, 50, self.height - 140)
        
        self.pdf.save()
        