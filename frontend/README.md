Here's a README section detailing the backend setup steps you've provided, converted into a clean and easy-to-follow format.

🚀 Backend Setup (Python)
This section guides you through setting up the Python backend, including creating a virtual environment, installing dependencies, and running the server.

1. Clean Up Previous Environment (Optional, but Recommended)

If you've had issues with your virtual environment before, it's often best to start fresh.

# Deactivate the virtual environment if it's currently active
deactivate

# Remove the existing virtual environment directory
# BE CAREFUL: Ensure you are in the correct project directory before running this.
rm -rf .venv

2. Install a Stable Python Version (if needed)

It's highly recommended to use a stable Python version (e.g., 3.11 or 3.12) as newer versions like 3.13 might have compatibility issues with certain libraries (like moviepy).

# Example for Python 3.11 using Homebrew on macOS
# If you already have it, Homebrew will skip installation.
brew install python@3.11

3. Create and Activate a New Virtual Environment

Navigate to your backend project's root directory (e.g., /Users/shakhzod/SpeechAnalyzer-3 or SpeechAnalyzer-2). Then, create a new virtual environment using the desired Python version and activate it.

# Make sure you are in the correct directory, e.g., cd /Users/shakhzod/SpeechAnalyzer-3

# Create the virtual environment using Python 3.11
# Adjust the path to your Python 3.11 executable if it's different.
/opt/homebrew/opt/python@3.11/bin/python3.11 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

Your terminal prompt should now show (.venv) at the beginning, indicating the virtual environment is active.

4. Install Python Dependencies

With your virtual environment active, install all the necessary Python packages.

# First, upgrade pip to the latest version within your virtual environment
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install FastAPI, Uvicorn, and MoviePy (ensure all are explicitly covered)
pip install "fastapi[all]" uvicorn moviepy

5. Download NLTK Data

Your project's NLP functionalities rely on specific NLTK data. Ensure your virtual environment is active before running these commands:

python -c "import nltk; nltk.download('universal_tagset')"
python -c "import nltk; nltk.download('punkt_tab')"
python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

6. Run the Backend Server

Finally, start your FastAPI backend server using Uvicorn. Make sure you are in the backend project's root directory and your virtual environment is active.

uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

The server will typically run on http://0.0.0.0:8000 or http://127.0.0.1:8000. The --reload flag will automatically restart the server when changes are detected in your code.

