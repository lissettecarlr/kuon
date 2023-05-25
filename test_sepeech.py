from sepeech.sepeech import SepeechThread
import time

if __name__ == "__main__":
    kuon_sepeech = SepeechThread()
    kuon_sepeech.start()

    try:
        while True:
            #kuon_sepeech.input_audio(r'J:\code\kuon\text_to_sepeech\temp\0.wav')
            kuon_sepeech.input_audio(r'J:\code\kuon\text_to_sepeech\temp\1.wav')
            kuon_sepeech.input_audio(r'J:\code\kuon\text_to_sepeech\temp\1.wav')
            #kuon_sepeech.input_audio(r'J:\code\kuon\text_to_sepeech\temp\2.wav')
            time.sleep(30)
    except:
        kuon_sepeech.exit()       
             