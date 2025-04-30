from mcp.server import FastMCP
import httpx
import os
from dotenv import load_dotenv
import pytz

# 加载环境变量
load_dotenv()

# 初始化 FastMCP 服务器
server = FastMCP(port=23333)


### 时间 #####################################################
@server.tool()
def get_current_time() -> str:
    """获取当前北京时间，包括年月日和星期几"""
    from datetime import datetime
    
    weekdays = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    
    # 获取北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz)
    weekday = weekdays[now.weekday()]
    return f"{now.year}年{now.month}月{now.day}日 {weekday} {now.hour}:{now.minute}:{now.second}"


###天气######################################################

# 城市名映射
CITY_MAP = {
    "北京": "beijing",
    "上海": "shanghai",
    "广州": "guangzhou",
    "深圳": "shenzhen",
    "成都": "chengdu",
    "杭州": "hangzhou",
    "南京": "nanjing",
    "武汉": "wuhan",
    "西安": "xian",
    "重庆": "chongqing",
    "苏州": "suzhou",
    "天津": "tianjin",
    "长沙": "changsha",
    "郑州": "zhengzhou",
    "青岛": "qingdao",
    "厦门": "xiamen",
    "大连": "dalian",
    "宁波": "ningbo",
    "福州": "fuzhou",
    "济南": "jinan"
}

def convert_city_name(city: str) -> str:
    """转换城市名为英文"""
    return CITY_MAP.get(city, city.lower())

@server.tool()
async def get_weather(city: str="成都"):
    """获取指定城市的天气信息,当不指定城市时，默认使用成都
    Args:
        city: 城市名称（中文),当不指定时，默认使用成都
    Returns:
        dict: 包含天气信息
        {
            天气:"阵雨"
            温度:16.94
            湿度:88
            风速:4
            城市:"成都"
        }
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise ValueError("缺少 OPENWEATHERMAP_API_KEY 环境变量")

    # 转换城市名为英文
    english_city = convert_city_name(city)
    params = {
        "q": english_city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            return {
                "天气": data["weather"][0]["description"],
                "温度": data["main"]["temp"],
                "湿度": data["main"]["humidity"],
                "风速": data["wind"]["speed"],
                "城市": city
            }
            
    except Exception as e:
        raise Exception(f"获取天气信息失败：{str(e)}")

@server.tool()
async def get_weather_forecast(
    city: str="成都",
    days: int = 5,
) -> dict:
    """获取指定城市的天气预报信息,当不指定城市时，默认使用成都
    
    Args:
        city: 城市名称（中文）,当不指定时，默认使用成都
        days: 预报天数（最多5天）,当不指定时，默认使用5天

    Returns:
        dict: 包含天气预报信息
        {
            "数据说明": "最近2天的天气情况",
            "天气情况": [
                {
                    "时间": "2025-04-29",
                    "天气": "多云/阴，多云/小雨",
                    "最低温度": 16.36,
                    "最高温度": 20.67,
                    "湿度": 69,
                    "风速": 3.2,
                    "城市": "成都"
                },
                {
                    "时间": "2025-04-30",
                    "天气": "阴，多云",
                    "最低温度": 17.8,
                    "最高温度": 27.38,
                    "湿度": 48,
                    "风速": 2.83,
                    "城市": "成都"
                }
            ]
        }
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise ValueError("缺少 OPENWEATHERMAP_API_KEY 环境变量")

    # 转换城市名为英文
    english_city = convert_city_name(city)
    
    params = {
        "q": english_city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn",
        "cnt": min(days * 8, 40)
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api.openweathermap.org/data/2.5/forecast",
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            forecasts = {}
            for item in data["list"]:
                date = item["dt_txt"].split()[0]
                if date not in forecasts:
                    forecasts[date] = {
                        "temp_min": float("inf"),
                        "temp_max": float("-inf"),
                        "descriptions": set(),
                        "humidity": [],
                        "wind_speed": []
                    }
                
                daily = forecasts[date]
                daily["temp_min"] = min(daily["temp_min"], item["main"]["temp"])
                daily["temp_max"] = max(daily["temp_max"], item["main"]["temp"])
                daily["descriptions"].add(item["weather"][0]["description"])
                daily["humidity"].append(item["main"]["humidity"])
                daily["wind_speed"].append(item["wind"]["speed"])

            result = {
                "数据说明": f"最近{days}天的天气情况",
                "天气情况": []
            }
            
            for date, daily in list(forecasts.items())[:days]:
                result["天气情况"].append({
                    "时间": date,
                    "天气": "/".join(daily["descriptions"]),
                    "最低温度": round(daily["temp_min"], 2),
                    "最高温度": round(daily["temp_max"], 2),
                    "湿度": round(sum(daily["humidity"]) / len(daily["humidity"])),
                    "风速": round(sum(daily["wind_speed"]) / len(daily["wind_speed"]), 2),
                    "城市": city
                })
            
            return result
            
    except Exception as e:
        raise Exception(f"获取天气预报信息失败：{str(e)}")










if __name__ == "__main__":
    server.run()