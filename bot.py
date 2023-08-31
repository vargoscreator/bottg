import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot, types
from aiogram import Bot, Dispatcher


bot = Bot(token="tokenherelink")

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)



def goods_list(message):
    try:
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM goods")
        myresult = cursor.fetchall()
        markup = types.InlineKeyboardMarkup(row_width=1)
        if myresult:
            print(myresult)
            for x in myresult:
                item = types.InlineKeyboardButton(
                    f"{x[1]}", callback_data=f'item_{x[0]}')
                markup.add(item)
                if x[0] == 1:
                    break
            next = types.InlineKeyboardButton(
                            f">", callback_data=f'next_page_{x[0]}')
            markup.add(next)
            return bot.send_message(
                    message.chat.id, 'Привет!👋 Рад тебя видеть! :)\nДля приобретения товара - выбери его из списка доступных:', reply_markup=markup)
        else:
            return bot.send_message(
                    message.chat.id, 'Привет! К сожалению товаров пока что нет!', reply_markup=markup)
    except Exception as e:
        return bot.send_message(
                    message.chat.id, 'Привет! К сожалению товаров пока что нет!', reply_markup=markup)




@dp.message_handler(commands="start", state="*")
async def start_handler(message: types.Message, state: FSMContext):
    try:
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        used_id = message.chat.id
        cursor.execute("""CREATE TABLE IF NOT EXISTS goods(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            product_name varchar(255),
                            product_descr varchar(255),
                            product_photo varchar(255),
                            product_price varchar(255)
                        )""")
        connect.commit()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS user_{used_id}(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            product_name varchar(255)
                        )""")
        connect.commit()
        await goods_list(message)
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id,
                           text=e)
        
        
@dp.callback_query_handler(lambda callback: "back_to_goods_list" in callback.data)
async def back_handler(callback: types.callback_query):
    try:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await goods_list(callback.message)
    except Exception as e:
        print(e)
        
        
        

@dp.callback_query_handler(lambda callback: "next_page_" in callback.data)
async def back_handler(callback: types.callback_query):
    try:
        page = callback.data.replace('next_page_', '')
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM goods")
        myresult = cursor.fetchall()
        markup = types.InlineKeyboardMarkup(row_width=2)
        want_page = 1 
        showpage = want_page + int(page)
        back_page = int(page) - want_page
        check_last_page = True
        for x in myresult:
            data = x[0]
            next_page = data - 1
            if data > showpage:
                if int(page) != 0:
                    backpage = types.InlineKeyboardButton(
                                        f"<", callback_data=f'next_page_{back_page}')
                    markup.add(backpage)
                next = types.InlineKeyboardButton(
                                    f">", callback_data=f'next_page_{next_page}')
                markup.add(next)
                check_last_page = False
                break
            if data > int(page):
                item = types.InlineKeyboardButton(f"{x[1]}", callback_data=f'item_{data}')
                markup.add(item)
        if check_last_page:
            backpage = types.InlineKeyboardButton(
                f"<", callback_data=f'next_page_{back_page}')
            markup.add(backpage)
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)

    except Exception as e:    
        await bot.send_message(chat_id=callback.chat.id,
                           text="Нет доступных товаров!")


@dp.callback_query_handler(lambda callback: "item_" in callback.data)
async def back_handler(callback: types.callback_query):
    try:
        page = int(callback.data.replace('item_', ''))
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute(
                f"SELECT * FROM goods WHERE id='{page}'")
        myresult = cursor.fetchall()
        for x in myresult:
            product_id = x[0]
            product_name = x[1]
            product_descr = x[2]
            product_photo = x[3]
            product_price = x[4]
        
        used_id = callback.message.chat.id
        cursor.execute(
                f"SELECT * FROM user_{used_id}")
        myresults = cursor.fetchall()
        if myresults:
            for x in myresults:
                name = x[1]
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        if myresults and str(name) == str(product_name):
            buygoods = types.InlineKeyboardButton(
                        f"Отказатся", callback_data=f'delete_{product_id}')
            markup.add(buygoods)
            backpage = types.InlineKeyboardButton(
                        f"<", callback_data=f'back_to_goods_list')
            markup.add(backpage)
            await bot.send_photo(chat_id=callback.message.chat.id, photo=product_photo, caption=f"Вы уже купили {product_name}", reply_markup=markup)
        else:
            buygoods = types.InlineKeyboardButton(
                            f"Купить", callback_data=f'buy_{product_id}')
            markup.add(buygoods)
            backpage = types.InlineKeyboardButton(
                            f"<", callback_data=f'back_to_goods_list')
            markup.add(backpage)
            await bot.send_photo(chat_id=callback.message.chat.id, photo=product_photo, caption=f"Название: {product_name}\nЦена: {product_price}\n\n{product_descr}", reply_markup=markup)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except Exception as e:    
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=e)
        
@dp.callback_query_handler(lambda callback: "buy_" in callback.data)
async def back_handler(callback: types.callback_query):
    try:
        buy_id = int(callback.data.replace('buy_', ''))
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        user_id = callback.message.chat.id
        cursor.execute(f"SELECT * FROM goods WHERE id='{buy_id}'")
        result = cursor.fetchall()
        for x in result:
            name__prod = x[1]
            id__prod = x[0]    
        cursor.execute(
            f"INSERT INTO user_{user_id} (product_name) VALUES ('{name__prod}')")
        connect.commit() 
        markup = types.InlineKeyboardMarkup(row_width=1)
        backpage = types.InlineKeyboardButton(
                        f"<", callback_data=f'item_{id__prod}')
        markup.add(backpage)
        await bot.send_message(callback.message.chat.id, f"Вы успешно купили {name__prod}", reply_markup=markup)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except Exception as e:    
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=e)


@dp.callback_query_handler(lambda callback: "delete_" in callback.data)
async def back_handler(callback: types.callback_query):
    try:
        buy_id = int(callback.data.replace('delete_', ''))
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        user_id = callback.message.chat.id
        cursor.execute(f"SELECT * FROM goods WHERE id='{buy_id}'")
        result = cursor.fetchall()
        for x in result:
            name__prod = x[1]
            id__prod = x[0]    
        cursor.execute(
            f"DELETE FROM user_{user_id} WHERE product_name='{name__prod}'")
        connect.commit() 
        markup = types.InlineKeyboardMarkup(row_width=1)
        backpage = types.InlineKeyboardButton(
                        f"<", callback_data=f'item_{id__prod}')
        markup.add(backpage)
        await bot.send_message(callback.message.chat.id, f"Вы успешно отказались от покупки товара {name__prod}.", reply_markup=markup)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    except Exception as e:    
        await bot.send_message(chat_id=callback.message.chat.id,
                           text=e)


executor.start_polling(dp, skip_updates=True)
