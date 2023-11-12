import json
import os
import requests
from typing import Any

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import (BotCommand, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

import utils

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
URL = os.getenv("URL")

bot = TeleBot(API_TOKEN)
bot.set_my_description("Ищите интересные и необычные рецепты по категориям и ингредиентам.")
bot.set_my_commands([
    BotCommand("start", "Начни работу с ботом"),
    BotCommand("random", "Случайный рецепт"),
    BotCommand("menu_day", "Меню на день"),
    BotCommand("search_by_categories", "Поиск по категориям"),
    BotCommand("search_by_ingredients", "Поиск по ингредиентам"),
])


categories = json.loads(requests.get(f"{URL}api/categories").text)
user_categories = dict()
user_ingredients = dict()


"""Обработчики команд:"""


@bot.message_handler(commands=["start"])
def start(message: Message) -> None:
    """Обработчик команды /start."""

    keyboard = utils.get_main_menu()
    bot.send_message(message.chat.id, "Привет!")
    bot.send_message(message.chat.id, "Что будем искать?", reply_markup=keyboard)


@bot.message_handler(commands=["random"])
def random(message: Message) -> None:
    """Обработчик команды /random."""

    send_random_recipe(message)


@bot.message_handler(commands=["menu_day"])
def menu_day(message: Message) -> None:
    """Обработчик команды /menu_day."""

    send_menu_day(message)


@bot.message_handler(commands=["search_by_categories"])
def search_by_categories(message: Message) -> None:
    """Обработчик команды /search_by_categories."""

    send_categories(message)


@bot.message_handler(commands=["search_by_ingredients"])
def search_by_ingredients(message: Message) -> None:
    """Обработчик команды /search_by_ingredients."""

    send_ingredients(message)


"""Обработчики callback_query:"""


@bot.callback_query_handler(lambda callback: callback.data == "random_recipe")
def callback_random_recipe(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при нажатии кнопки главного меню 'Случайный рецепт'."""

    send_random_recipe(callback.message)


@bot.callback_query_handler(lambda callback: callback.data == "menu_day")
def callback_menu_day(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при нажатии кнопки главного меню 'Меню на день'."""

    send_menu_day(callback.message)


@bot.callback_query_handler(lambda callback: callback.data == "search_by_category")
def callback_search_by_category(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при нажатии кнопки главного меню 'Поиск по категориям'."""

    send_categories(callback.message)


@bot.callback_query_handler(lambda callback: callback.data.startswith("category"))
def callback_selected_categories(callback: CallbackQuery) -> None:
    """
    Функция для обработки запроса при выборе одной кнопки категории.

    Изменяется клавиатура - выбранные категории помечены галочкой (на вид как чекбокс).
    """

    global user_categories
    user_id = callback.message.chat.id
    user_categories.setdefault(user_id, list())
    category_id = int(callback.data.split()[-1])
    if category_id not in user_categories[user_id]:
        user_categories[user_id].append(int(callback.data.split()[-1]))
    else:
        user_categories[user_id].remove(category_id)

    keyboard = get_keyboard_categories(categories, user_id)

    bot.edit_message_text(
        chat_id=user_id,
        message_id=callback.message.message_id,
        text="Выберите категории:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(lambda callback: callback.data.startswith("send_categories"))
def callback_send_categories_aside_select(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при отправке выбранных категорий."""

    global user_categories
    user_id = callback.message.chat.id
    url_endswith = "aside" if callback.data.endswith("aside") else "select"
    response = requests.get(
        f"{URL}api/recipes/categories/{url_endswith}",
        params=f"categories={','.join([str(category) for category in user_categories[user_id]])}"
    )
    recipes = json.loads(response.text)
    keyboard = utils.get_keyboard_recipes(recipes)
    text_message = "Блюда:" if keyboard.keyboard else "Блюда не найдены"
    bot.send_message(user_id, text_message, reply_markup=keyboard)


@bot.callback_query_handler(lambda callback: callback.data == "search_by_ingredients")
def callback_search_by_ingredients(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при нажатии кнопки главного меню 'Поиск по ингредиентам'."""

    send_ingredients(callback.message)


@bot.callback_query_handler(lambda callback: callback.data.endswith("add"))
def callback_search_by_ingredients_add(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при нажатии кнопки 'другие ингредиенты' если нет выбранных."""

    send_ingredients(callback.message, add=True)


@bot.callback_query_handler(lambda callback: callback.data.startswith("search_by_ingredients"))
def callback_selected_startswith_symbol_for_ingredients(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при выборе начала названия ингредиента."""

    callback_data = callback.data.split()
    user_id = callback.message.chat.id

    global user_ingredients
    user_ingredients.setdefault(user_id, dict())
    if len(callback_data) > 2:
        ingredient_id = int(callback_data[-1])
        if ingredient_id not in user_ingredients[user_id].keys():
            user_ingredients[user_id][ingredient_id] = " ".join(callback_data[1:-1])
        else:
            user_ingredients[user_id].pop(ingredient_id)

    startswith_ingredient = callback_data[1][0]
    response = requests.get(f"{URL}api/ingredients", params=f"startswith={startswith_ingredient}")
    ingredients = json.loads(response.text)
    keyboard = get_keyboard_ingredients(ingredients, user_id)

    select_ingredients = ", ".join(user_ingredients[user_id].values())
    text_message = f"Выбранные ингредиенты: {select_ingredients}"

    if text_message.startswith("Выбранные ингредиенты:"):
        keyboard.add(InlineKeyboardButton(
            text="<<< Добавить другие ингредиенты",
            callback_data="search_by_ingredients_add"
        ))

    bot.edit_message_text(
        chat_id=user_id,
        message_id=callback.message.message_id,
        text=text_message,
        reply_markup=keyboard
    )


@bot.callback_query_handler(lambda callback: callback.data == "send_ingredients")
def callback_send_ingredients(callback: CallbackQuery) -> None:
    """
    Функция для обработки запроса при нажатии кнопки 'Найти рецепт'.

    Предоставляется выбор - искать рецепты с содержанием указанных
    ингредиентов либо с ограничением ингредиентов.
    """

    user_id = callback.message.chat.id
    global user_ingredients
    bot.send_message(
        user_id, f"Выбранные ингредиенты: {', '.join(user_ingredients[user_id].values())}"
    )
    keyboard = InlineKeyboardMarkup()
    button_aside = InlineKeyboardButton(
        text="с содержанием ингредиентов",
        callback_data="send_ingredients_aside"
    )
    keyboard.add(button_aside)
    button_select = InlineKeyboardButton(
        text="с ограничением по ингредиентам",
        callback_data="send_ingredients_select"
    )
    keyboard.add(button_select)
    bot.send_message(user_id, "Поиск рецептов...", reply_markup=keyboard)


@bot.callback_query_handler(lambda callback: callback.data.startswith("send_ingredients"))
def callback_send_ingredients_aside_select(callback: CallbackQuery) -> None:
    """Функция для обработки запроса при отправке выбранных ингредиентов."""

    global user_ingredients
    user_id = callback.message.chat.id
    ingredients = ",".join([str(ingredient) for ingredient in user_ingredients[user_id].keys()])
    url_endswith = "in" if callback.data.endswith("aside") else "only"
    response = requests.get(
        f"{URL}api/recipes/ingredients/{url_endswith}", params=f"ingredients={ingredients}"
    )
    recipes = json.loads(response.text)
    keyboard = utils.get_keyboard_recipes(recipes)
    text_message = "Блюда:" if keyboard.keyboard else "Блюда не найдены"
    bot.send_message(user_id, text_message, reply_markup=keyboard)


@bot.callback_query_handler(lambda callback: callback.data.startswith("clear"))
def callback_clear(callback: CallbackQuery) -> None:
    """Функция для обработки при запросе по очистке выбора."""

    user_id = callback.message.chat.id
    if callback.data.endswith("categories"):
        global user_categories
        user_categories[user_id].clear()
        keyboard = get_keyboard_categories(categories, user_id)
        bot.edit_message_text(
            chat_id=user_id,
            message_id=callback.message.message_id,
            text="Выберите категории:",
            reply_markup=keyboard
        )
    else:
        global user_ingredients
        user_ingredients[user_id].clear()
        keyboard = utils.get_keyboard_startswith_ingredients()
        bot.edit_message_text(
            chat_id=user_id,
            message_id=callback.message.message_id,
            text="Выберите ингредиенты:",
            reply_markup=keyboard
        )


@bot.callback_query_handler(lambda callback: callback.data.startswith("recipe"))
def callback_recipe(callback: CallbackQuery) -> None:
    """Функция для обработки при запросе полного рецепта."""

    user_id = callback.message.chat.id
    response = requests.get(f"{URL}api/recipes/{callback.data.split()[-1]}")
    recipes_data = json.loads(response.text)
    text = utils.get_recipe_message(recipes_data)
    with open(recipes_data.get("image"), "rb") as photo:
        bot.send_photo(callback.message.chat.id, photo=photo)
    bot.send_message(user_id, text, parse_mode="HTML")

    global user_categories, user_ingredients
    user_categories.setdefault(user_id, list())
    user_categories[user_id].clear()
    user_ingredients.setdefault(user_id, dict())
    user_ingredients[user_id].clear()


@bot.message_handler()
def other_message(message: Message) -> None:
    """Обработчик всех остальных сообщений."""

    keyboard = utils.get_main_menu()
    bot.send_message(message.chat.id, "Что будем искать?", reply_markup=keyboard)


"""Функции для отправки сообщений при вызове команд/кнопок главного меню:"""


def send_random_recipe(msg: Any) -> None:
    """Функция для отправки случайного рецепта."""

    response = requests.get(f"{URL}api/random_recipe")
    random_recipe = json.loads(response.text)
    text = utils.get_recipe_message(random_recipe)
    with open(random_recipe.get("image"), "rb") as photo:
        bot.send_photo(msg.chat.id, photo=photo)
    bot.send_message(msg.chat.id, text, parse_mode="HTML")


def send_menu_day(msg: Any) -> None:
    """Функция для отправки меню на день."""

    response = requests.get(f"{URL}api/menu_day")
    menu = json.loads(response.text)

    for key, value in {
        "breakfast": "ЗАВТРАК", "lunch": "ОБЕД",
        "snack": "ПЕРЕКУС", "dinner": "УЖИН",
    }.items():
        with open(menu.get(key).get("image"), "rb") as photo:
            bot.send_photo(msg.chat.id, photo=photo)
        bot.send_message(
            msg.chat.id,
            f"<b>{value}:</b> " + utils.get_recipe_message(menu.get(key)),
            parse_mode="HTML"
        )


def send_categories(msg: Any) -> None:
    """Функция для отправки категорий."""

    user_id = msg.chat.id
    keyboard = get_keyboard_categories(categories, user_id)
    bot.send_message(user_id, "Выберите категории:", reply_markup=keyboard)


def send_ingredients(msg: Any, add: bool = False) -> None:
    """Функция для отправки ингредиентов."""

    keyboard = utils.get_keyboard_startswith_ingredients()

    global user_ingredients
    user_id = msg.chat.id
    user_ingredients.setdefault(user_id, dict())

    if user_ingredients[user_id] or add:
        select_ingredients = ", ".join(user_ingredients[user_id].values())
        text_message = f"Выбранные ингредиенты: {select_ingredients}"
        if user_ingredients[user_id]:
            keyboard.add(InlineKeyboardButton(
                text="Очистить ингредиенты",
                callback_data="clear_ingredients"
            ))
            keyboard.add(InlineKeyboardButton(
                text="Найти рецепты", callback_data="send_ingredients"
            ))
        bot.edit_message_text(
            chat_id=user_id,
            message_id=msg.message_id,
            text=text_message,
            reply_markup=keyboard
        )
    else:
        bot.send_message(msg.chat.id, "Выберите ингредиенты:", reply_markup=keyboard)


"""Функции для получения inline-клавиатур:"""


def get_keyboard_categories(categories_data: json, user_id: int) -> InlineKeyboardMarkup:
    """Функция для получения inline-меню с категориями блюд."""

    global user_categories
    user_categories.setdefault(user_id, list())
    buttons = list()
    for category in categories_data:
        category_id = category.get('id')
        if category_id in user_categories[user_id]:
            text = "✅ " + category.get("name")
        else:
            text = "🟩 " + category.get("name")
        buttons.append(InlineKeyboardButton(text=text, callback_data=f"category {category_id}"))
    keyboard = utils.get_inline_keyboard_row(buttons=buttons)

    if user_categories[user_id]:
        button_send = InlineKeyboardButton(
            text="Очистить выбор",
            callback_data="clear_categories"
        )
        keyboard.row(button_send)

    button_send = InlineKeyboardButton(
        text="Найти рецепты из каждой категории",
        callback_data="send_categories_aside"
    )
    keyboard.row(button_send)
    button_send = InlineKeyboardButton(
        text="Найти рецепты с полным совпадением",
        callback_data="send_categories_select"
    )
    keyboard.row(button_send)
    return keyboard


def get_keyboard_ingredients(ingredients_data: json, user_id: int) -> InlineKeyboardMarkup:
    """Функция для получения inline-меню с ингредиентами."""

    global user_ingredients
    user_ingredients.setdefault(user_id, dict())
    buttons = list()
    for ingredient in ingredients_data:
        ingredient_id = ingredient.get('id')
        if ingredient_id in user_ingredients[user_id].keys():
            text = "✅ " + ingredient.get("name")
        else:
            text = "🟩 " + ingredient.get("name")
        buttons.append(InlineKeyboardButton(
            text=text, callback_data=f"search_by_ingredients {text[2:]} {ingredient_id}")
        )
    keyboard = utils.get_inline_keyboard_row(buttons=buttons, row_count=2)
    if user_ingredients[user_id]:
        keyboard.add(InlineKeyboardButton(
            text="Найти рецепты", callback_data="send_ingredients"
        ))
    return keyboard


if __name__ == "__main__":
    bot.infinity_polling()
