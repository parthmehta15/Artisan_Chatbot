

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



class UserQuery(BaseModel):
    userQuery: str

@app.post("/api/get_ai_message")
async def get_ai_message(query: UserQuery) -> Dict[str, str]:
    
        print(query)
        return {
            "role": "assistant",
            "content": "Hi form backend"
        }
   

if __name__ == '__main__':
  
    uvicorn.run("test:app")

