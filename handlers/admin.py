import keyboards.inline as ikb
from aiogram import types
from loader import dp, db, bot
from states import *
from keyboards.markup import back
from aiogram.dispatcher import FSMContext
from bot import start
import asyncio
from loguru import logger
from media.texts.captions import start_message


@dp.callback_query_handler(text="spam")
async def spamer(call: types.CallbackQuery):
    await Spam.spam.set()
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= '🗒 Введите текст, фото с подписью, видео с подписью:', 
                                    reply_markup= ikb.back_to_menu_ikb())


@dp.message_handler(state=Spam.spam, content_types=['text', 'photo', 'video'])
async def send_spam(message: types.Message, state: FSMContext):
    spam_base = db.all_users()
    succ_count = 0
    bad_count = 0
    
    if message.content_type == 'text':
        for i in range(len(spam_base)):
            try:
                await bot.send_message(spam_base[i][0], message.text)
                succ_count+=1
            
            except:
                bad_count+=1
                continue

    elif message.content_type == 'photo':
        message_text = message.caption
        photo_id = message.photo[0].file_id
        for i in range(len(spam_base)):
            try:
                await bot.send_photo(spam_base[i][0], photo_id, caption=message_text)
                succ_count+=1
            
            except: 
                bad_count+=1
    
    else:
        message_text = message.caption
        video_id = message.video.file_id
        for i in range(len(spam_base)):
            try:
                await bot.send_video(spam_base[i][0], video_id, caption=message_text)
                succ_count+=1
            
            except: 
                bad_count+=1
                continue

    await bot.send_message(message.from_user.id ,f'✅ Рассылка завершена!\n\nВсего отправлено сообщение: <b>{succ_count}</b>\nЗаблокировало бота: <b>{bad_count}</b>')
    await asyncio.sleep(2)
    await start(message)
    await state.finish()

@dp.callback_query_handler(text="ban")
async def ban(call: types.CallbackQuery):
    await Ban.ban.set()
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                   message_id= call.message.message_id,
                                   caption= '🗒 Введите ID нарушителя:', 
                                   reply_markup= ikb.back_to_menu_ikb())


@dp.message_handler(state=Ban.ban, content_types=['text'])
async def ban_user(message: types.Message, state: FSMContext):
    user_id = message.text

    db.ban_user(user_id)

    await bot.send_message(message.from_user.id, f"✅ Пользователь {user_id} был успешно заблокирован!")
    await asyncio.sleep(2)
    await start(message)
    await state.finish()


@dp.callback_query_handler(text="unban")
async def unban(call: types.CallbackQuery):
    await Unban.unban.set()
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                   message_id= call.message.message_id,
                                   caption= '🗒 Введите ID пользователя, которого хотите разблокировать:', 
                                   reply_markup= ikb.back_to_menu_ikb())


@dp.message_handler(state=Unban.unban, content_types=['text'])
async def unban_user(message: types.Message, state: FSMContext):
    user_id = message.text

    db.unban_user(user_id)

    await bot.send_message(message.from_user.id, f"✅ Пользователь {user_id} был успешно разблокирован!")
    
    await asyncio.sleep(2)
    await start(message)

    await state.finish()


@dp.callback_query_handler(text="add_balance")
async def add_balance(call: types.CallbackQuery):
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= '✏️ Введите ID пользователя: ', 
                                    reply_markup= ikb.back_to_menu_ikb())
    
    await AddBalance.user.set()


@dp.message_handler(state = AddBalance.user, content_types=["text"])
async def add_balance_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_balance"] = message.text
        user = data['user_balance']

    await bot.send_message(message.from_user.id, f"✏️ Введите сумму, которую хотите добавить пользователю <b>{user}</b>: ")
    await AddBalance.next()


@dp.message_handler(state = AddBalance.amount, content_types=["text"])
async def add_balance_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = data["user_balance"]
        try:
            data["amount_balance"] = int(message.text)
            amount = data["amount_balance"]

            await bot.send_message(message.from_user.id, f'''🔰 Добавление баланса:
            
🆔 ID: {user}
💵 Сумма: {amount} р

🔆 Выберите действие ниже:''', reply_markup= ikb.add_balance_confirmation())
            
            await AddBalance.next()

        except:
            await bot.send_message(message.from_user.id, "🚫 Вы ввели не число!\n\n✏️ Попробуйте ещё раз!")


@dp.callback_query_handler(state= AddBalance.confirmation, text="accept_add")
async def add_balance_confirm(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user = data["user_balance"]
        amount = data["amount_balance"]
    
    try:
        db.balance_plus(amount, user)

        await bot.send_message(call.from_user.id, f"✅ {amount} р успешно зачислено на баланс пользователя {user}")

        await bot.delete_message(call.from_user.id, call.message.message_id)

    except Exception as e:
        await bot.send_message(call.from_user.id, "⚒ Что-то пошло не так")
        logger.error(e)

    finally:
        await asyncio.sleep(2)
        await state.finish()

        await start(call)
        

@dp.callback_query_handler(state= AddBalance.confirmation, text="decline_add")
async def add_balance_decline(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(call.from_user.id, "✅ Успешно отменено!")
    
    await asyncio.sleep(2)
    await start(call)


@dp.callback_query_handler(state= AddBalance.user, text="back_to_main_menu")
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= start_message, 
                                    reply_markup= ikb.admin())
    

@dp.callback_query_handler(state= Spam.spam, text="back_to_main_menu")
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= start_message, 
                                    reply_markup= ikb.admin())
    

@dp.callback_query_handler(state= Ban.ban, text="back_to_main_menu")
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= start_message, 
                                    reply_markup= ikb.admin())
    

@dp.callback_query_handler(state= Unban.unban, text="back_to_main_menu")
async def back_to_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    
    await bot.edit_message_caption(chat_id=call.from_user.id,
                                    message_id= call.message.message_id,
                                    caption= start_message, 
                                    reply_markup= ikb.admin())