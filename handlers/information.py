from aiogram import types

from loader import dp, db, bot
from keyboards.inline import ikb
from media.texts.captions import start_message


@dp.callback_query_handler(text="information")
async def information(call: types.CallbackQuery):
    for item in db.all_bot_information():
        information_caption = f"""🧩 Информация о боте: 

🎮 <b>Всего игр сыграно:</b> {item[1]}
💵 <b>Всего выведено:</b> {item[2]} р
👥 <b>Всего пользователей:</b> {item[3]}

🤖 <b>Бот запущен:</b> {item[4]}"""

    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=information_caption,
        reply_markup=ikb.back_to_menu_ikb(),
    )


@dp.callback_query_handler(text="back_to_main_menu")
async def back(call: types.CallbackQuery):
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=start_message,
        reply_markup=ikb.start_ikb(),
    )