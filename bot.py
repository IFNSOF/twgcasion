import telebot
import sqlite3
import random

# Ваш токен Telegram-бота
TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Функция для добавления пользователя в базу данных
def add_user(user_id):
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)', (user_id, 100))  # Стартовый баланс
    conn.commit()
    conn.close()

# Функция для получения баланса
def get_balance(user_id):
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Функция для обновления баланса
def update_balance(user_id, new_balance):
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance=? WHERE user_id=?', (new_balance, user_id))
    conn.commit()
    conn.close()

# Команда старт
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user(user_id)  # Добавляем пользователя в БД, если его еще нет
    balance = get_balance(user_id)
    bot.send_message(message.chat.id, f'Добро пожаловать в казино! Ваш баланс: {balance} монет.')
    show_game_buttons(message)

# Функция для показа кнопок игры
def show_game_buttons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Играть в кубики', 'Мой баланс')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)

# Обработчик кнопки "Играть в кубики"
@bot.message_handler(func=lambda message: message.text == 'Играть в кубики')
def play_dice(message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    
    if balance < 10:
        bot.send_message(message.chat.id, 'Недостаточно средств для игры. Минимальная ставка — 10 монет.')
        return

    # Ставка
    bet = 10
    user_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)

    bot.send_message(message.chat.id, f'Вы выбросили: {user_roll}, Бот выбросил: {bot_roll}')
    
    if user_roll > bot_roll:
        balance += bet
        bot.send_message(message.chat.id, f'Вы выиграли! Ваш новый баланс: {balance} монет.')
    elif user_roll < bot_roll:
        balance -= bet
        bot.send_message(message.chat.id, f'Вы проиграли. Ваш новый баланс: {balance} монет.')
    else:
        bot.send_message(message.chat.id, 'Ничья! Баланс не изменился.')

    update_balance(user_id, balance)
    show_game_buttons(message)

# Обработчик кнопки "Мой баланс"
@bot.message_handler(func=lambda message: message.text == 'Мой баланс')
def my_balance(message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    bot.send_message(message.chat.id, f'Ваш текущий баланс: {balance} монет.')
    show_game_buttons(message)

# Запуск бота
bot.polling(none_stop=True)
