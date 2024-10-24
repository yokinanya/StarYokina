import random
from pydantic import BaseModel
import os
import json

VOICES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "voices"))
GROUP_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "data.json"))


class VoiceFile(BaseModel):
    name: str
    file_name: str
    tag: str


class Voice(BaseModel):
    resource_name: str
    voices: list[VoiceFile]

    def get_random_voice(self) -> str:
        result = self.voices
        RESOURCE_FOLDER = os.path.abspath(
            os.path.join(VOICES_FOLDER, self.resource_name)
        )
        voice = os.path.abspath(
            os.path.join(RESOURCE_FOLDER, random.choice(result).file_name)
        )
        return voice


class Resources:
    def __init__(self):
        with open(GROUP_DATA, "r") as f:
            self.data = json.load(f)

    def isEnabled(self, groupid):
        return self.data[groupid]["enabled"]

    def getResource(self, groupid):
        return self.data[groupid]["resource"]

    def updateData(self, groupid, enabled_value=False, resource_value="Miya按钮"):
        self.data[groupid] = {"enabled": enabled_value, "resource": resource_value}
        with open(GROUP_DATA, "w") as f:
            json.dump(self.data, f)
