import os
import requests
from typing import Union
from aiogram import types
from dotenv import load_dotenv

load_dotenv()
FLASK_URL = os.getenv("FLASK_URL")


async def divide_event_request(request: str, message: Union[types.Message, types.CallbackQuery], json: dict):
    response = requests.post(f'{FLASK_URL}/{request}', json=json)
    if response.status_code == 200:
        return response.json()
    else:
        await message.answer("Error response")
