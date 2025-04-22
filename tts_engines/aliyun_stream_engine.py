import time
import pyaudio
import dashscope
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
from dashscope.audio.tts_v2 import *
import os
from tts_engines.base import TextToSpeechEngine

from loguru import logger
import sys
# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")


class AliyunStreamCallback(ResultCallback):
    _player = None
    _stream = None
    _audio_data_received = False

    def on_open(self):
        """当和服务端建立连接完成后，该方法立刻被回调"""
        logger.debug(" TTS websocket is open.")
        self._player = pyaudio.PyAudio()
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=22050, output=True
        )
        # 音频数据是否接收
        self._audio_data_received = False

    def on_event(self, message):
        """当服务有回复时会被回调"""
        pass

    def on_complete(self):
        """当所有合成数据全部返回后被回调"""
        logger.debug("TTS 完成")

    def on_error(self, message: str):
        logger.error(f"TTS 错误, {message}")

    def on_close(self):
        """当服务已经关闭连接后被回调。"""
        logger.debug("TTS websocket is closed.")
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._player:
            self._player.terminate()

    def stop(self):
        """强制停止当前播放的音频"""
        logger.debug("强制停止TTS播放")
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._player:
            self._player.terminate()
            self._player = None
        self._audio_data_received = False

    def on_data(self, data: bytes) -> None:
        """	当服务器有合成音频返回时被回调"""
        if self._stream:
            self._stream.write(data)
        self._audio_data_received = True

    def is_audio_data_received(self):
        """判断是否正在接收音频数据"""
        return self._audio_data_received


class AliyunStreamEngine(TextToSpeechEngine):
    """阿里云流式文本转语音引擎"""
    
    def __init__(self, model="cosyvoice-v1", voice="longxiaochun", api_key=None):
        """
        初始化阿里云流式TTS引擎
        
        Args:
            model: 语音模型
            voice: 声音类型
            api_key: API密钥，如果为None则从环境变量获取
        """
        # 设置API密钥
        if api_key:
            dashscope.api_key = api_key
        else:
            dashscope.api_key = os.getenv("ALIYUN_ACCESS_KEY_ID")
            
        self.model = model
        self.voice = voice
        self.callback = AliyunStreamCallback()
        self.synthesizer = None
        self.init()
    
    def init(self):
        """初始化合成器"""
        self.synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=self.voice,
            format=AudioFormat.PCM_22050HZ_MONO_16BIT,
            callback=self.callback,
        )
    
    def text_to_speech(self, text: str):
        """
        将文本转换为语音并立即播放
        Args:
            text: 待转换的文本  
        """
        if self.synthesizer is None:
            logger.error("合成器未初始化，请先初始化合成器")
            return
        # 调用流式API
        self.synthesizer.streaming_call(text)
 
    def stop(self):
        """强制停止当前TTS播放和合成"""
        if self.synthesizer is None:
            logger.debug("没有活跃的合成器，无需停止")
            return
        
        logger.debug("开始强制停止TTS流程...")
        if self.synthesizer is not None:
            self.synthesizer.streaming_cancel()
 
        logger.debug("TTS已完全停止，可以开始新的合成")
  
    def complete(self):
        """标识文本已经传输完毕，结束任务"""
        if not self.synthesizer:
            return
        self.synthesizer.streaming_complete()
        self.synthesizer = None  

    def exit(self):
        """退出并清理资源"""
        try:
            self.stop()
        except Exception as e:
            logger.debug(f"退出TTS引擎时出错: {e}")
        finally:
            self.synthesizer = None


