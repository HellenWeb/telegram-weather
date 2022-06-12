# Modules

from dispacher import bot, dp, db
import requests
from bs4 import BeautifulSoup as bs
from aiogram import types, executor
from config import weather_API
from dataclasses import dataclass
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Types Class

@dataclass()
class Weather:
    name: str
    city: str

# State Class

class FSMSettings(StatesGroup):
    name = State()
    city = State()

# Logic

"""

    Save in memory

"""


@dp.message_handler(state=FSMSettings.name)
async def upload_name(message: types.message, state: FSMContext):
    """Detected data"""
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer("Name saved")
    """Checking in the database"""
    if db.show_info(message.from_user.id):
        db.update_name(message.from_user.id, data["name"])
    else:
        db.inster_name(message.from_user.id, data["name"])
    await state.finish()


@dp.message_handler(state=FSMSettings.city)
async def upload_name(message: types.message, state: FSMContext):
    """Detected data"""
    async with state.proxy() as data:
        data["city"] = message.text
    await message.answer("City saved")
    """Checking in the database"""
    if db.show_info(message.from_user.id):
        db.update_city(message.from_user.id, data["city"])
    else:
        db.inster_city(message.from_user.id, data["city"])
    await state.finish()


"""

    Welcome Message

"""


@dp.message_handler(commands=["start"])
async def echo(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.row(
        types.InlineKeyboardButton(text="❓", callback_data="call_help"),
        types.InlineKeyboardButton(text="🇷🇺", callback_data="call_lang"),
    )
    await message.answer(
        f"<strong>Hello {message.from_user.first_name}</strong>\n\n- This bot will help you find out the weather in any city and all the information about it.\n\nCreator: @YungHellen",
        reply_markup=markup,
    )


"""

    Help Command

"""


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(
        "<strong>/start</strong> - Welcome Message\n<strong>/weather</strong> - Weather in your city\n<strong>/settings</strong> - Settings user"
    )


"""

    Settings Command

"""


@dp.message_handler(commands=["settings"])
async def settings_command(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Name", "City")
    markup.row("🏠", "⬅️")
    try:
        await message.answer(
            f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - {db.show_info(message.from_user.id)[0][2]}\n<strong>City</strong> - {db.show_info(message.from_user.id)[0][3]}",
            reply_markup=markup,
        )
    except IndexError or TypeError:
        await message.answer(
            f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - empty\n<strong>City</strong> - empty\n\n<strong>To display the data you need to enter all of them</strong>",
            reply_markup=markup,
        )


"""

    Weather Command

"""


@dp.message_handler(commands=["weather"])
async def weather(message: types.Message):
    try:
        r = requests.get("https://time-in.ru/coordinates/russia")
        html = bs(r.content, "html.parser")
        items = html.select(".coordinates-items > li")
        if len(items):
            for el in items:
                if (
                    el.select(".coordinates-items-left")[0].text
                    == db.show_info(message.from_user.id)[0][3]
                ):
                    title = el.select(".coordinates-items-right")
                    api = requests.get(
                        f"https://api.openweathermap.org/data/2.5/weather?lat={title[0].text.split(', ')[0]}&lon={title[0].text.split(', ')[1]}&appid={weather_API}"
                    ).json()
                    await message.answer(
                        f'\nCity: {db.show_info(message.from_user.id)[0][3]}\nTemperature: {round(api["main"]["temp"] - 273)}°С\nDescription: {api["weather"][0]["description"]}\nHumidity: {api["main"]["humidity"]}%'
                    )
    except IndexError or TypeError:
        await message.answer(
            "<strong>Enter your profile information</strong> /settings"
        )


"""

    Inline Callbacks

"""


@dp.callback_query_handler(lambda r: True)
async def callback(c: types.CallbackQuery):
    if c.data == "call_help":
        markup_lang = types.InlineKeyboardMarkup(row_width=1)
        markup_lang.add(
            types.InlineKeyboardButton(text="⬅️", callback_data="call_back")
        )
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text="<strong>/start</strong> - Welcome Message\n<strong>/weather</strong> - Weather in your city\n<strong>/settings</strong> - Settings user",
            reply_markup=markup_lang,
        )
    if c.data == "call_lang":
        markup_lang = types.InlineKeyboardMarkup(row_width=1)
        markup_lang.add(
            types.InlineKeyboardButton(text="⬅️", callback_data="call_back")
        )
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"<strong>Привет {c.from_user.first_name}</strong>\n\n- Этот бот поможет вам узнать погоду в любом городе и всю информацию о ней\n\nСоздатель: @YungHellen",
            reply_markup=markup_lang,
        )
    if c.data == "call_back":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.row(
            types.InlineKeyboardButton(text="❓", callback_data="call_help"),
            types.InlineKeyboardButton(text="🇷🇺", callback_data="call_lang"),
        )
        await bot.edit_message_text(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
            text=f"<strong>Hello {c.from_user.first_name}</strong>\n\n- This bot will help you find out the weather in any city and all the information about it.\n\nCreator: @YungHellen",
            reply_markup=markup,
        )


