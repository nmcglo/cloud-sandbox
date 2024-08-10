from fastapi import FastAPI
from pydantic import BaseModel
import random
import time
from lorem_text import lorem

app = FastAPI()

class ComputeResponse(BaseModel):
    response: str

@app.post("/compute", response_model=ComputeResponse)
async def compute():
    time.sleep(1)
    
    word_count = 200
    random_text = lorem.words(word_count)
    
    return ComputeResponse(response=random_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
