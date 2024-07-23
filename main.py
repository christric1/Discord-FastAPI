from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from extract import *
import os


SECRET = os.getenv("SECRET")

app = FastAPI()

class Msg(BaseModel):
    msg: str
    secret: str

@app.get("/")
async def root():
    return {"message": "Hello World. Welcome to FastAPI!"}

@app.get("/hulan")
async def hulan_get(topic: str="馬哥", len: str="100"):
    driver=createDriver()

    data = getHulan(driver, topic, len)
    driver.close()
    return data

@app.get("/drawLots")
async def drawLots_get():
    data = drawLots()
    return data

@app.get("/getHentai")
async def hentai_get(name: str="紅村"):
    driver=createDriver()

    data = getHentai(driver, name)
    driver.close()
    return data

@app.get("/getImageHentai")
async def hentaiImage_get(url: str):
    driver=createDriver()

    data = getImageHentai(driver, url)
    driver.close()
    return data

@app.post("/backgroundDemo")
async def demo_post(inp: Msg, background_tasks: BackgroundTasks):
    
    background_tasks.add_task(doBackgroundTask, inp)
    return {"message": "Success, background task started"}