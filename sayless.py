from flask import Flask, request, abort
import os
import tempfile
import openai
from pydub import AudioSegment
import logging
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, AudioMessage, TextSendMessage
)
import os

load_dotenv()

app = Flask(__name__)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your Channel Access Token and Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dictionary to store user messages (for handling multiple audio messages)
user_audio_messages = {}

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    logger.info(f"Received request body: {body}")


    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(403)
    except Exception as e:
        logger.exception("Error handling the webhook:")
        abort(500)

    return 'OK', 200

def transcribe_and_summarize(audio_file_path):
    try:
        logger.info(f"Transcribing audio file: {audio_file_path}")
        with open(audio_file_path, 'rb') as audio_file:
            transcription = openai.audio.translations.create(model='whisper-1', file=audio_file)
        transcribed_text = (transcription.text)
        logger.info(f"Transcription result: {transcribed_text}")

        logger.info("Summarizing transcribed text")
        summary_prompt = f"Summarize the following text:\n\n{transcribed_text}"
        response = openai.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role":"system", "content": "You are a helpful assistant."},
                {
                    "role":"user",
                    "content": summary_prompt
                }
            ],)
        summary_text = response.choices[0].message.content
        logger.info(f"Summary result: {summary_text}")

        return transcribed_text, summary_text
    except Exception as e:
        logger.exception("Error during transcription and summarization:")
        return "Error processing the audio.", "Error summarizing the text."

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    user_id = event.source.user_id
    message_id = event.message.id
    logger.info(f"Handling audio message from user: {user_id}, message_id: {message_id}")

    try:
        user_dir = os.path.join(tempfile.gettempdir(), user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            logger.info(f"Created directory for user: {user_dir}")


        message_content = line_bot_api.get_message_content(message_id)
        audio_file_path = os.path.join(user_dir, f'{message_id}.m4a')
        with open(audio_file_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        logger.info(f"Downloaded audio message to: {audio_file_path}")


        wav_file_path = os.path.join(user_dir, f'{message_id}.wav')
        AudioSegment.from_file(audio_file_path).export(wav_file_path, format='wav')
        logger.info(f"Converted audio to WAV format: {wav_file_path}")


        if user_id not in user_audio_messages:
            user_audio_messages[user_id] = []
        user_audio_messages[user_id].append(wav_file_path)
        logger.info(f"Added WAV file to user_audio_messages: {user_audio_messages[user_id]}")


        combined_audio = AudioSegment.empty()
        for wav_file in user_audio_messages[user_id]:
            audio = AudioSegment.from_wav(wav_file)
            combined_audio += audio
        combined_wav_path = os.path.join(user_dir, 'combined.wav')
        combined_audio.export(combined_wav_path, format='wav')
        logger.info(f"Combined audio files into: {combined_wav_path}")


        transcribed_text, summary_text = transcribe_and_summarize(combined_wav_path)


        response_message = f"**Transcription:**\n{transcribed_text}\n\n**Summary:**\n{summary_text}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_message)
        )
        logger.info("Sent transcription and summary to user")

    except Exception as e:
        logger.exception("Error processing the audio message:")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Sorry, I encountered an error processing your message.")
        )

    finally:

        try:
            for file_path in user_audio_messages.get(user_id, []):
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted temporary file: {file_path}")
            if os.path.exists(combined_wav_path):
                os.remove(combined_wav_path)
                logger.info(f"Deleted combined audio file: {combined_wav_path}")
            user_audio_messages[user_id] = []
        except Exception as cleanup_error:
            logger.exception("Error during cleanup:")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)