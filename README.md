# TO RUN
# SETUP
conda create -n chatbot python=3.8.19
conda activate chatbot
pip install -r requirements.txt

OPEN 2 TERMINALS AND RUN:

cd backend
## `python fastapi_code.py`
Runs backend 
Runs on http://127.0.0.1:5000 

cd frontend
## `npm start` 
Runs frontend 
Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.


### `.env`
In the .env file add OpenAI Api key 
OPENAI_API_KEY=