import telebot
from main import Text2ImageAPI
import random
from telebot import types
import sqlite3

DATABASE = 'database.db'
API_TOKEN = 'YOUR BOT TOKEN'
game = False
bot = telebot.TeleBot(API_TOKEN)
moves = ['камень', 'ножницы', 'бумага']
number = ['1', '2', '3', '4', '5']
numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
summ = 0
abc = 0
abcd = 0
abcde = 0


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        if c.fetchone():
            bot.reply_to(message, "Вы уже зарегестрированны")
            return
        else:
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, 30))
            bot.reply_to(message, """Вас приветствует бот с генерацией картинок на рабочий стол!

У этого бота есть несколько команд:
/help - показывет команды
/generate - генерирует картинку. Цена генерации 10 монеток
/balance - просмотр баланса пользователя
/game1 - игра 'Камень, ножницы, бумага'
/game2 - игра 'Угадайка'
/game3 - игра 'Интуиция'

Удачного пользования!""")
        conn.commit()


@bot.message_handler(commands=['help'])
def help(message):
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            bot.reply_to(message, """Вас приветствует бот с генерацией картинок на рабочий стол!

У этого бота есть несколько команд:
/help - показывет команды
/generate - генерирует картинку. Цена генерации 10 монеток
/balance - просмотр баланса пользователя
/game1 - игра 'Камень, ножницы, бумага'
/game2 - игра 'Угадайка'
/game3 - игра 'Интуиция'

Удачного пользования!""")


@bot.message_handler(commands=['generate'])
def echo_message(message):
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            coins = res[1]
            if coins >= 10:
                coins -= 10
                c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
                bot.reply_to(message, "Подождите...")
                api = Text2ImageAPI('https://api-key.fusionbrain.ai/', 'API KEY',
                                    'SECRET KEY')
                model_id = api.get_model()
                uuid = api.generate("Красивая картинка на рабочий стол", model_id)
                images = api.check_generation(uuid)[0]
                img_name = message.from_user.id
                api.decode_image(images, img_name)
                with open(f"img/{img_name}.jpg", 'rb') as img:
                    bot.send_photo(message.chat.id, img)
                conn.commit()
            else:
                bot.reply_to(message, "У вас недостаточно монет")


@bot.message_handler(commands=['balance'])
def balance(message):
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            coins = res[1]
    bot.reply_to(message, f"Ваш баланс: {coins}")


@bot.message_handler(commands=['game1'])
def play_game(message):
    global abcde
    abcde = 1
    bot.reply_to(message,
                 "Давайте сыграем в 'Камень, ножницы, бумага'. Выберите один из вариантов: камень, ножницы, бумага. Когда захотите прекратить напишите /stop")
    # Генерация нового выбора бота для каждого раунда игры
    bot.register_next_step_handler(message, make_choice)


def make_choice(message):
    global abcde
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            coins = res[1]
    bot_choice = random.choice(moves)  # Генерация выбора бота для каждого раунда игры
    player_choice = message.text.lower()
    if player_choice in moves:
        if player_choice == bot_choice:
            bot.reply_to(message, f"Ничья! Я выбрал {bot_choice}. Утешительный приз в 3 монетки")
            coins += 3
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
            if abcde == 1:
                bot.register_next_step_handler(message, make_choice)
        elif (player_choice == "камень" and bot_choice == "ножницы") or (
                player_choice == "ножницы" and bot_choice == "бумага") or (
                player_choice == "бумага" and bot_choice == "камень"):
            bot.reply_to(message, f"Поздравляю! Вы выиграли! Я выбрал {bot_choice}. Ты получил 10 монет!")
            coins += 10
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
            if abcde == 1:
                bot.register_next_step_handler(message, make_choice)
        else:
            bot.reply_to(message, f"Вы проиграли! Я выбрал {bot_choice}.")
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
            if abcde == 1:
                bot.register_next_step_handler(message, make_choice)

    elif message.text == "/stop":
        abcde = 0
        bot.reply_to(message, "Игра завершилась")
    else:
        bot.reply_to(message, "Нужно ввести 'камень','ножницы' или 'бумага'")
        if abcde == 1:
            bot.register_next_step_handler(message, make_choice)
    conn.commit()


