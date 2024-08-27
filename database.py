import sqlite3


class DataBase:
    def __init__(self, db_file):
        # Подключение к базе данных SQLite
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        # Создание таблицы users, если она не существует
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT UNIQUE,  
                user_name TEXT UNIQUE,  
                count INTEGER DEFAULT 0  
            );
            """
        )
        self.connection.commit()

    def add_user(self, user_id: int, user_name: str) -> None:
        try:
            # Добавление нового пользователя с начальным счетчиком 0
            self.cursor.execute(
                'INSERT INTO users (user_id, user_name, count) VALUES (?, ?, ?)',
                (user_id, user_name, 0)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"User with ID {user_id} or name {user_name} already exists.")

    def user_exists(self, user_id: int) -> bool:
        # Проверка, существует ли пользователь в базе данных
        result = self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
        )
        return result.fetchone() is not None

    def update_user_name(self, user_id: int, user_name: str) -> None:
        try:
            # Обновление имени пользователя
            self.cursor.execute(
                'UPDATE users SET user_name = ? WHERE user_id = ?',
                (user_name, user_id)
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"User with name {user_name} already exists.")

    def count(self, user_id: int) -> None:
        # Увеличение счетчика пользователя на 1
        self.cursor.execute(
            'UPDATE users SET count = count + 1 WHERE user_id = ?', (user_id,)
        )
        self.connection.commit()

    def get_user(self, user_id: int = None, user_name: str = None):
        """
        Получение информации о пользователе по user_id или user_name.

        :param user_id: ID пользователя.
        :param user_name: Имя пользователя.
        :return: Кортеж (user_id, user_name, count) или None, если пользователь не найден.
        """
        if user_id is not None:
            # Получение информации по user_id
            result = self.cursor.execute(
                'SELECT user_id, user_name, count FROM users WHERE user_id = ?', (user_id,)
            )
        elif user_name is not None:
            # Получение информации по user_name
            result = self.cursor.execute(
                'SELECT user_id, user_name, count FROM users WHERE user_name = ?', (user_name,)
            )
        else:
            raise ValueError("Необходимо указать user_id или user_name.")

        row = result.fetchone()
        return row if row else None

    def search_users(self, user_id: int = None, user_name: str = None, count: int = None):
        # Формирование SQL запроса с условиями поиска
        query = "SELECT * FROM users WHERE 1=1"
        parameters = []

        if user_id is not None:
            query += " AND user_id = ?"
            parameters.append(user_id)
        if user_name is not None:
            query += " AND user_name LIKE ?"
            parameters.append(f'%{user_name}%')
        if count is not None:
            query += " AND count = ?"
            parameters.append(count)

        result = self.cursor.execute(query, parameters)
        return result.fetchall()

    def get_all_records(self):
        # Получение всех записей и колонок из таблицы users
        result = self.cursor.execute('SELECT * FROM users')
        rows = result.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return columns, rows
