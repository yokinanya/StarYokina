import random
from pydantic import BaseModel
from typing import Optional

from hoshimiya.utils.DataBaseUtils import SQLiteDB

class BaseCave(BaseModel):
    id: int
    title: Optional[str]
    image: Optional[str]


class CaveData(BaseModel):
    """
    回声洞库
    TODO: 多类别存储
    """

    category: str = "default"
    caves: list[BaseCave] = []

    def get_random_cave(self) -> BaseCave:
        db = SQLiteDB(plugin_name="cave")
        cave_model = {
            "table_name": "caves",
            "columns": [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "title TEXT",
                "image TEXT",
                "category DEFAULT 'default'",
            ],
        }
        db.create_table(cave_model)

        # 检查是否需要插入测试数据
        count = db.execute("SELECT COUNT(*) FROM caves")
        if count[0] == 0:
            return BaseCave(
                id=1,
                title="这是一条测试回声洞",
                image=None,
            )

        # 查询所有 caves
        rows = db.execute(
            "SELECT id, title, image FROM caves WHERE category = ?",
            (self.category,),
        )

        # 关闭连接
        db.close()

        # 随机选择一行
        random_cave_data = random.choice(rows)

        # 创建 BaseCave 实例并返回
        return BaseCave(
            id=random_cave_data[0],
            title=random_cave_data[1],
            image=random_cave_data[2],
        )
