import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('database.db')

# Создаем курсор для выполнения запросов
c = conn.cursor()

# Создаем таблицу
c.execute('''CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER
)''')

# Сохраняем изменения в базе данных
conn.commit()

# Закрываем соединение с базой данных
conn.close()
