from loader import dp, db, bot
from aiogram import types
import keyboards.inline as ikb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from utils.other_utils import games_cb, arbitrage_cb
from media.texts.captions import find_games_message
from loguru import logger
import asyncio
from states import Arbitration
import data.config as cfg


@dp.callback_query_handler(text="find_match")
async def find_game(call: types.CallbackQuery):
    ikb = InlineKeyboardMarkup(row_width=1)

    for item in db.get_all_active_games():
        ikb.add(InlineKeyboardButton(f"🎲 Ставка {item[5]} р", callback_data= games_cb.new(id= item[1], action = "view")))

    ikb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main_menu"))
    
    await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=find_games_message, reply_markup=ikb)


@dp.callback_query_handler(games_cb.filter(action="view"))
async def game_info(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    match_id = callback_data['id']

    for item in db.get_game_information(match_id):
        await bot.edit_message_caption(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        caption= f'''📄 Информация о матче:
                                        
⚒ Создатель: {item[1]}
🎲 Ставка: {item[5]} р
📝 Описание: {item[6]}''', reply_markup= ikb.game_ikb())
        
    await state.update_data(match_index = match_id)
        

@dp.callback_query_handler(text="back_to_matches")
async def back_to_matches(call: types.CallbackQuery):
    await find_game(call)


@dp.callback_query_handler(text="join")
async def join_match(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        match_id = data["match_index"]

    if db.get_user_status(call.from_user.id) == 1:
        await call.answer("❌ Вы не можете присоединиться к матчу так как у вас открыт арбитраж!", show_alert= True)

    elif db.game_exists(call.from_user.id):
        await call.answer("❌ Вы не можете присоединиться к матчу, так как уже создали свой!", show_alert= True)
    
    elif str(match_id) == str(call.from_user.id):
        await call.answer("❌ Вы не можете присоединиться к своей же игре!", show_alert= True)
    
    elif db.get_user_balance(call.from_user.id) >= db.get_bet_amount(match_id):
        try:
            db.balance_minus_bet(db.get_bet_amount(match_id), call.from_user.id)
            db.update_games_count()
            db.update_user_games_count(match_id)
            db.update_user_games_count(call.from_user.id)
            db.activate_game(match_id)
            db.add_joiner(call.from_user.id, call.from_user.username, match_id)
            db.add_game_results(match_id)

            ikb = InlineKeyboardMarkup(row_width=2)
            ikb.add(InlineKeyboardButton(f"🏆 {match_id}", callback_data="creator"))
            ikb.add(InlineKeyboardButton(f"🏆 {call.from_user.id}", callback_data="joiner"))

            
            for item in db.get_game_information(match_id):
                await bot.edit_message_caption(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            caption=f'''✅ Вы успешно присоединились!
                
🔖 Информация об игре:

🔷 Вы: {item[3]}, @{item[4]}
🔷 Противник: {item[1]}, @{item[2]}

🎲 Ставка: {item[5]} р
📝 Описание: {item[6]}

💬 Удачной игры! 
⬇️ Ниже можно выбрать победителя по окончанию матча!
''', reply_markup= ikb)
                
                await bot.send_message(match_id, f'''✅ К вашей игре присоединился {call.from_user.id}!
                
🔖 Информация об игре:

🔷 Вы: {item[1]}, @{item[2]}
🔷 Противник: {item[3]}, @{item[4]}

🎲 Ставка: {item[5]} р
📝 Описание: {item[6]}

💬 Удачной игры!
⬇️ Ниже можно выбрать победителя по окончанию матча!
''', reply_markup= ikb)

            await state.update_data(match_index = match_id)

        except Exception as e:
            logger.exception(e)


@dp.callback_query_handler(text="creator")
async def winner_creator(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        match_id = data["match_index"]

    winner = call.data

    if str(call.from_user.id) == str(match_id):
        db.add_winner_1(winner, match_id)
  
        for item in db.get_results(match_id):
            if item[2] == "Выбор":
                await bot.send_message(call.from_user.id,  '❇️ Выбор сделан!\n⌛️ Ожидайте выбора второго игрока!')

            elif item[1] == item[2]:
                await bot.send_message(call.from_user.id, "🥇🎗 Вы победили в матче!")
                
                for user in db.get_game_information(match_id):
                    await bot.send_message(user[3], '⛔️ Вы проиграли в матче!')

                    db.balance_plus(user[5]*2-db.get_comission(), match_id)

                db.delete_game(match_id)
                db.delete_results(match_id)
                
            elif item[1] != item[2]:
                await bot.send_message(call.from_user.id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....")
                await bot.send_message(db.get_joiner(match_id), "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....\n\n‼️ Ожидайте когда с вами свяжется администратор!")

                db.update_status_arbitrage(call.from_user.id)
                db.update_status_arbitrage(db.get_joiner(match_id))
                
                await asyncio.sleep(2)

                await Arbitration.proofs.set()

                await bot.send_message(call.from_user.id, '⚠️ Пришлите следующим сообщением все доказательства вашей победы(фото, видео): ')   

                db.delete_results(match_id)
    
    else:
        db.add_winner_2(winner, match_id)
        
        for item in db.get_results(match_id):
            if item[1] == "Выбор":
                await bot.send_message(call.from_user.id, '❇️ Выбор сделан!\n⌛️ Ожидайте выбора второго игрока!')

            elif item[1] == item[2]:
                await bot.send_message(call.from_user.id,"⛔️ Вы проиграли в матче!")

                await bot.send_message(match_id, '🥇🎗 Вы победили в матче!')
                
                for user in db.get_game_information(match_id):
                    db.balance_plus(user[5]*2-db.get_comission(), match_id)

                db.delete_game(match_id)
                db.delete_results(match_id)
                
            elif item[1] != item[2]:
                await bot.send_message(call.from_user.id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....")
                await bot.send_message(match_id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....\n\n‼️ Ожидайте когда с вами свяжется администратор!")

                db.update_status_arbitrage(call.from_user.id)
                db.update_status_arbitrage(match_id)
                
                await asyncio.sleep(2)

                await Arbitration.proofs.set()

                await bot.send_message(call.from_user.id, '⚠️ Пришлите следующим сообщением все доказательства вашей победы(фото, видео): ')

                db.delete_results(match_id)
            

@dp.callback_query_handler(text="joiner")
async def winner_joiner(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        match_id = data["match_index"]

    winner = call.data

    if str(call.from_user.id) == str(match_id):
        db.add_winner_1(winner, match_id)
  
        for item in db.get_results(match_id):
            if item[2] == "Выбор":
                await bot.send_message(call.from_user.id,  '❇️ Выбор сделан!\n⌛️ Ожидайте выбора второго игрока!')

            elif item[1] == item[2]:
                await bot.send_message(call.from_user.id, "⛔️ Вы проиграли в матче!")
                
                for user in db.get_game_information(match_id):
                    await bot.send_message(user[3], '🥇🎗 Вы победили в матче!')

                    db.balance_plus(user[5]*2-db.get_comission(), user[3])

                db.delete_game(match_id)
                db.delete_results(match_id)
                
            elif item[1] != item[2]:
                await bot.send_message(call.from_user.id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....")
                await bot.send_message(db.get_joiner(match_id), "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....\n\n‼️ Ожидайте когда с вами свяжется администратор!")

                db.update_status_arbitrage(call.from_user.id)
                db.update_status_arbitrage(db.get_joiner(match_id))
                
                await asyncio.sleep(2)

                await Arbitration.proofs.set()

                await bot.send_message(call.from_user.id, '⚠️ Пришлите следующим сообщением все доказательства вашей победы(фото, видео): ') 

                db.delete_results(match_id)  
    
    else:
        db.add_winner_2(winner, match_id)
        
        for item in db.get_results(match_id):
            if item[1] == "Выбор":
                await bot.send_message(call.from_user.id, '❇️ Выбор сделан!\n⌛️ Ожидайте выбора второго игрока!')

            elif item[1] == item[2]:
                await bot.send_message(call.from_user.id,"🥇🎗 Вы победили в матче!")

                await bot.send_message(match_id, '⛔️ Вы проиграли в матче!')
                
                for user in db.get_game_information(match_id):
                    db.balance_plus(user[5]*2-db.get_comission(), user[3])

                db.delete_game(match_id)
                db.delete_results(match_id)
                
            elif item[1] != item[2]:
                await bot.send_message(call.from_user.id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....")
                await bot.send_message(match_id, "📛 Выборы не совпадают!\n\n🔰 Создаю арбитраж.....\n\n‼️ Ожидайте когда с вами свяжется администратор!")

                db.update_status_arbitrage(call.from_user.id)
                db.update_status_arbitrage(match_id)
                
                await asyncio.sleep(2)

                await Arbitration.proofs.set()

                await bot.send_message(call.from_user.id, '⚠️ Пришлите следующим сообщением все доказательства вашей победы(фото, видео): ')

                db.delete_results(match_id)



@dp.message_handler(state= Arbitration.proofs)
async def arbitrage_proofs(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        match_id = data["match_index"]
    
    ikb = InlineKeyboardMarkup(row_width=1)
    ikb.add(InlineKeyboardButton("♻️ Снять ограничения", callback_data=arbitrage_cb.new(id= f"index_{match_id}", action = "end")))

    for item in db.get_game_information(match_id):
        await bot.send_message(cfg.ADMIN, f'''🔰 Новый арбитраж!

1️⃣ Первый игрок:
🆔 ID: {item[1]}
📱 Username: @{item[2]}

2️⃣ Второй игрок:
🆔 ID: {item[3]}
📱 Username: @{item[4]}

🎲 Сумма ставки: {item[5]} р

⌛️ Ожидайте доказательства от участников арбитража!
 
    
⬇️ Воспользуйтесь кнопкой ниже если арбитраж закрыт''',
                                    reply_markup= ikb)
    
    await bot.forward_message(cfg.ADMIN, message.from_user.id, message.message_id)

    await bot.send_message(message.from_user.id, '📨 Ваши доказательства отправлены на рассмотрение!')

    await state.finish()
        

@dp.callback_query_handler(arbitrage_cb.filter(action="end"))
async def end_arbitrage(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    match_id = int(str(callback_data["id"]).split("_")[1])

    db.update_status_free(match_id)
    db.update_status_free(db.get_joiner(match_id))

    await call.answer("✅ Успешно выполнено!",show_alert=True)

    await bot.send_message(match_id, "❇️ С вас сняты все ограничения!")
    await bot.send_message(db.get_joiner(match_id), "❇️ С вас сняты все ограничения!")

    db.delete_game(match_id)
    
    await bot.delete_message(call.from_user.id, call.message.message_id)