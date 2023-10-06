import speech_recognition as sr
import asyncio
import websockets
import json
import openai
import base64
import shutil
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Define API keys and voice ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize the SpeechRecognition recognizer
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        print("Please start speaking...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing your speech...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            print("No speech detected within 5 seconds.")
            return None
        except sr.UnknownValueError:
            print("Could not understand your speech.")
            return None

def is_installed(lib_name):
    return shutil.which(lib_name) is not None



async def text_chunker(chunks):
    """Split text into chunks, ensuring not to break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "



# Modify the stream function to adjust volume
async def stream(audio_stream, volume=100):
    """Stream audio data using mpv player."""
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    # Use the --volume flag to set the volume level (0-100)
    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0", f"--volume={volume}"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    print(f"Started streaming audio at volume {volume}%")
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()



async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_monolingual_v1"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": True},
            "xi_api_key": ELEVENLABS_API_KEY,
        }))

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get('isFinal'):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))

        async for text in text_chunker(text_iterator):
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

        await websocket.send(json.dumps({"text": ""}))

        await listen_task

async def chat_completion():
    while True:
        spoken_text = recognize_speech()
        if spoken_text:
            user_query = spoken_text
            if user_query.lower() == "goodbye":
                print("Ava: Goodbye!")
                break
            response = await openai.ChatCompletion.acreate(
                model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': user_query}],
                temperature=1, stream=True
            )
            async def text_iterator():
                async for chunk in response:
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get("delta", {})
                        if 'content' in delta:
                            yield delta["content"]
                        else:
                            break
                    else:
                        break
            await text_to_speech_input_streaming(VOICE_ID, text_iterator())
        else:
            print("Ava: No speech detected or recognized.")

# Main execution
if __name__ == "__main__":
    print("Ava: Hello! How can I assist you today?")
    asyncio.run(chat_completion())
