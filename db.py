import sqlite3
from pathlib import Path
from typing import Optional
import hashlib

class SqliteDb:
    def __init__(self, db_path: str = "test.db"):
        self.db_path = db_path
    
    def _get_connection(self):
        """Создает соединение с БД"""
        return sqlite3.connect(self.db_path)
    
    @staticmethod
    def _hash_username(username: str) -> str:
        """Хеширует username"""
        if username is None:
            return ""
        return hashlib.sha256(username.encode()).hexdigest()
    
    def add_user(self, telegram_id: int, username: Optional[str] = None) -> bool:
        """
        Добавляет пользователя в таблицу users
        
        Returns:
            bool: True если пользователь успешно добавлен,
                  False если:
                  - telegram_id уже существует
                  - username уже занят другим пользователем
                  - произошла другая ошибка целостности
        """
        username_hash = self._hash_username(username) if username else ""
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (telegram_id, username_hash) VALUES (?, ?)",
                    (telegram_id, username_hash)
                )
                conn.commit()
                
                if cursor.rowcount == 0:
                    # Проверяем, почему не добавилось
                    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
                    if cursor.fetchone():
                        print(f"Пользователь с telegram_id {telegram_id} уже существует")
                    else:
                        cursor.execute("SELECT 1 FROM users WHERE username_hash = ?", (username_hash,))
                        if cursor.fetchone():
                            print(f"Username {username} уже используется другим пользователем")
                
                return cursor.rowcount > 0
                
        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности БД: {e}")
            return False
        
    def user_exists(self, telegram_id: int) -> bool:
        """
        Проверяет существует ли пользователь с указанным telegram_id
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            bool: True если пользователь существует, False если нет
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            return cursor.fetchone() is not None
        
    def username_exists(self, username: str) -> bool:
        """
        Проверяет существует ли пользователь с указанным username
        
        Args:
            username: Username пользователя (без @)
            
        Returns:
            bool: True если пользователь с таким username существует, False если нет
        """
        if not username:
            return False
        
        username_hash = self._hash_username(username)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE username_hash = ?",
                (username_hash,)
            )
            return cursor.fetchone() is not None
        
    def get_telegram_id_by_username(self, username: str) -> Optional[int]:
        """
        Находит telegram_id пользователя по его username
        """
        if not username:
            return None
        
        username_hash = self._hash_username(username)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT telegram_id FROM users WHERE username_hash = ?",
                (username_hash,)
            )
            result = cursor.fetchone()
            return result[0] if result else None


# Пример использования
if __name__ == "__main__":
    db = SqliteDb("test.db")
    
    # Добавляем первого пользователя
    is_exists = db.user_exists(1234138818)
    print(is_exists)

    # tg_id = db.get_telegram_id_by_username("gottl1eb")
    # print(tg_id)
    