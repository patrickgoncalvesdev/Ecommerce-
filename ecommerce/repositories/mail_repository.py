from django.core.mail import send_mail
import threading


class SendEmailRepository:
    def __init__(self, email_host: str) -> None:
        self._from = email_host
        
    def execute_async(self, *args, **kwargs):
        print(f"Sending email {args} {kwargs}")
        thread = threading.Thread(target=self.send, args=args, kwargs=kwargs)
        thread.start()
        
    def send(self, to: str, subject: str, body: str):
        send_mail(subject, body, self._from, [to], fail_silently=False)
        