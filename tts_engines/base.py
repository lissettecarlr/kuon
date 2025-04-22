"""
文本转语音引擎的基类和默认实现
"""

import abc

class TextToSpeechEngine(abc.ABC):
    """文本转语音引擎的抽象基类"""
    
    @abc.abstractmethod
    def init(self) -> None:
        """初始化引擎"""
        pass
        
    @abc.abstractmethod
    def text_to_speech(self, text: str) -> bytes:
        """将文本转换为语音数据"""
        pass
    
    @abc.abstractmethod
    def complete(self) -> None:
        """完成所有待处理的合成任务，对于流式引擎很重要"""
        pass
    
    @abc.abstractmethod
    def stop(self) -> None:
        """强制停止当前正在进行的TTS合成和播放"""
        pass
    
    @abc.abstractmethod
    def exit(self) -> None:
        """退出并清理资源"""
        pass
