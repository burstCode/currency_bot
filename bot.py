import asyncio
import logging
import datetime
import requests
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

import config

TOKEN = config.TOKEN

API_LINK = config.API_LINK

CHAT_ID = config.CHAT_ID

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

previous_data = []
previous_time = None
comparison_text = ""


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Приветствую, {hbold(message.from_user.full_name)}!\n"
        f"Используйте команду /about, чтобы узнать больше."
    )


@dp.message(Command('about'))
async def command_about_handler(message: Message) -> None:
    await message.answer(
        "Я призван ежечасно сообщать о котировках криптовалют.\n"
        "Если хотите узнать о курсе в данный момент времени,\n"
        "используйте команду /cryptocurrency_rate"
    )


@dp.message(Command('cryptocurrency_rate'))
async def command_cryptocurrency_rate_handler(message: Message) -> None:
    data = get_cryptocurrency_rate()

    global previous_data
    global previous_time
    global comparison_text

    compare_currency(data)

    previous_data = data

    if comparison_text:
        await message.answer(
            f"Курс криптовалют на момент {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}:\n\n"
            f"Биткоин: {data['bitcoin']['usd']}$, {data['bitcoin']['eur']}€, {data['bitcoin']['rub']}₽\n"
            f"Эфириум: {data['ethereum']['usd']}$, {data['ethereum']['eur']}€, {data['ethereum']['rub']}₽\n"
            f"Лайткоин: {data['litecoin']['usd']}$, {data['litecoin']['eur']}€, {data['litecoin']['rub']}₽\n"
            f"\nСравнение с предыдущими данными от {previous_time}:\n{comparison_text}"
        )
    else:
        await message.answer(
            f"Курс криптовалют на момент {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}:\n\n"
            f"Биткоин: {data['bitcoin']['usd']}$, {data['bitcoin']['eur']}€, {data['bitcoin']['rub']}₽\n"
            f"Эфириум: {data['ethereum']['usd']}$, {data['ethereum']['eur']}€, {data['ethereum']['rub']}₽\n"
            f"Лайткоин: {data['litecoin']['usd']}$, {data['litecoin']['eur']}€, {data['litecoin']['rub']}₽\n"
        )

    previous_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')


async def send_cryptocurrency_rate_periodically(wait):
    global previous_time
    global comparison_text

    while True:
        await asyncio.sleep(wait)

        now = datetime.datetime.now()

        if now.minute == 0:
            data = get_cryptocurrency_rate()

            compare_currency(data)

            if comparison_text:
                await bot.send_message(
                    CHAT_ID,
                    f"Курс криптовалют на момент {now.strftime('%d.%m.%Y %H:%M')}:\n\n"
                    f"Биткоин: {data['bitcoin']['usd']}$, {data['bitcoin']['eur']}€, {data['bitcoin']['rub']}₽\n"
                    f"Эфириум: {data['ethereum']['usd']}$, {data['ethereum']['eur']}€, {data['ethereum']['rub']}₽\n"
                    f"Лайткоин: {data['litecoin']['usd']}$, {data['litecoin']['eur']}€, {data['litecoin']['rub']}₽\n"
                    f"\nСравнение с предыдущими данными от {previous_time}:\n{comparison_text}"
                )
            else:
                await bot.send_message(
                    CHAT_ID,
                    f"Курс криптовалют на момент {now.strftime('%d.%m.%Y %H:%M')}:\n\n"
                    f"Биткоин: {data['bitcoin']['usd']}$, {data['bitcoin']['eur']}€, {data['bitcoin']['rub']}₽\n"
                    f"Эфириум: {data['ethereum']['usd']}$, {data['ethereum']['eur']}€, {data['ethereum']['rub']}₽\n"
                    f"Лайткоин: {data['litecoin']['usd']}$, {data['litecoin']['eur']}€, {data['litecoin']['rub']}₽\n"
                )

            previous_time = now.strftime('%d.%m.%Y %H:%M')


def get_cryptocurrency_rate():
    r = requests.get(API_LINK)
    data = r.json()

    return data


def compare_currency(data):
    global previous_data
    global comparison_text

    if previous_data:
        comparison_text = ""

        for currency, values in data.items():
            for key, value in values.items():
                prev_value = previous_data[currency].get(key)
                if prev_value is not None:
                    comparison_text += f"{currency} ({key}): {prev_value} -> {value}\n"

        return comparison_text


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    loop = asyncio.get_event_loop()

    loop.create_task(send_cryptocurrency_rate_periodically(60))

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(bot.session.close())
        loop.close()