@bot.message_handler(commands=['game2'])
def game(message):
    global abcd
    abcd = 1
    bot.reply_to(message, "Давайте сыграем в угадайку. Назовите целое число от 1 до 10. Когда захотите прекратить напишите /stop")
    # Генерация нового выбора бота для каждого раунда игры
    bot.register_next_step_handler(message, choice_number)


def choice_number(message):
    global abcd
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            coins = res[1]
    num = random.choice(numbers)  # Генерация выбора бота для каждого раунда игры
    num = int(num)
    print(num)
    player_num = message.text.lower()
    if player_num.isdigit():
        if player_num in numbers:
            player_num = int(player_num)
            if player_num == num:
                bot.reply_to(message, "Поздравляю! Вы угадали и получаете 16 монет")
                coins += 16
                c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
                if abcd == 1:
                    bot.register_next_step_handler(message, choice_number)
            elif player_num == num + 1 or player_num == num - 1:
                bot.reply_to(message, "Вы почти угадали и получаете 8 монет")
                coins += 8
                c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
                if abcd == 1:
                    bot.register_next_step_handler(message, choice_number)
            else:
                bot.reply_to(message, "Вы проиграли!")
                c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
                if abcd == 1:
                    bot.register_next_step_handler(message, choice_number)
        else:
            bot.reply_to(message, "Нужно ввести целое число от 1 до 10")
            if abcd == 1:
                bot.register_next_step_handler(message, choice_number)
    elif message.text == "/stop":
        abcd = 0
        bot.reply_to(message, "Игра завершилась")
    else:
        bot.reply_to(message, "Вы должны ввести целое число от 1 до 10")
        if abcd == 1:
            bot.register_next_step_handler(message, choice_number)
    conn.commit()


@bot.message_handler(commands=['game3'])
def game3(message):
    global abc
    abc = 1
    bot.reply_to(message, """Давайте сыграем в игру на интуицию. Назовите целое число от 1 до 10
После этого бот тоже выберет число. В случайное время игры вы можете написать /check
Если общее количество очков будет больше 20, но меньше 30, то вы получите монетки
Будьте внимательны, за проигрыш вы теряете 3 монетки""")
    bot.register_next_step_handler(message, guess)


def guess(message):
    global summ
    global abc
    conn = sqlite3.connect('database.db')
    with conn:
        c = conn.cursor()
        user_id = message.from_user.id
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        res = c.fetchone()
        if res is None:
            bot.reply_to(message, "Вы должны зарегестроваться по команде /start")
            return
        else:
            coins = res[1]
    player_number = message.text.lower()
    if player_number.isdigit():
        player_number = int(player_number)
        if player_number > 0 and player_number < 11:
            summ += player_number
            nums = random.randint(1, 10)  # Генерация выбора бота для каждого раунда игры
            summ += nums
            print(summ)
            bot.reply_to(message, "Бот сделал свой ход")
            if abc == 1:
                bot.register_next_step_handler(message, guess)
        else:
            bot.reply_to(message, "Введите целое число от 1 до 10")
            if abc == 1:
                bot.register_next_step_handler(message, guess)
    elif message.text == "/check":
        abc = 0
        if summ > 19 and summ < 25:
            coins += 8
            bot.reply_to(message, f'Число: {summ}. Вы получаете 8 монет')
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
        elif summ > 24 and summ < 31:
            bot.reply_to(message, f'Число: {summ}. Вы получаете 16 монет!')
            coins += 16
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
        else:
            bot.reply_to(message, f'Число: {summ}. Вы теряете 3 монеты')
            coins -= 3
            c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
            if coins < 0:
                coins = 0
                c.execute("INSERT OR REPLACE INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins))
        summ = 0
    else:
        bot.reply_to(message, "Вы должны ввести целое число от 1 до 10")
        if abc == 1:
            bot.register_next_step_handler(message, guess)
    conn.commit()


bot.infinity_polling()
