import json
from typing import List

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_inline_keyboard_column(buttons: List[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    """ Функция для создания встроенной клавиатуры в столбик. """

    keyboard = InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    return keyboard


def get_inline_keyboard_row(buttons: List[InlineKeyboardButton], row_count: int = 3) -> InlineKeyboardMarkup:
    """ Функция для создания встроенной клавиатуры рядами. """

    keyboard = InlineKeyboardMarkup()
    for i in range(0, len(buttons), row_count):
        row_button = list()
        row_button.append(buttons[i])
        for j in range(1, row_count):
            if i + j < len(buttons):
                row_button.append(buttons[i + j])
        keyboard.row(*row_button)
    return keyboard


def get_main_menu() -> InlineKeyboardMarkup:
    """ Функция для создания клавиатуры главного меню. """

    main_button_data = [
        {"text": "Случайный рецепт", "callback_data": "random_recipe"},
        {"text": "Меню на день", "callback_data": "menu_day"},
        {"text": "Поиск по категориям", "callback_data": "search_by_category"},
        {"text": "Поиск по ингредиентам", "callback_data": "search_by_ingredients"},
    ]
    buttons = [
        InlineKeyboardButton(
            text=button_data.get("text"), callback_data=button_data.get("callback_data")
        )
        for button_data in main_button_data
    ]
    return get_inline_keyboard_column(buttons)


def get_recipe_message(recipe_data: json) -> str:
    """ Функция для формирования сообщения о полном рецепте. """

    ingredients = '\n'.join([
        f"  {ingredient['ingredient']['name']}: {ingredient['count']}"
        for ingredient in recipe_data.get('ingredients')
    ])

    return (f"<b>{recipe_data.get('name').upper()}</b>\n"
            f"<b><i>Время приготовления:</i></b> {recipe_data.get('cooking_time')} мин.\n"
            f"<b><i>Ингредиенты:</i></b>\n"
            f"{ingredients}\n"
            f"<b><i>Приготовление:</i></b>\n{recipe_data.get('description')}")


def get_keyboard_recipes(recipes_data: json) -> InlineKeyboardMarkup:
    """ Функция для получения inline-меню с названиями блюд. """

    buttons = [
        InlineKeyboardButton(
            text=recipe.get("name").capitalize(),
            callback_data=f"recipe {recipe.get('id')}"
        )
        for recipe in recipes_data
    ]
    return get_inline_keyboard_row(buttons=buttons, row_count=2)


def get_keyboard_startswith_ingredients() -> InlineKeyboardMarkup:
    """ Функция для получения inline-меню с началом названий блюд (алфавит). """

    buttons = [
        InlineKeyboardButton(
            text=symbol + "...",
            callback_data=f"search_by_ingredients {symbol}"
        )
        for symbol in "абвгдежзиклмнопрстуфхцчшщэюя"
    ]
    return get_inline_keyboard_row(buttons=buttons, row_count=4)
