from ecommerce.serializers.send_email import SendEmailSerializers
import httpx
import threading

from ecommerce.serializers.send_sms import SendSmsSerializers


class SMSMarketAPIRepository:
    def __init__(self, username: str, password: str, base_url: str) -> None:
        self._base_url = base_url
        self._username = username
        self._password = password

    def execute_async(self, *args, **kwargs):
        thread = threading.Thread(target=self.send, args=args, kwargs=kwargs)
        thread.start()

    def send(self, **kwargs):
        body = SendSmsSerializers(data=kwargs)
        body.is_valid(raise_exception=True)
        payload = body.validated_data
        print(self._base_url)
        print(self._username)
        print(self._password)
        print(payload['number'])
        print(payload['message'])
        with httpx.Client() as client:
            response = client.get(
                f"{self._base_url}/send-single?user={self._username}&password={self._password}&country_code={55}&number={payload['number']}&content={payload['message']}&type={2}",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            print("sending sms", response.json(), response.status_code)
            response.raise_for_status()
            return response.json()
