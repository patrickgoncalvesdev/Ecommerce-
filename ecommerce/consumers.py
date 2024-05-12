import json
import multiprocessing

import pika

import os

from ecommerce.interfaces import BetMessage, EndDrawMessage
from ecommerce.models import Bet
from ecommerce.models.lottery_draw import LotteryDraw
from django.db import transaction


class AMQPConsuming(multiprocessing.Process):
    def callback(self, ch, method, properties, body):
        try:
            with transaction.atomic():
                message = BetMessage(**json.loads(body.decode("utf-8")))
                Bet.objects.select_for_update().get(
                    id=message.bet_id, win=False
                ).to_win()
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            ch.basic_ack(method.delivery_tag)

    @staticmethod
    def _get_connection():
        parameters = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        return pika.BlockingConnection(parameters)

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue="winner_bets")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume("winner_bets", self.callback)
        channel.start_consuming()


class AMQPConsumingEndDraw(multiprocessing.Process):
    def callback(self, ch, method, properties, body):
        try:
            message = EndDrawMessage(**json.loads(body.decode("utf-8")))
            draw = LotteryDraw.objects.get(id=message.draw_id)
            with transaction.atomic():
                draw.end_draw(message.results)
                draw.add_profits()
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            ch.basic_ack(method.delivery_tag)

    @staticmethod
    def _get_connection():
        parameters = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        return pika.BlockingConnection(parameters)

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue="end_draw")
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume("end_draw", self.callback)
        channel.start_consuming()


class AMQPProducing:

    @staticmethod
    def _get_connection():
        parameters = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        return pika.BlockingConnection(parameters)

    @staticmethod
    def send_message(queue_name: str, message: dict):
        connection = AMQPProducing._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message).encode("utf-8"),
        )
        connection.close()
