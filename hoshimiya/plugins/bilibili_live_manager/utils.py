import json
import os
import httpx


async def send_request(
    method: str, url: str, params: dict, cookies: httpx.Cookies
) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": f"https://live.bilibili.com/{params.get('room_id', '')}",
        "Origin": "https://live.bilibili.com",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient() as client:
        try:
            if method == "POST":
                response = await client.post(
                    url, headers=headers, params=params, cookies=cookies
                )
            else:  # default to GET
                response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "code": -1,
                "message": str(e),
            }  # Return error code -1 for failed requests


async def startLive(room_id: int, area_v2: str, cookies: httpx.Cookies) -> str:
    csrf = cookies.get("bili_jct")
    params = {"csrf": csrf, "room_id": room_id, "area_v2": area_v2, "platform": "web"}
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"

    response_data = await send_request("POST", url, params, cookies)
    return handle_response(response_data)


async def stopLive(room_id: int, cookies: httpx.Cookies) -> str:
    csrf = cookies.get("bili_jct")
    params = {"csrf": csrf, "room_id": room_id}
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"

    response_data = await send_request("POST", url, params, cookies)
    return handle_response(response_data)


async def changeLiveTitle(room_id: int, title: str, cookies: httpx.Cookies) -> str:
    csrf = cookies.get("bili_jct")
    params = {"csrf": csrf, "room_id": room_id, "title": title}
    url = "https://api.live.bilibili.com/room/v1/Room/update"

    response_data = await send_request("POST", url, params, cookies)
    return handle_response(response_data)


async def getLiveAreaList() -> dict:
    url = "https://api.live.bilibili.com/room/v1/Area/getList"
    response_data = await send_request("GET", url, {}, httpx.Cookies())
    return response_data if "data" in response_data else {}


async def areaNametoAreaId(area_name: str) -> int:
    if area_name.isdigit():
        return int(area_name)

    area_list = await getLiveAreaList()
    if not area_list:
        return 0

    for parent_area in area_list.get("data", []):
        for area in parent_area.get("list", []):
            if area["name"] == area_name:
                return area["id"]
    return 0


async def readData(uin: int) -> dict:
    data_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "data.json"))
    try:
        with open(data_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return next((userdata for userdata in data if userdata["uin"] == uin), {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"读取数据时发生错误: {e}")
        return {}


def handle_response(response_data: dict) -> str:
    code = response_data.get("code", -1)
    messages = {
        0: "操作成功",
        65530: "token错误（登录错误）",
        60009: "分区不存在",
        60024: "目标分区需要人脸认证",
        60013: "地区受实名认证限制无法开播",
        -1: "请求失败",
    }
    return messages.get(code, f"操作失败，错误码{code}")


__all__ = ["startLive", "stopLive", "areaNametoAreaId", "readData", "changeLiveTitle"]
