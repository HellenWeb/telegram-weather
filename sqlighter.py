# Modules

import sqlite3

# Class


class SQLighter:
    def __init__(self, db_name):
        self.connect = sqlite3.connect(db_name)
        self.cursor = self.connect.cursor()

    def show_info(self, user_id):
        with self.connect:
            return self.cursor.execute(
                "SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)
            ).fetchall()

    def inster_name(self, user_id, name):
        with self.connect:
            self.cursor.execute(
                f"INSERT INTO `users` (`user_id`, `name`) VALUES (?, ?)",
                (user_id, name),
            )

    def inster_city(self, user_id, city):
        with self.connect:
            self.cursor.execute(
                f"INSERT INTO `users` (`user_id`, `city`) VALUES (?, ?)",
                (user_id, city),
            )

    def update_name(self, user_id, name):
        with self.connect:
            self.cursor.execute(
                f"UPDATE `users` SET `name` = ? WHERE `user_id` = ?", (name, user_id)
            )

    def update_city(self, user_id, city):
        with self.connect:
            self.cursor.execute(
                f"UPDATE `users` SET `city` = ? WHERE `user_id` = ?", (city, user_id)
            )
