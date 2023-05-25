from loguru import logger
import time

def test_paraformer():
    from sepeech_to_text.Paraformer import paraformer
    service = paraformer()
    wav_path = r'sepeech_to_text\0478_00017.wav'
    start_time = time.time()
    result = service.infer(wav_path)
    end_time = time.time()
    logger.debug("文件 {} 转换完成 api耗时:{}，结果：{}".format(wav_path,round(end_time-start_time,2),result))

def test_whisper_online():
    from sepeech_to_text.whisper_online.whisper_app import Whispers
    from cfg.config import read_yaml
    config = read_yaml(r'cfg/kuon.yaml')
    # print(config)
    # print(config['OPENAI']['key'])  
    service = Whispers(config['OPENAI']['key'])
    wav_path = r'sepeech_to_text\0478_00017.wav'
    start_time = time.time()
    result = service.infer(wav_path)
    end_time = time.time()
    logger.debug("文件 {} 转换完成 api耗时:{}，结果：{}".format(wav_path,round(end_time-start_time,2),result))
  
def test_asr():
    from sepeech_to_text.asr import ASR
    from cfg.config import read_yaml
    config = read_yaml(r'cfg/kuon.yaml')
    asr = ASR(config)
    wav_path = r'sepeech_to_text\0478_00017.wav'
    asr.convert(wav_path,'parafomer')
    #asr.convert(wav_path,'whisper_online')

if __name__ == '__main__':
    #test_paraformer()
    #test_whisper_online()
    test_asr()