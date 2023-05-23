# coding=utf-8
import time

import torch
from torch import no_grad, LongTensor
from scipy.io.wavfile import write
from loguru import logger


from . import commons
from .models import SynthesizerTrn
from .text import text_to_sequence
from . import utils

# import logging
# logging.getLogger('numba').setLevel(logging.WARNING)


def get_text(text, hps):
    text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm, clean_text

class TextToAudio():
    def __init__(self,model,model_config):
        logger.info("init vist : model_path:{} , model_config:{}".format(model,model_config))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        device = torch.device('cpu')
       
        self.hps_ms = utils.get_hparams_from_file(model_config)
        self.net_g_ms = SynthesizerTrn(
            len(self.hps_ms.symbols),
            self.hps_ms.data.filter_length // 2 + 1,
            self.hps_ms.train.segment_size // self.hps_ms.data.hop_length,
            n_speakers=self.hps_ms.data.n_speakers,
            **self.hps_ms.model)
        _ = self.net_g_ms.eval().to(self.device)

        speakers = self.hps_ms.speakers

        model, optimizer, learning_rate, epochs = utils.load_checkpoint(model, self.net_g_ms, None)
           

    # text 转化文本
    # language 语言
    # speaker_id 说话人
    # noise_scale 控制感情变化程度
    # noise_scale_w 控制音素发音长度    
    # length_scale 控制整体语速
    def infer(self,text,speaker_id=205, noise_scale=0.6, noise_scale_w=0.668,length_scale=1.2 ):
        start = time.perf_counter()
        if not len(text):
            raise ValueError("输入不能为空！")
        
        text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
        if len(text) > 100:
            raise ValueError("输入文字过长！")
        
        text = f"[ZH]{text}[ZH]"
        stn_tst, clean_text = get_text(text, self.hps_ms)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(self.device)

            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(self.device)

            speaker_id = LongTensor([speaker_id]).to(self.device)
            
            audio = self.net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                                 length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
        #logger.debug("文本转语音完成，耗时：{} s".format(round(time.perf_counter()-start, 2)))   
        return audio

    def save(self,audio,save_path):
        write(save_path, self.hps_ms.data.sampling_rate, audio)
        #logger.debug("保存语音文件到：{}".format(save_path))
        return save_path

if __name__ == "__main__":
    text = "你好，这是一段测试文字转语音的文本。"
    text_to_audio = TextToAudio()
    audio = text_to_audio.convert(text)
    text_to_audio.save(audio,"./out/test.wav")


# def vits(text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
#     start = time.perf_counter()
#     if not len(text):
#         return "输入文本不能为空！", None, None
#     text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
#     if len(text) > 100:
#         return f"输入文字过长！{len(text)}>100", None, None
#     if language == 0:
#         text = f"[ZH]{text}[ZH]"
#     elif language == 1:
#         text = f"[JA]{text}[JA]"
#     else:
#         text = f"{text}"
#     stn_tst, clean_text = get_text(text, hps_ms)

#     with no_grad():
#         x_tst = stn_tst.unsqueeze(0).to(device)
#         x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
#         speaker_id = LongTensor([speaker_id]).to(device)
#         audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
#                                length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
        
#     return audio
#     write("./out/test.wav", hps_ms.data.sampling_rate, audio)
#     print(f"生成耗时 {round(time.perf_counter()-start, 2)} s")
#     return "生成成功!", (22050, audio), f"生成耗时 {round(time.perf_counter()-start, 2)} s"

# def text_to_audio(text,audio="./out/test.wav"):

#     lang = 0
#     #声音选择
#     # for index, value in enumerate(speakers):
#     #     print(f"Index: {index}, Value: {value}")
#     # exit(0)
#     # 205
#     speaker = 205
#     #控制感情变化程度
#     ns=0.6   
#     #控制音素发音长度
#     nsw=0.668      
#     #控制整体语速
#     ls= 1.2  
#     vits(text, lang, speaker, ns, nsw, ls)
       