import asyncio
import json
import os
import wave
import websockets

class FunASRClient:
    def __init__(self, url="ws://127.0.0.1:20002"):
        self.url = url

    async def connect_server(self, wav_path):
        async with websockets.connect(self.url, subprotocols=["binary"], ping_interval=None) as websocket:
            with wave.open(wav_path, "rb") as wav_file:
                params = wav_file.getparams()
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                audio_bytes = bytes(frames)

            message = json.dumps({
                "mode": "offline",
                "chunk_size": [5, 10, 5],
                "chunk_interval": 10,
                "audio_fs": sample_rate,
                "wav_name": os.path.basename(wav_path),
                "is_speaking": True,
                "hotwords": "",
                "itn": True
            })
            await websocket.send(message)

            chunk_interval = 10
            chunk_size = 10
            stride = int(60 * chunk_size / chunk_interval / 1000 * sample_rate * 2)
            chunk_num = (len(audio_bytes) - 1) // stride + 1

            for i in range(chunk_num):
                beg = i * stride
                data = audio_bytes[beg:beg + stride]
                await websocket.send(data)

                if i == chunk_num - 1:
                    is_speaking = False
                    message = json.dumps({"is_speaking": is_speaking})
                    await websocket.send(message)

                await asyncio.sleep(0.001)

            response = await websocket.recv()
            return response

    async def filter(self, audio_path):
        try:
            response = await self.connect_server(audio_path)
            data = json.loads(response)
            if os.path.basename(audio_path) == data["wav_name"]:
                return data["text"]
            else:
                raise ValueError("The response is not matched with the request.")
        except websockets.exceptions.ConnectionClosedError:
            raise ValueError("Connection closed unexpectedly.")
        except Exception as e:
            raise ValueError(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    transcriber = FunASRClient()
    result = asyncio.run(transcriber.filter("../audio/asr_example.wav"))
    print(f"Transcription Result: {result}")
