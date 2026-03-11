# Interview Simulator
Allows the user to have a mock interview with an ai model that will provide questions for the related job, feedback on the answers, a transcript so the user can review exactly what they said, monitor body language and other features

## Installation & Setup
Follow these exact steps to configure the environment and install the necessary drivers for the Interview Simulator.

1. Environment Initialization
It is recommended to use a virtual environment to ensure dependency isolation.

## Create the environment

```bash
python -m venv venv
```

## Activate the environment (Windows)

```powershell
venv\Scripts\activate
```

## Activate the environment (Mac/Linux)

```bash
source venv/bin/activate
```

2. Dependency Installation
Once the environment is active, install the core libraries required for audio processing and networking:

```bash
pip install -r requirements.txt
```

3. Special Hardware Configuration (PyAudio)
If the standard installation fails for pyaudio (common on Windows systems), execute the following commands to install the pre-compiled binary:

```bash
pip install pipwin
pipwin install pyaudio
```

4. API Configuration
The system requires a Deepgram API key for the Speech-to-Text engine.

    - Create a file named config.py in the root directory.

    - Add your API key in the following Python format:

```python
API_KEY = "YOUR_DEEPGRAM_API_KEY_HERE"
```

5. Running the Module
To verify the setup and test the microphone pipeline:

```bash
python your_filename.py
```