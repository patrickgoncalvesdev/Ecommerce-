from zoneinfo import ZoneInfo
from ecommerce.models.lottery_draw import LotteryDraw
from django.core.management.base import BaseCommand
from ecommerce.consumers import AMQPProducing
from django.utils import timezone
import threading


class Command(BaseCommand):
    help = "Starts the job for active draws"

    def handle(self, *args, **options):
        draws = LotteryDraw.objects.filter(
            draw_trigger_date__gt=timezone.now(), is_active=True
        )
        for draw in draws:
            print(f"Now: {timezone.now()} Trigger date :{draw.draw_trigger_date}")
            draw_date = timezone.localtime(draw.date).strftime("%Y-%m-%d %H:%M:%S")
            til_cron_date = (draw.draw_trigger_date - timezone.now()).total_seconds()
            if til_cron_date > 0:
                print(
                    f"Time to cron: {til_cron_date} seconds or {(til_cron_date/60)/60} hours"
                )
                print(f"Draw date: {draw_date}")
                print(10 * "-")
                threading.Timer(
                    til_cron_date,
                    AMQPProducing.send_message,
                    args=(
                        "jb_trigger",
                        {
                            "lotery_key": draw.lottery.lotery_key,
                            "target_lotery_datetime": draw_date,
                            "draw_id": draw.id,
                        },
                    ),
                ).start()
