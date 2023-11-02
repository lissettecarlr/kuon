
import requests
import numpy as np

class OnlineTTS():
    def __init__(self,url) -> None:
        self.url = url

    def run(self,text,speaker="kt",language='简体中文', speed=1,save_path:str=None):
        url = self.url
        response = requests.post(url, json= 
                                 {
                                     "text": text,
                                     "speaker":speaker,
                                     "language":language,
                                     "speed":speed
                                }
        )
        if response.status_code == 200:
            data = response.json()
            if data["result"] == "Success":
                rate = data["rate"]
                audio = np.array(data["audio"], dtype=np.float32)
                if save_path != None:
                    import scipy.io.wavfile as wavf
                    wavf.write(save_path,rate, audio)
                    #print("tts转换完成：{}".format(aduio_path))
                    # return "Success",save_path
                # else:
                    #print("tts转换完成")
                    # 和offline通义输出格式
                output=[rate,audio]
                return "Success",output
            
            #print("tts转换失败：{}".format(data["message"]))
            return "Fail",data["message"]
        else:
            print("请求错误,status_code:{}", response.status_code)
            return "Fail","请求错误"        

