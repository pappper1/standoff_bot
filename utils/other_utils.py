import datetime
from aiogram.utils.callback_data import CallbackData

games_cb = CallbackData("games_cb", "id", "action")

arbitrage_cb = CallbackData("arbitrage_cb", "id", "action")

date_now = datetime.datetime.now()
date = date_now.strftime("%Y-%m-%d")

def profile_caption(db, call):
    for item in db.all_user_information(call.from_user.id):
        profile_caption = f'''🎩 Ваш профиль: 

🆔 <b>ID:</b> {item[1]}
👤 <b>Username:</b> {item[2]}

💰 <b>Баланс:</b> {item[3]} р
🕹 <b>Игр сыграно:</b> {item[4]}

⏰ <b>Дата регистрации:</b> {item[5]}

'''

    return profile_caption