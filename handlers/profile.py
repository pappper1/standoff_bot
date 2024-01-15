import asyncio
from loguru import logger


from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot
from keyboards.inline import ikb
from states import WithDraw, CashIn
from data.config import settings
from bot import start
from utils.other_utils import profile_caption


@dp.callback_query_handler(text="profile")
async def profile(call: types.CallbackQuery):
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=profile_caption(db, call),
        reply_markup=ikb.profile_ikb(),
    )


@dp.callback_query_handler(text="delete_game")
async def delete_game(call: types.CallbackQuery):
    if db.game_exists(call.from_user.id):
        if db.get_status(call.from_user.id) == 0:
            try:
                db.balance_plus(db.get_bet_amount(call.from_user.id), call.from_user.id)
                db.delete_game(call.from_user.id)
                await call.answer("✅ Ваша игра была успешно удалена!", show_alert=True)

            except Exception as e:
                await call.answer("❗️ Ошибка!", show_alert=True)
                logger.error(e)

        else:
            await call.answer(
                "❗️ Вы не можете удалить эту игру, так как она сейчас начата!",
                show_alert=True,
            )

    else:
        await call.answer("❗️ У вас нет созданных игр!", show_alert=True)


@dp.callback_query_handler(text="withdraw")
async def withdraw(call: types.CallbackQuery):
    await WithDraw.info.set()
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption="✏️ Введите платёжную систему и ваши реквизиты для вывода: ",
        reply_markup=ikb.back_to_menu_ikb(),
    )


@dp.message_handler(state=WithDraw.info, content_types=["text"])
async def withdraw_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["withdraw_info"] = message.text

    await bot.send_message(message.from_user.id, "✏️ Введите сумму для вывода: ")
    await WithDraw.next()


@dp.message_handler(state=WithDraw.amount, content_types=["text"])
async def withdraw_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        info = data["withdraw_info"]
        try:
            data["withdraw_amount"] = int(message.text)
            amount = data["withdraw_amount"]
            if 0 > amount < 50:
                await bot.send_message(
                    message.from_user.id, "❗️ Минимальная сумма вывода - <b>50р</b>"
                )
                await state.finish()
                await asyncio.sleep(2)
                await start(message)

            elif amount > db.get_user_balance(message.from_user.id):
                await bot.send_message(
                    message.from_user.id, f"‼️ На вашем балансе недостаточно средств!"
                )
                await state.finish()
                await asyncio.sleep(2)
                await start(message)

            else:
                await bot.send_message(
                    message.from_user.id,
                    f"💵 Сумма вывода: {amount} р\n\n🪪 Реквизиты: {info}\n\n🔰 Выберите действие ниже:",
                    reply_markup=ikb.withdraw_confirmation(),
                )
                await WithDraw.next()
        except:
            await bot.send_message(
                message.from_user.id, "🚫 Вы ввели не число!\n\n✏️ Попробуйте ещё раз!"
            )


@dp.callback_query_handler(state=WithDraw.acceptation, text="accept_withdraw")
async def withdraw_accept(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        amount = data["withdraw_amount"]
        info = data["withdraw_info"]

    db.balance_minus_bet(amount, call.from_user.id)
    db.update_withdraws_count(amount)
    for item in db.all_user_information(call.from_user.id):
        await bot.send_message(
            settings.ADMIN,
            f"""🔰 Новая заявка на вывод!
        
🆔 ID: {item[1]}
📱 Username: @{item[2]}
⏱ Дата регистрации: {item[5]}
🎯 Игр сыграл: {item[4]}

🪪 Платёжные реквизиты: {info}

💵Сумма вывода: {amount} р""",
        )

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(
        call.from_user.id,
        "✅ Заявка на вывод успешно создана!\n\n⌛️ Вывод осуществляется в течении 24 часов",
    )
    await asyncio.sleep(2)
    await start(call)
    await state.finish()


@dp.callback_query_handler(state=WithDraw.acceptation, text="decline_withdraw")
async def withdraw_decline(call: types.CallbackQuery, state: FSMContext):
    await bot.send_message(call.from_user.id, "✅ Вывод успешно отменён!")
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()
    await asyncio.sleep(2)
    await start(call)


@dp.callback_query_handler(text="cash_in")
async def cash_in(call: types.CallbackQuery):
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption="✏️ Введите сумму пополнения:",
        reply_markup=ikb.back_to_menu_ikb(),
    )
    await CashIn.amount.set()


@dp.message_handler(state=CashIn.amount, content_types=["text"])
async def cash_in_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data["cash_in_amount"] = int(message.text)
            amount = data["cash_in_amount"]
            await bot.send_message(
                message.from_user.id,
                f"💵 Сумма пополнения: {amount} р\n\n🔰 Выберите действие ниже: ",
                reply_markup=ikb.cash_in_confirmation(),
            )
            await CashIn.next()
        except:
            await bot.send_message(
                message.from_user.id, "🚫 Вы ввели не число!\n\n✏️ Попробуйте ещё раз!"
            )


@dp.callback_query_handler(state=CashIn.confirmation, text="accept_cash_in")
async def accept_cash_in(call: types.CallbackQuery, state: FSMContext):
    amount = (await state.get_data())["cash_in_amount"]
    await bot.delete_message(call.from_user.id, call.message.message_id)
    for item in db.all_user_information(call.from_user.id):
        await bot.send_message(
            settings.ADMIN,
            f"""🔰 Новая заявка на пополнение!
        
🆔 ID: {item[1]}
📱 Username: @{item[2]}
⏱ Дата регистрации: {item[5]}
🎯 Игр сыграл: {item[4]}

💵Сумма пополнения: {amount} р""",
        )
    await bot.send_message(
        call.from_user.id,
        "✅ Заявка на пополнение успешно создана!\n\n💈 Ожидайте, с вами свяжется администратор!",
    )
    await state.finish()
    await asyncio.sleep(2)
    await start(call)


@dp.callback_query_handler(state=CashIn.confirmation, text="decline_cash_in")
async def decline_cash_in(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "✅ Пополнение успешно отменено!")
    await asyncio.sleep(2)
    await start(call)


@dp.callback_query_handler(state=CashIn.amount, text="back_to_main_menu")
async def back_to_profile(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=profile_caption(db, call),
        reply_markup=ikb.profile_ikb(),
    )


@dp.callback_query_handler(state=WithDraw.info, text="back_to_main_menu")
async def back_to_profile(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.edit_message_caption(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        caption=profile_caption(db, call),
        reply_markup=ikb.profile_ikb(),
    )