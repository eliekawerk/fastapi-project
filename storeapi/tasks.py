import logging

import httpx

from storeapi.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass

async def send_simple_email(to: str, subject: str, body: str):
    logger.debug(f"Sending email to: {to[:3]} with subject: {subject[:20]}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Jose Salvatiera <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body
                }
            )
            response.raise_for_status()
            logger.debug(response.content)
            return response
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"API Request failed with status code: {err.response.status_code}"
            ) from err


async def send_user_registration_email(email: str, confirmation_url: str):
    return await send_simple_email(
        email,
        "Succesfully signed_up",
        (
            f"Hi {email}! You have successfully signed up.\n"
            f"Please confirm your email by clicking on the following link {confirmation_url}"
        )
    )
