from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def back():
    kb= ReplyKeyboardMarkup(resize_keyboard= True)
    but_1= KeyboardButton(text= '🔄Назад🔄')
    kb.add(but_1)
    return kb