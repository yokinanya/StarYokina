from hoshimiya.utils.DataBaseUtils import SQLiteDB


class GroupVerifyConfig:
    def __init__(self, isEnable=False, isAuto=False, Password=""):
        self.isEnable = isEnable
        self.isAuto = isAuto
        self.Password = Password

    def getGroupConfig(self, gid: int) -> None:
        db = SQLiteDB(plugin_name="groupverify")
        data_model = {
            "table_name": "groupverify",
            "columns": [
                "gid INTEGER PRIMARY KEY NOT NULL",
                "isEnable INTEGER",
                "isAuto INTEGER",
                "Password TEXT DEFAULT ''",
            ],
        }
        db.create_table(data_model)
        data = db.execute("SELECT * FROM groupverify WHERE gid=?", (gid,))

        if not data:
            data = {
                "gid": gid,
                "isEnable": self.isEnable,
                "isAuto": self.isAuto,
                "Password": self.Password,
            }
            db.insert_data("groupverify", data)
        else:
            self.isEnable = bool(data[0][1])
            self.isAuto = bool(data[0][2])
            self.Password = data[0][3]
        db.close()
        return None

    def updateConfig(self, gid: int):
        db = SQLiteDB(plugin_name="groupverify")
        data = {
            "isEnable": self.isEnable,
            "isAuto": self.isAuto,
            "Password": self.Password,
        }
        db.update_data("groupverify", data, f"gid={gid}")
        db.close()
