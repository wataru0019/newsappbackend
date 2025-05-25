from fastapi import FastAPI, Body, UploadFile, File
from fastapi.responses import StreamingResponse # StreamingResponse をインポート
from fastapi.middleware.cors import CORSMiddleware
from src.agent_master import agent_master
from src.test.sqlpractice import read_article
from src.test.fetchnews import get_article_description
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
    # get_env() がジェネレータを返すと仮定
    # ジェネレータの各要素を処理する内部関数を定義
    # result = get_env("356423 + 543382478327は？")
    # response_text = result['messages'][1].content
    # return { "message": response_text }
    return { "message": "Hello World" }
    # async def stream_generator():
    #     for chunk in get_env(): # get_env() からチャンクを取得
    #         yield chunk # 各チャンクを yield
    
    # return StreamingResponse(stream_generator(), media_type="text/plain") # StreamingResponse を返す


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

@app.get("/news/{id}")
async def news(id):
    article = get_article_description(id)
    print(article)
    return { "article": article }

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
