import sqlite3
from typing import Optional
from hoshimiya.utils.DataBaseUtils import SQLiteDB
import datetime

from .config import wife_config


class wifeRecord:
    def __init__(
        self,
        gid: str,
        qid: str,
        wife_id: int = 0,
        times: int = 0,
        date: str = str(datetime.date.today()),
    ) -> None:
        self.gid = gid
        self.qid = qid
        self._wife_id = wife_id
        self._times = times
        self._date = date

    def get_wife(self) -> Optional[int]:
        db = SQLiteDB(plugin_name="today_wife")
        data = db.execute(
            f"SELECT * FROM {"group_" + self.gid} WHERE qid=?", (self.qid,)
        )
        db.close()
        if not data:
            return None
        else:
            self.qid = str(data[0][0])
            self._wife_id = int(data[0][1])
            self._times = int(data[0][2])
            self._date = str(data[0][3])
        return self._wife_id

    def get_bewife(self) -> Optional[int]:
        db = SQLiteDB(plugin_name="today_wife")
        data = db.execute(
            f"SELECT * FROM {"group_" + self.gid} WHERE wife_id=?", (self.qid,)
        )
        db.close()
        if not data:
            return None
        else:
            self.qid = data[0][0]
            self._wife_id = data[0][1]
            self._times = data[0][2]
            self._date = data[0][3]
            return self.qid

    def get_allwife(self) -> list:
        db = SQLiteDB(plugin_name="today_wife")
        data = db.execute(f"SELECT wife_id FROM {"group_" + self.gid} WHERE wife_id!= 0")
        db.close()
        return [row[0] for row in data]

    def check_date(self) -> bool:
        db = SQLiteDB(plugin_name="today_wife")
        data_model = {
            "table_name": "group_" + self.gid,
            "columns": [
                "qid INTEGER PRIMARY KEY NOT NULL",
                "wife_id INTEGER NOT NULL",
                "times INTEGER NOT NULL",
                "date TEXT NOT NULL",
            ],
        }
        db.create_table(data_model)
        data = db.execute(
            f"SELECT * FROM {"group_" + self.gid} WHERE date=?", (self._date,)
        )
        if not data:
            self.reset()
            return False
        db.close()
        return True

    def reset(self) -> None:
        db = SQLiteDB(plugin_name="today_wife")
        db.delete_data("group_" + self.gid)
        db.close()

    def save(self) -> None:
        db = SQLiteDB(plugin_name="today_wife")
        try:
            data = {
                "qid": self.qid,
                "wife_id": self._wife_id,
                "times": self._times,
                "date": self._date,
            }
            db.insert_data("group_" + self.gid, data)
        except sqlite3.IntegrityError:
            data = {
                "wife_id": self._wife_id,
                "times": self._times,
                "date": self._date,
            }
            db.update_data("group_" + self.gid, data, f"qid={self.qid}")
        db.close()

    @property
    def wife_id(self):
        return self._wife_id

    @wife_id.setter
    def wife_id(self, value=int):
        self._wife_id = value

    @property
    def times(self):
        return self._times

    @times.setter
    def times(self, value=int):
        self._times = value


class wifeSettings:
    def __init__(
        self,
        gid: int,
        limit_times: int = wife_config.today_waifu_default_limit_times,
        allow_change_wife: bool = wife_config.today_waifu_default_change_waifu,
    ) -> None:
        self.gid = gid
        self._limit_times = limit_times
        self._allow_change_wife = allow_change_wife

    def initConfig(self) -> None:
        db = SQLiteDB(plugin_name="today_wife")
        data_model = {
            "table_name": "settings",
            "columns": [
                "gid INTEGER PRIMARY KEY NOT NULL",
                "limit_times INTEGER NOT NULL",
                "allow_change_wife INTEGER NOT NULL",
            ],
        }
        db.create_table(data_model)
        db.close()
        return None

    def getConfig(self) -> None:
        db = SQLiteDB(plugin_name="today_wife")
        data = db.execute("SELECT * FROM settings WHERE gid=?", (self.gid,))
        if not data:
            data = {
                "gid": self.gid,
                "limit_times": self._limit_times,
                "allow_change_wife": self._allow_change_wife,
            }
            db.insert_data("settings", data)
        else:
            self._limit_times = data[0][1]
            self._allow_change_wife = bool(data[0][2])
        db.close()
        return None

    def updateConfig(self) -> None:
        db = SQLiteDB(plugin_name="today_wife")
        data = {
            "limit_times": self._limit_times,
            "allow_change_wife": self._allow_change_wife,
        }
        try:
            db.update_data("settings", data, f"gid={self.gid}")
        except sqlite3.OperationalError:
            data = {
                "gid": self.gid,
                "limit_times": self._limit_times,
                "allow_change_wife": self._allow_change_wife,
            }
            db.insert_data("settings", data)
        db.close()
        return None

    @property
    def limit_times(self):
        return self._limit_times

    @limit_times.setter
    def limit_times(self, value: int):
        self._limit_times = value

    @property
    def allow_change_wife(self):
        return self._allow_change_wife

    @allow_change_wife.setter
    def allow_change_wife(self, value: bool):
        self._allow_change_wife = value
