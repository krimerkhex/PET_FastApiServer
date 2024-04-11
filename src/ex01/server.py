from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from aiohttp import ClientSession
import asyncio
import uvicorn
from logger import Loger, logger
from uuid import uuid4, UUID

"""Command to start server: uvicorn server:core --reload"""

""" Test link's
"url_list": [
    "http://pinterest.com",
    "http://guardian.co.uk",
    "http://facebook.com",
    "http://pinterest.com",
    "https://instagram.com",
    "https://wikipedia.org",
    "https://netflix.com",
    "https://walmart.com",
    "https://naver.com",
    "http://ebay.com"
]
"""

core = FastAPI(title="Crowle")
tasks = {}


class Object(BaseModel):
    id: str
    status: str
    result_code: int
    url: str


class Urls(BaseModel):
    url_list: list[str]


@Loger
async def crowlering(uid: str):
    async with ClientSession() as session:
        try:
            async with session.get(tasks[uid].result_url) as response:
                logger.info(f"\nUUID: {uid}\nURL: {tasks[uid].url}\nStatus code: {response.status}")
                tasks[uid].result_code = response.status
        except Exception as e:
            logger.warning(f"\nUUID: {uid}\nURL: {tasks[uid].url}\nStatus code: {404}")
            tasks[uid].result_code = 404
        tasks[uid].status = "ready"


@Loger
async def create_async_task(task_id: list[str]):
    asnc_task = []
    for uid in task_id:
        asnc_task.append(asyncio.create_task(crowlering(uid)))
    for task in asnc_task:
        await task


@core.post("/api/v1/tasks/")
@Loger
def get_json(data: Urls):
    task_id: list[str] = [str(uuid4()) for _ in range(len(data.url_list))]
    for index, uid in enumerate(task_id):
        tasks[uid] = Object(id=uid, status="running", result_code=0, url=data.url_list[index])
    asyncio.run(create_async_task(task_id))
    r_value: list[Object] = [tasks[uid] for uid in task_id]
    return JSONResponse(content=jsonable_encoder(r_value), status_code=201)


@core.get("/api/v1/tasks/{received_task_id}")
@Loger
def send_urls(received_task_id: str | int | UUID):
    if type(received_task_id) is int or type(received_task_id) is UUID:
        received_task_id = str(received_task_id)
    return JSONResponse(content=jsonable_encoder(tasks[received_task_id]), status_code=200)


@core.get("/api/v1/list")
@Loger
def send_urls():
    r_value: list[Object] = [tasks[uid] for uid in tasks.keys()]
    return JSONResponse(content=jsonable_encoder(r_value), status_code=200)


if __name__ == "__main__":
    logger.info("Server started")
    uvicorn.run(core, host="127.0.0.1", port=8888, log_level="info")
