pip install -r requirements.txt
pkill -f uvicorn; uvicorn api_server:app --reload
exit()
import nltk
nltk.download('universal_tagset')
uvicorn api_server:app --reload
