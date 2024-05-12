from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from ecommerce.consumers import AMQPProducing

from ecommerce.models.lottery_draw import LotteryDraw
from django.contrib.auth.decorators import login_required

from django.utils import timezone


@login_required
def draw_trigger(request, id: int):
    user = request.user
    if not user.is_staff:
        return HttpResponseForbidden()
    draw = LotteryDraw.objects.get(id=id)
    draw_date = timezone.localtime(draw.date).strftime("%Y-%m-%d %H:%M:%S")
    queue = "jb_trigger"
    payload = {
        "lotery_key": draw.lottery.lotery_key,
        "target_lotery_datetime": draw_date,
        "draw_id": draw.id,
    }

    AMQPProducing.send_message(queue, payload)
    return redirect("admin:ecommerce_lotterydraw_changelist")
