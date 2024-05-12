from django.db import models
from ecommerce.models.lottery_draw import LotteryDraw
from django.utils import timezone
from pydantic import BaseModel
import logging


logger = logging.getLogger(__name__)

class Draws(BaseModel):
    name: str
    hour: int

class Automato(BaseModel):
    weekday: int
    draws: list[Draws]

    @staticmethod
    def get_automato_default():
        hours = [9, 11, 14, 16, 19, 21]
        weekdays = [0, 1, 2, 3, 4, 5, 6]
        return [{"weekday": weekday, "draws": [{"name": f"Sorteio das {hour} horas", "hour": hour} for hour in hours]} for weekday in weekdays]

class Lottery(models.Model):
    lotery_key = models.CharField(max_length=255)
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    modalities = models.ManyToManyField("Modality", related_name="lotteries")
    automato_payload = models.JSONField(default=Automato.get_automato_default, help_text="Payload para o automato")

    class Meta:
        verbose_name = "Loteria"
        verbose_name_plural = "Loterias"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_lotteries_active():
        return Lottery.objects.filter(is_active=True)
    
    def create_lottery_draw_by_each_day_of_week_and_hour(self):
        current_timezone = timezone.get_current_timezone()
        today = timezone.now().astimezone(current_timezone)
        current_week_day = today.weekday()
        automatos = sorted([Automato(**payload) for payload in self.automato_payload], key=lambda x: x.weekday)
        range = automatos[-1].weekday - current_week_day
        if range == 0:
            logger.error(f"data: {today.date()}")
            if LotteryDraw.objects.filter(date__date=today.date(), lottery=self).exists():
                for automato in automatos:
                    if automato.weekday >= current_week_day:
                        days_until_weekday = (automato.weekday - current_week_day + 7) % 7
                        if automato.weekday == current_week_day:
                            days_until_weekday = 7
                        date = today + timezone.timedelta(days=days_until_weekday)
                        logger.error(f"date: {date}")
                        if not LotteryDraw.objects.filter(date__date=date.date(), lottery=self).exists():
                            for draw in automato.draws:
                                date = date.replace(hour=draw.hour, minute=0, second=0)
                                logger.error(f"draw: {draw.name} - {date}")
                                if date > today:
                                    LotteryDraw.objects.create(
                                        name=draw.name,
                                        date=date,
                                        draw_trigger_date=date + timezone.timedelta(minutes=40),
                                        is_active=True,
                                        lottery=self,
                                    )
            else:
                for automato in automatos:
                    if automato.weekday >= current_week_day:
                        days_until_weekday = (automato.weekday - current_week_day + 7) % 7
                        date = today + timezone.timedelta(days=days_until_weekday)
                        logger.error(f"date: {date}")
                        if not LotteryDraw.objects.filter(date__date=date.date(), lottery=self).exists():
                            for draw in automato.draws:
                                date = date.replace(hour=draw.hour, minute=0, second=0)
                                logger.error(f"draw: {draw.name} - {date}")
                                if date > today:
                                    LotteryDraw.objects.create(
                                        name=draw.name,
                                        date=date,
                                        draw_trigger_date=date + timezone.timedelta(minutes=40),
                                        is_active=True,
                                        lottery=self,
                                    )
        else:
            for automato in automatos:
                if automato.weekday >= current_week_day:
                    days_until_weekday = (automato.weekday - current_week_day + 7) % 7
                    date = today + timezone.timedelta(days=days_until_weekday)
                    logger.error(f"date: {date}")
                    if not LotteryDraw.objects.filter(date__date=date.date(), lottery=self).exists():
                        for draw in automato.draws:
                            date = date.replace(hour=draw.hour, minute=0, second=0)
                            logger.error(f"draw: {draw.name} - {date}")
                            logger.error(f"date {date} > today {today} {date > today}")
                            if date > today:
                                LotteryDraw.objects.create(
                                    name=draw.name,
                                    date=date,
                                    draw_trigger_date=date + timezone.timedelta(minutes=40),
                                    is_active=True,
                                    lottery=self,
                                )
