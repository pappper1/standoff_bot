from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class InlineKeyboard:

    @staticmethod
    def start_ikb():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("🎩 Профиль", callback_data="profile")
        but_2 = InlineKeyboardButton("ℹ️ Информация", callback_data="information")
        but_3 = InlineKeyboardButton("🔫 Создать матч", callback_data="create_match")
        but_4 = InlineKeyboardButton("🔎 Найти матч", callback_data="find_match")
        ikb.add(but_1, but_2, but_3, but_4)
        return ikb


    @staticmethod
    def profile_ikb():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("💸 Пополнить", callback_data="cash_in")
        but_2 = InlineKeyboardButton("📤 Вывести", callback_data="withdraw")
        but_3 = InlineKeyboardButton("🚫 Удалить игру", callback_data="delete_game")
        but_4 = InlineKeyboardButton("🔙 Назад", callback_data="back_to_main_menu")
        ikb.add(but_1, but_2).add(but_3).add(but_4)
        return ikb


    @staticmethod
    def back_to_menu_ikb():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("🔙 Назад", callback_data="back_to_main_menu")
        ikb.add(but_1)
        return ikb


    @staticmethod
    def game_ikb():
        ikb = InlineKeyboardMarkup(row_width=1)
        but_1 = InlineKeyboardButton("🌐 Присоединиться", callback_data="join")
        but_2 = InlineKeyboardButton("🔙 Назад", callback_data="back_to_matches")
        ikb.add(but_1, but_2)
        return ikb


    @staticmethod
    def admin():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("📨 Рассылка", callback_data="spam")
        but_2 = InlineKeyboardButton("🚫 Бан", callback_data="ban")
        but_3 = InlineKeyboardButton("♻️ Разбанить", callback_data="unban")
        but_4 = InlineKeyboardButton("📱 Меню пользователя", callback_data="back_to_main_menu")
        but_5 = InlineKeyboardButton("💈 Выдать баланс", callback_data="add_balance")
        ikb.add(but_1).add(but_2, but_3).add(but_4).add(but_5)
        return ikb


    @staticmethod
    def withdraw_confirmation():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("✅ Подтвердить", callback_data="accept_withdraw")
        but_2 = InlineKeyboardButton("❌ Отмена", callback_data="decline_withdraw")
        ikb.add(but_1, but_2)
        return ikb


    @staticmethod
    def add_balance_confirmation():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("✅ Подтвердить", callback_data="accept_add")
        but_2 = InlineKeyboardButton("❌ Отмена", callback_data="decline_add")
        ikb.add(but_1, but_2)
        return ikb


    @staticmethod
    def cash_in_confirmation():
        ikb = InlineKeyboardMarkup(row_width=2)
        but_1 = InlineKeyboardButton("✅ Подтвердить", callback_data="accept_cash_in")
        but_2 = InlineKeyboardButton("❌ Отмена", callback_data="decline_cash_in")
        ikb.add(but_1, but_2)
        return ikb


    @staticmethod
    def chech_payment():
        ikb = InlineKeyboardMarkup(row_width=1)
        but_1 = InlineKeyboardButton("🔎 Проверить оплату", callback_data="check_payment")
        ikb.add(but_1)
        return ikb


    @staticmethod
    def back_to_profile_ikb():
        ikb = InlineKeyboardMarkup(row_width=1)
        but_1 = InlineKeyboardButton("🔙 Назад", callback_data="back_to_profile")
        ikb.add(but_1)
        return ikb

ikb = InlineKeyboard()