import sqlite3
from typing import Optional
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
        """
        根据提供的模型创建表
        模型是包含表名和字段列表的字典
        """
        table_name = model["table_name"]
        columns = ", ".join(model["columns"])
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()

    def insert_data(self, table_name: str, data: dict) -> None:
        """插入数据到表中"""
        columns = ", ".join(list(data.keys()))
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        self.cursor.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values
        )
        self.conn.commit()

    def update_data(self, table_name: str, data: dict, condition: str) -> None:
        """更新数据到表中"""
        set_clause = ", ".join([f"{key} = ?" for key in data])
        values = tuple(data.values())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def execute(self, query: str, params: Optional[tuple] = None) -> list[tuple]:
        """查询数据"""
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def delete_data(self, table_name: str) -> None:
        """清空表数据(不会重置自增)"""
        self.cursor.execute(f"DELETE FROM {table_name}")
        self.conn.commit()
        self.close()

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


class SettingsDB(SQLiteDB):
    def __init__(self, gid: int, node: str, value: str) -> None:
        super().__init__("settings")
        self._gid = gid
        self._node = node
        self._value = value
        data_model = {
            "table_name": "settings",
            "columns": [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "gid INTEGER NOT NULL",
                "node TEXT NOT NULL",
                "value TEXT NOT NULL",
            ],
        }
        self.create_table(data_model)

    @property
    def node(self) -> str:
        return self._node

    @node.setter
    def node(self, node) -> None:
        self._node = node

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value) -> None:
        self._value = value

    def set(self, value) -> None:
        try:
            self.insert_data(
                "settings", {"gid": self._gid, "node": self._node, "value": value}
            )
        except:
            self.update_data(
                "settings",
                {"value": value},
                f"gid = {self._gid} AND node = {self._node}",
            )

    def get(self) -> list[tuple]:
        return self.execute(
            f"SELECT value FROM settings WHERE gid=? AND node=?",
            (self._gid, self._node),
        )


# 使用示例
# db = SQLiteDB("my_database.db")

# 定义一个表模型
# user_model = {
#     "table_name": "users",
#     "columns": ["id INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT", "age INTEGER"],
# }

# 创建表
# db.create_table(user_model)

# 插入数据
# db.insert_data("users", {"name": "Alice", "age": 30})

# 更新数据
# db.update_data("users",{"name": "Alice", "age": 30}, "id=114514")

# 清空表数据(不会重置自增)
# db.delete_data(users)

# 查询数据
# data = db.execute("SELECT * FROM users WHERE name = ?", ("Alice",))
