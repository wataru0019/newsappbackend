from fastapi import FastAPI, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.agent_master import agent_master
from src.tools_list.sqlpractice import read_article
from typing import Any
import os

try :
    from dotenv import load_dotenv
    load_dotenv()
except :
    pass

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(): # 非同期関数として定義
    return { "message": "Hello World" }

@app.post("/")
async def post_root(payload: Any = Body(...)): # 非同期関数として定義
    print(payload)
    result = agent_master(payload["text"])
    return { "message": result }

@app.get("/news")
async def news():
    articles = read_article()
    print(articles)
    return { "articles": articles }

# @app.get("/news/{id}")
# async def news(id):
#     article = get_article_description(id)
#     print(article)
#     return { "article": article }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create uploads directory if it doesn't exist
        print(file)
        os.makedirs("uploads", exist_ok=True)
        
        # Save the file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_path": file_path
        }
    except Exception as e:
        return {"error": str(e)}
