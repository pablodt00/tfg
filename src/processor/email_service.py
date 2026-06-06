# pylint: disable=too-many-arguments, too-many-positional-arguments, broad-exception-caught
import asyncio
import os

import resend
import structlog

default_logger = structlog.get_logger()


class EmailService:
    def __init__(self, api_key: str, from_email: str, logger=default_logger):
        resend.api_key = api_key
        if base_url := os.getenv("RESEND_BASE_URL"):
            resend.base_url = base_url
        self.from_email = from_email
        self.logger = logger

    async def send_alert_email(
        self, to_email: str, coin: str, price: float, condition: str, threshold: float
    ):
        subject = f"Price Alert: {coin.upper()}"
        content = (
            f"Alert triggered for "
            f"{coin.upper()}!\n\n"
            f"Current price: €{price}\n"
            f"Condition: {condition}\n"
            f"Threshold: €{threshold}"
        )

        params: resend.Emails.SendParams = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "text": content,
        }

        try:
            response = await asyncio.to_thread(resend.Emails.send, params)
            self.logger.info(
                "Email sent successfully",
                id=response["id"],
                to=to_email,
            )
            return True
        except Exception as e:
            self.logger.error("Failed to send email", error=str(e), to=to_email)
            return False
