from ecommerce.serializers.send_email import SendEmailSerializers
import httpx
import threading


class MailBabyAPIRepository:
    def __init__(self, api_key: str, domain: str, email_host: str) -> None:
        self._from = email_host
        self._headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        self._url = f"{domain}/mail/send"
        
    def execute_async(self, *args, **kwargs):
        thread = threading.Thread(target=self.send, args=args, kwargs=kwargs)
        thread.start()
        
    def send(self, *args, **kwargs):
        body = SendEmailSerializers(data=kwargs)
        body.is_valid(raise_exception=True)
        payload = body.validated_data
        payload["from"] = self._from
        with httpx.Client() as client:
            response = client.post(self._url, headers=self._headers, json=payload)
            print(f"Sending email {response.json()} {response.status_code}")
            response.raise_for_status()
            return response.json()
        