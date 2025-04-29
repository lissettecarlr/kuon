import threading
import queue
from typing import List, Optional, Iterator, Union, Dict, Any
from loguru import logger
import yaml

from chat_engines import MemoryChatAssistant
from tts_engines import AliyunStreamEngine, TextToSpeechEngine

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {"tts": {"enabled": False, "engine": "aliyun"}}

class AIAssistant: 
    def __init__(
        self,
        chat_engine: Optional[MemoryChatAssistant] = None,
        tts_engine: Optional[TextToSpeechEngine] = None,

    ):
 
        self.chat_engine = chat_engine
        self.tts_engine = tts_engine
        self.tts_input_queue = queue.Queue()
        
        # 处理响应的线程
        self.chat_thread_running = False # AI对话线程
        self.tts_thread_running = False # TTS线程
        self.tts_thread = None
        self.chat_thread = None
        
 
    def _chat_thread_function(self, response_stream: Iterator[str]) -> None:
        self.chat_thread_running = True
        """处理流式响应"""
        print("KUON: ", end="", flush=True)
        
        # 将响应分成句子或短语
        buffer = ""
        full_response = ""
        
        for chunk in response_stream:
            buffer += chunk
            full_response += chunk
            print(chunk, end="", flush=True)
            
            # 如果有TTS引擎，则将内容存入tts_input_queue
            if self.tts_engine is not None:
                separators = ["。", "！", "？", ".", "!", "?", "\n"]
                for sep in separators:
                    if buffer.endswith(sep):
                        self.tts_input_queue.put(buffer)
                        buffer = ""

            # 如果被修改了标志位，则直接退出
            if self.chat_thread_running == False:
                return
            
        # 如果缓冲区中还有内容，也推送到队列
        if buffer and self.tts_engine is not None:
                self.tts_input_queue.put(buffer)
        
        # 标记响应结束
        self.tts_input_queue.put(None)
        print()
    
    def _tts_thread_function(self) -> None:
        """文本转语音的线程函数"""
        
        if self.tts_engine is None:
            logger.error("意外启动TTS线程")
            return
        
        self.tts_thread_running = True 
        while self.tts_thread_running:
            try:
                text = self.tts_input_queue.get(timeout=1)
                if text is None: 
                    break
             
                # 将文本转换为语音并播放
                self.tts_engine.text_to_speech(text)
                self.tts_input_queue.task_done()

            except queue.Empty:
                continue
        self.tts_engine.complete()
    
    def start_interactive_session(self) -> None:
        """开始交互式会话"""
        print("开始对话 (输入 'exit' 或 'quit' 退出)")
        
        while True:
            # 只接受文本输入
            text = input("\n你: ")
            if text.lower() in ['exit', 'quit']:
                # 确保在退出前停止所有线程
                self.chat_thread_running = False
                self.tts_thread_running = False
                if self.tts_engine:
                    self.tts_engine.stop()
                break

            # 退出上一次的AI对话线程
            if self.chat_thread and self.chat_thread.is_alive():
                logger.debug("退出上一次的AI对话线程")
                self.chat_thread_running = False

            # 当新输入内容的时候，关闭线程，重置TTS
            if self.tts_thread and self.tts_thread.is_alive():
                logger.debug("退出上一次的TTS线程")
                self.tts_thread_running = False
                self.tts_engine.stop()
            
            # AI对话线程
            self.chat_thread = threading.Thread(
                target=self._chat_thread_function,
                args=(self.chat_engine.chat(text),)
            )
            self.chat_thread.start()

            # TTS线程
            ## 如果TTS引擎存在，则启动TTS线程
            if self.tts_engine is not None:
                self.tts_engine.init()
                self.tts_thread = threading.Thread(target=self._tts_thread_function)
                self.tts_thread.start()
            
            # 等待AI回复完成
            self.chat_thread.join()
            
    
    def exit(self) -> None:
        """退出并清理资源"""
        self.tts_thread_running = False
        self.chat_thread_running = False
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception as e:
                logger.debug(f"停止TTS引擎时出错: {e}")
        
        # 退出TTS引擎
        if hasattr(self.tts_engine, 'exit'):
            try:
                self.tts_engine.exit()
            except Exception as e:
                logger.debug(f"退出TTS引擎时出错: {e}")
        
        self.chat_engine.exit()
        print("会话已结束")      


def main():
    config = load_config()

    tts_enabled = config["tts"]["enabled"]
     
    chat_engine = MemoryChatAssistant(
        chat_model_name="gpt-4.1",
        use_tts_prompt=tts_enabled
    )
    
    tts_engine = None
    if config["tts"]["enabled"]:
        if config["tts"]["engine"] == "aliyun":
            tts_engine = AliyunStreamEngine()
        else:
            logger.warning(f"不支持的TTS引擎: {config['tts']['engine']}")
    
    # 创建AI助手实例
    assistant = AIAssistant(
        chat_engine=chat_engine,
        tts_engine=tts_engine
    )
    
    try:
        assistant.start_interactive_session()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        assistant.exit()

if __name__ == "__main__":
    main()