"""

    Reply Callbacks

"""


@dp.message_handler(content_types=["text"])
async def reply_callbacks(message: types.Message):
    if message.chat.type == "private":
        if message.text == "Name":
            await FSMSettings.name.set()
            await message.answer("Enter your name")
        if message.text == "City":
            await FSMSettings.city.set()
            await message.answer("Enter your city on Russian (Москва)")
        if message.text == "⬅️":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("Name", "City")
            markup.row("🏠", "⬅️")
            try:
                await message.answer(
                    f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - {db.show_info(message.from_user.id)[0][2]}\n<strong>City</strong> - {db.show_info(message.from_user.id)[0][3]}",
                    reply_markup=markup,
                )
            except IndexError or TypeError:
                await message.answer(
                    f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - empty\n<strong>City</strong> - empty\n\n<strong>To display the data you need to enter all of them</strong>",
                    reply_markup=markup,
                )
        if message.text == "🏠":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("🌦", "⚙️")
            await message.answer(
                f"<strong>Hello {message.from_user.first_name}</strong>\n\n- This bot will help you find out the weather in any city and all the information about it.\n\nCreator: @YungHellen",
                reply_markup=markup,
            )
        if message.text == "🌦":
            try:
                r = requests.get("https://time-in.ru/coordinates/russia")
                html = bs(r.content, "html.parser")
                items = html.select(".coordinates-items > li")
                if len(items):
                    for el in items:
                        if (
                            el.select(".coordinates-items-left")[0].text
                            == db.show_info(message.from_user.id)[0][3]
                        ):
                            title = el.select(".coordinates-items-right")
                            api = requests.get(
                                f"https://api.openweathermap.org/data/2.5/weather?lat={title[0].text.split(', ')[0]}&lon={title[0].text.split(', ')[1]}&appid={weather_API}"
                            ).json()
                            await message.answer(
                                f'\nCity: {db.show_info(message.from_user.id)[0][3]}\nTemperature: {round(api["main"]["temp"] - 273)}°С\nDescription: {api["weather"][0]["description"]}\nHumidity: {api["main"]["humidity"]}%'
                            )
            except IndexError or TypeError:
                await message.answer(
                    "<strong>Enter your profile information</strong> /settings"
                )
        if message.text == "⚙️":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("Name", "City")
            markup.row("🏠", "⬅️")
            try:
                await message.answer(
                    f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - {db.show_info(message.from_user.id)[0][2]}\n<strong>City</strong> - {db.show_info(message.from_user.id)[0][3]}",
                    reply_markup=markup,
                )
            except IndexError or TypeError:
                await message.answer(
                    f"<strong>ID</strong> - {message.from_user.id}\n<strong>Name</strong> - empty\n<strong>City</strong> - empty\n\n<strong>To display the data you need to enter all of them</strong>",
                    reply_markup=markup,
                )


# Polling

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
