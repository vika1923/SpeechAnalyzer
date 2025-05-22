pip install -r requirements.txt
python3 api_server.py
pip install uvicorn
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
pkill -f source .venv/bin/activate; uvicorn api_server:app --reload
exit()
import nltk
nltk.download('universal_tagset')
uvicorn api_server:app --reload
pip install -r requirements.txt
