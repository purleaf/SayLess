# 🤖 LINE Bot with OpenAI Transcription & Summarization

![LINE Bot](https://img.shields.io/badge/LINE-Bot-green) ![OpenAI](https://img.shields.io/badge/OpenAI-API-blue) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

Welcome to the **LINE Bot with OpenAI Transcription & Summarization** project! This bot allows users to send audio messages, which are then transcribed and summarized using OpenAI's powerful APIs. The application is built with Python and Flask, making it easy to set up and run locally.

## ✨ Features

- **📣 Audio Message Processing**: Receive and handle audio messages from LINE users.
- **📝 Transcription**: Convert audio messages to text using OpenAI's Whisper API.
- **📚 Summarization**: Generate concise summaries of transcribed text using OpenAI's GPT models.
- **🔒 Secure Environment**: Manage sensitive credentials securely with environment variables.
- **📦 Easy Setup**: Simple setup process without the need for Docker.
- **🌐 ngrok Integration**: Expose your local server to the internet for webhook integration.

## 📋 Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+** installed on your machine. [Download Python](https://www.python.org/downloads/)
- **pip** package manager. Comes bundled with Python.
- **ngrok** installed for exposing your local server. [Download ngrok](https://ngrok.com/download)
- A **LINE Messaging API** channel with `Channel Access Token` and `Channel Secret`.
- An **OpenAI API Key** for accessing Whisper and GPT models.

## 🚀 Getting Started

Follow these instructions to set up and run the bot locally.

### 1. 📁 Clone the Repository

```bash
git clone https://github.com/purleaf/SayLess.git
cd your-repository
```
### 2. 🐍 Set Up a Virtual Environment (Recommended)

Creating a virtual environment helps manage dependencies without affecting your global Python installation.

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```
### 3. 📦 Install Dependencies
Install the required Python packages using pip.

```bash
pip install -r requirements.txt
```
### 4. 🛠️ Configure Environment Variables
Create a `.env` file in the root directory of your project and add the following environment variables:
```dotenv
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
LINE_CHANNEL_SECRET=your-channel-secret
OPENAI_API_KEY=your-openai-api-key
```
### 5. 🔧 Running the Application
Start the Flask application using the following command:
```bash
python app.py
```
You should see output indicating that the Flask server is running:
```csharp
 * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
```
### 6. 🌐 Expose Your Local Server with ngrok
To allow LINE to send webhook events to your local server, use ngrok to create a public URL.
```bash
ngrok http 5001
```
**Sample Output:**
```bash
Forwarding                    https://abcd1234.ngrok.io -> http://localhost:5001
```
### 7. 🔗 Configure LINE Webhook URL

1. **Copy the ngrok URL** (e.g., https://abcd1234.ngrok.io).
2. **Navigate to the LINE Developers Console**: LINE Developers Console
3. **Select Your Channel**.
4. **Set the Webhook URL** to `<ngrok-url>/callback` (e.g., `https://abcd1234.ngrok.io/callback`).
5. Enable Webhooks and Verify the URL.

