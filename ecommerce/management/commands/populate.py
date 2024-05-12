from django.core.management.base import BaseCommand
from ecommerce.models.quotation import Quotation
from ecommerce.models.messages import MessagesTemplate
from ecommerce.models.modality import Modality
from ecommerce.models.lottery import Lottery
from ecommerce.models.placing import Placing
from ecommerce.models.quotation_modality import QuotationModality
from ecommerce.models.config import Config
from ecommerce.models.first_deposit import FirstDeposit
from django.db.models.query import QuerySet
from ecommerce.models.affiliate_config import AffiliateConfig
from pydantic import BaseModel
import traceback
import json
from django.db import transaction


class Structure(BaseModel):
    object: str
    action: str
    filter: dict | None = None
    data: list | dict | None = None
    
    @property
    def get_object(self):
        return eval(self.object)

class Populate:        
    temp = None
    
    @staticmethod
    def read_json() -> list:
        with open('populate.json', 'r') as file:
            data = json.load(file)
        return data
            
    def read_payloads(self, payload: dict):
        try:
            structure = Structure(**payload)
            if structure.action == 'create':
                if isinstance(structure.data, list):
                    for data in structure.data:
                        obj = structure.get_object.objects.create(**self.read_data(data))
                        if isinstance(self.temp, QuerySet):
                            if structure.object == 'Lottery':
                                obj.modalities.set(self.temp)
                            elif structure.object == 'Modality':
                                obj.placements.set(self.temp)
                else:
                    structure.get_object.objects.create(**self.read_data(structure.data))
                    if isinstance(self.temp, QuerySet):
                        if structure.object == 'Lottery':
                            obj.modalities.set(self.temp)
                        elif structure.object == 'Modality':
                            obj.placements.set(self.temp)
            elif structure.action == 'get':
                return structure.get_object.objects.get(**self.read_data(structure.filter))
            elif structure.action == 'filter':
                self.temp = structure.get_object.objects.filter(**self.read_data(structure.filter))
        except Exception as e:
            raise e
        
    def read_data(self, payload: dict):
        keys = []
        for key, value in payload.items():
            if isinstance(value, dict):
                response = self.read_payloads(value)
                if not response:
                    keys.append(key)
                else:
                    payload[key] = response
                    
        for key in keys:
            del payload[key]
        return payload
    

class Command(BaseCommand, Populate):
    help = "Populate database with data from populate.json file."

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.stdout.write("Populating database...")
                payloads = Command.read_json()
                if isinstance(payloads, list):
                    for payload in self.read_json():
                        self.read_payloads(payload)
                elif isinstance(payloads, dict):
                    self.read_payloads(payloads)
                else:
                    self.stdout.write(self.style.ERROR("Invalid payload"))
        finally:
            self.stdout.write(self.style.SUCCESS("Database populated successfully"))
            