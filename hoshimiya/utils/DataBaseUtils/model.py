import sqlite3
from dbutils.persistent_db import PersistentDB
from .data import DatabaseConfig


class SQLiteDB(DatabaseConfig):
    def __init__(self, plugin_name):
        # 初始化数据库连接
        super().__init__()
        db_path = self.directory.joinpath(f"{plugin_name}.db")
        pool = PersistentDB(creator=sqlite3, maxusage=None, database=db_path)

        self.conn = pool.connection()
        self.cursor = self.conn.cursor()

    def create_table(self, model: dict) -> None:
        # 根据提供的模型创建表
        # 模型是包含表名和字段列表的字典
        table_name = model["table_name"]
        columns = ", ".join(model["columns"])
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert_data(self, table_name: str, data: dict) -> None:
        # 插入数据到表中
        columns = ", ".join(list(data.keys()))
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        self.cursor.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values
        )
        self.conn.commit()

    def update_data(self, table_name: str, data: dict, condition: str) -> None:
        # 更新数据到表中
        set_clause = ", ".join([f"{key} = ?" for key in data])
        values = tuple(data.values())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def execute(self, query: str, params=None) -> tuple:
        # 查询数据
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def delete_data(self, table_name: str) -> None:
        self.cursor.execute(f"DELETE FROM {table_name}")
        self.conn.commit()
        self.close()

    def close(self):
        # 关闭数据库连接
        self.conn.close()


# 使用示例
# db = SQLiteDB("my_database.db")

# 定义一个表模型
# user_model = {
#     "table_name": "users",
#     "columns": ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"],
# }

# 创建表
# db.create_table(user_model)

# 插入数据
# db.insert_data("users", {"name": "Alice", "age": 30})

# 查询数据
# data = db.execute("SELECT * FROM users WHERE name = ?", ("Alice",))
