from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.cache import cache
from ecommerce.utils.pdf import CreatePDF, Pule
import json


class DownloadFinalizePurchaseAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema()
    def get(self, request: Request, id: str):
        payload = cache.get(f"{id}.pdf")
        if not payload:
            return Response(status=404, data={"detail": "PDF não encontrado"})
        payload = json.loads(payload)
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="recibo.pdf"'
        pdf = canvas.Canvas(response, pagesize=letter)
        creator_pdf = CreatePDF(pdf)
        pules = [Pule(**pule) for pule in payload["pules"]]
        creator_pdf.create_pules_pdf(pules)
        return response
