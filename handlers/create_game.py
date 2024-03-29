import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot import start
from states import AddNewGame
from loader import dp, db, bot
from media.texts.captions import start_message
from media.texts.captions import create_game_message
from keyboards.inline import ikb


@dp.callback_query_handler(text="create_match")
async def create_game(call: types.CallbackQuery):
    if db.get_user_status(call.from_user.id) == 1:
        await call.answer(
            "❌ Вы не можете создавать игру так как у вас открыт арбитраж!",
            show_alert=True,
        )

    elif db.joiner_exists(call.from_user.id):
        await call.answer(
            "❌ Вы не можете создать игру, так как уже участвуете!", show_alert=True
        )

    elif db.game_exists(call.from_user.id):
        await call.answer(
            "❌ У вас уже существует 1 игра!\n🔘 Чтобы создать новую удалите предыдущую!",
            show_alert=True,
        )

    else:
        await AddNewGame.bet.set()
        await bot.edit_message_caption(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            caption=create_game_message,
            reply_markup=ikb.back_to_menu_ikb(),
        )


@dp.message_handler(state=AddNewGame.bet, content_types=["text"])
async def game_bet(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        bet = int(message.text)
        await state.update_data(bet=bet)

        if bet < 0:
            await bot.send_message(message.from_user.id, "‼️ Вы ввели число меньше 0!")

        elif bet == 0:
            await bot.send_message(
                message.from_user.id, "‼️ Ставка должна быть больше 0!"
            )

        elif bet > db.get_user_balance(message.from_user.id):
            await bot.send_message(
                message.from_user.id, "‼️ На вашем балансе недостаточно средств!"
            )
            await state.finish()
            await asyncio.sleep(2)
            await start(message)

        else:
            await AddNewGame.next()
            await bot.send_message(
                message.from_user.id, "✏️ Введите краткое описание для создания игры: "
            )
    else:
        await bot.send_message(message.from_user.id, "❌ <b>Вы ввели не число!</b>")


@dp.callback_query_handler(state=AddNewGame.bet, text="back_to_main_menu")
async def back(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=start_message,
        reply_markup=ikb.start_ikb(),
    )


@dp.message_handler(state=AddNewGame.description, content_types=["text"])
async def game_description(message: types.Message, state: FSMContext):
    bet = (await state.get_data())["bet"]
    description = message.text

    db.add_game(message.from_user.id, message.from_user.username, bet, description)
    db.balance_minus_bet(bet, message.from_user.id)
    for item in db.get_game_information(message.from_user.id):
        await bot.send_message(
            message.from_user.id,
            f"""✅ Ваша игра была успешно создана!

ℹ️ Информация:

🔢 Номер: {item[0]}
🎲 Ставка: {item[5]} р
📄 Описание: {item[6]}""",
        )

    await state.finish()
    await state.update_data(match_index=message.from_user.id)
    await asyncio.sleep(2)
    await start(message)