from django.core.management.base import BaseCommand
from ecommerce.consumers import AMQPConsuming, AMQPConsumingEndDraw


class Command(BaseCommand):
    help = 'Starts the consumer process'
    def handle(self, *args, **options):
        td = AMQPConsuming()
        td.start()
        end_draw = AMQPConsumingEndDraw()
        end_draw.start()
        self.stdout.write("Started Consumer Process")