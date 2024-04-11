from aiohttp import ClientSession
import asyncio
import argparse
from logger import Loger, logger


def print_response(response):
    print(f"id: {response['id']}")
    print(f"status: {response['status']}")
    print(f"result_code: {response['result_code']}")
    print(f"url: {response['url']}")


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["send", "request", "list"], help="Command's to execute")
    parser.add_argument("value", type=str, nargs="*")
    return parser.parse_args()


async def check_statys(uid):
    while True:
        async with ClientSession() as session:
            async with session.get(url=f"http://127.0.0.1:8888/api/v1/tasks/{uid}") as response:
                response = await response.json()
                print(response)
                if response["status"] == "ready":
                    break
                else:
                    await asyncio.sleep(1)


async def create_check_task(ids: list[str]):
    tasks = []
    for uid in ids:
        tasks.append(asyncio.create_task(check_statys(uid)))
    for task in tasks:
        await task


async def send_urls(url_list: list[str]):
    async with ClientSession() as session:
        async with session.post(url="http://127.0.0.1:8888/api/v1/tasks", json={"url_list": url_list}) as response:
            response = await response.json()
            await create_check_task([res['id'] for res in response])
            for res in response:
                print_response(res)


async def get_url_status(uid: str):
    async with ClientSession() as session:
        async with session.get(url=f"http://127.0.0.1:8888/api/v1/tasks/{uid}") as response:
            response = await response.json()
            print_response(response)


async def get_list():
    async with ClientSession() as session:
        async with session.get(url=f"http://127.0.0.1:8888/api/v1/list") as response:
            response = await response.json()
            for res in response:
                print_response(res)


def core():
    args = init_parser()
    if args.command == "send":
        asyncio.run(send_urls(args.value))
    elif args.command == "request":
        if len(args.value) == 1:
            asyncio.run(get_url_status(*args.value))
    elif args.command == "list":
        asyncio.run(get_list())


if __name__ == "__main__":
    core()
