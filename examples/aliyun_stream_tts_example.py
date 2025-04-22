import os
import sys
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts_engines import AliyunStreamEngine
import time

# 使用示例
if __name__ == "__main__":
    engine = AliyunStreamEngine()
    
    test_text = [
        "流式文本语音合成SDK，",
        "可以将输入的文本",
        "合成为语音二进制数据，",
        "相比于非流式语音合成，",
        "流式合成的优势在于实时性",
        "更强。用户在输入文本的同时",
        "可以听到接近同步的语音输出，",
        "极大地提升了交互体验，",
        "减少了用户等待时间。",
        "适用于调用大规模",
        "语言模型（LLM），以",
        "流式输入文本的方式",
        "进行语音合成的场景。",
    ]
    
    # for text in test_text:
    #     engine.text_to_speech(text)
    #     time.sleep(0.1)
    
    # engine.complete()
    print("开始合成")
    engine.text_to_speech(test_text[0])
    print("1")
    engine.text_to_speech(test_text[1])
    print("2")
    engine.text_to_speech(test_text[2])
    print("3")
    engine.text_to_speech(test_text[3])
    print("4")
    engine.text_to_speech(test_text[4])
    print("5")
    engine.text_to_speech(test_text[5])
    print("6")
    engine.text_to_speech(test_text[6])
    print("7")
    engine.text_to_speech(test_text[7])
    print("8")
    time.sleep(2)
    engine.stop()


    engine.engine_init()
    engine.text_to_speech(test_text[7])
    engine.text_to_speech(test_text[8])
    engine.complete()
    # engine.synthesizer.streaming_complete()
    # engine._initialize_synthesizer()


    # engine.text_to_speech(test_text[8])
    # engine.text_to_speech(test_text[9])
    # engine.synthesizer.streaming_complete()

