Here's a clean README file based on the commands and issues we've addressed, providing comprehensive instructions for setting up and running your Speech Analyzer project.

Speech Analyzer Project
This project consists of a Python backend (FastAPI) for speech analysis and a Next.js frontend for interaction.

🚀 Getting Started
Follow these steps to set up and run the project.

1. Backend Setup (Python)

The backend requires Python and its dependencies. It's highly recommended to use a virtual environment to manage dependencies.

Navigate to the backend directory:

cd /Users/shakhzod/SpeechAnalyzer-2

Create a virtual environment (if you don't have one):

It's recommended to use a stable Python version like 3.11 or 3.12, as Python 3.13 might have compatibility issues with some libraries (e.g., moviepy).

# If you don't have Python 3.11 installed via Homebrew:
# brew install python@3.11

# Create the virtual environment using Python 3.11 (adjust path if needed)
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv

Activate the virtual environment:

source .venv/bin/activate

Your terminal prompt should now show (.venv) at the beginning, indicating the virtual environment is active.

Install Python dependencies:

First, upgrade pip to the latest version within your virtual environment:

pip install --upgrade pip

Then, install all required packages from requirements.txt, along with FastAPI and Uvicorn:

pip install -r requirements.txt
pip install "fastapi[all]" uvicorn moviepy

Download NLTK data (Crucial for NLP functionalities):

Your project uses NLTK for part-of-speech tagging and tokenization. These resources need to be downloaded. Ensure your virtual environment is active before running these commands:

python -c "import nltk; nltk.download('universal_tagset')"
python -c "import nltk; nltk.download('punkt_tab')"
python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

2. Frontend Setup (Next.js)

The frontend is a Next.js application that uses Tailwind CSS.

Navigate to the frontend directory:

cd /Users/shakhzod/SpeechAnalyzer-2/frontend

Install JavaScript dependencies:

npm install
# or if you use yarn:
# yarn install

Update PostCSS Configuration:

Ensure your postcss.config.js file is correctly configured for ES module syntax and the latest Tailwind CSS PostCSS plugin. Open /Users/shakhzod/SpeechAnalyzer-2/frontend/postcss.config.js and ensure its content is exactly as follows:

// postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    'autoprefixer': {},
  },
};

3. Running the Backend

Make sure you are in the backend directory (/Users/shakhzod/SpeechAnalyzer-2) and your virtual environment is active.

cd /Users/shakhzod/SpeechAnalyzer-2
source .venv/bin/activate

uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

The server will typically run on http://0.0.0.0:8000 or http://127.0.0.1:8000.

4. Running the Frontend

Make sure you are in the frontend directory (/Users/shakhzod/SpeechAnalyzer-2/frontend).

cd /Users/shakhzod/SpeechAnalyzer-2/frontend

npm run dev
# or if you use yarn:
# yarn dev

The frontend application will usually start on http://localhost:3000 (or another available port if 3000 is in use).

🐛 Troubleshooting
zsh: command not found: uvicorn or source: no such file or directory: .venv/bin/activate:

Ensure you are in the correct project directory (/Users/shakhzod/SpeechAnalyzer-2).

Ensure the virtual environment (.venv folder) exists. If not, create it using python3 -m venv .venv.

Always activate the virtual environment using source .venv/bin/activate before running Python commands like uvicorn or pip.

ModuleNotFoundError: No module named '...':

Activate your virtual environment.

Install the missing package using pip install <package-name>. For NLTK data, use python -c "import nltk; nltk.download('<resource-name>')"

If the error persists for moviepy.editor or similar, consider recreating your virtual environment with a slightly older, more stable Python version (e.g., 3.11 instead of 3.13).

ReferenceError: module is not defined in ES module scope / Error: Cannot find module 'function Ot(...)' (Frontend):

Ensure your postcss.config.js file (located in /Users/shakhzod/SpeechAnalyzer-2/frontend/) is using the correct ES module syntax and plugin names as specified in "Update PostCSS Configuration" above.

Ensure you have installed @tailwindcss/postcss and autoprefixer using npm install @tailwindcss/postcss autoprefixer.

