
import os
import openai
openai.api_key = "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"

def whisper_openai(file_path):
    with open(file_path, 'rb') as audio_file:
        response = openai.Audio.transcribe('whisper-1', audio_file,language="zh")
    os.remove(file_path)
    result = response.get('text')
    return result