# Ava-Virtual-Assistant

Ava is a Python-based personal voice assistant that uses OpenAI's GPT-3.5 for natural language understanding and Eleven Labs for text-to-speech capabilities.

## Prerequisites

Before you can run Ava, make sure you have the following prerequisites installed:

- Python 3.x (https://www.python.org/downloads/)
- Git (https://git-scm.com/downloads)
- mpv (https://mpv.io/installation/) for audio streaming

## Getting Started

Follow these steps to set up and run Ava on your local machine:

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/Shubham-Balgotra/Ava-Virtual-Assistant.git

2. Install the required Python libraries by creating a virtual environment and using pip:

   <p>GO to the directory where you clone this repository in your local machine. Click on the directory path "C:\Users\SPSA\Desktop\ava_ai", remove it and type cmd. Hit enter.</p>
   
   ```bash
   pip install -r requirements.txt
   ```

3. Modify the .env file in the project directory with your API keys:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   VOICE_ID=your_voice_id
   ```
   <p> Replace your_openai_api_key, your_elevenlabs_api_key, and your_voice_id with your actual API keys and voice ID.</p>

4. Run Ava:

   ```bash
   python Ava.py
   ```

## Usage
Ava can assist you with various tasks, answer questions, and perform actions based on your voice commands. Simply start speaking, and Ava will do its best to assist you.

## Contributing
Contributions are welcome! If you have ideas for improving Ava or want to add new features, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
