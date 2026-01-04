# pylint: disable=too-many-arguments, too-many-positional-arguments, broad-exception-caught
import structlog
from async_sendgrid import SendgridAPI
from async_sendgrid.sendgrid import Mail

default_logger = structlog.get_logger()


class EmailService:
    def __init__(self, api_key: str, from_email: str, logger=default_logger):
        self.client = SendgridAPI(api_key)
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

        message = Mail(
            from_email=self.from_email,
            to_emails=[to_email],
            subject=subject,
            plain_text_content=content,
        )

        try:
            response = await self.client.send(message)
            if response.status_code in (200, 202):
                self.logger.info(
                    "Email sent successfully",
                    status_code=response.status_code,
                    to=to_email,
                )
                return True

            self.logger.error(
                "Failed to send email",
                status_code=response.status_code,
                to=to_email,
            )
            return False
        except Exception as e:
            self.logger.error("Failed to send email", error=str(e), to=to_email)
            return False
