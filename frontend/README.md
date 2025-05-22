pip install -r requirements.txt
pkill -f uvicorn; uvicorn api_server:app --reload
