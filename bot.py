import asyncio
import os
import copy

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram import Bot, Dispatcher, executor, types
from icmplib import async_multiping, async_ping

API_TOKEN = '6085300481:AAGc58QwYQ0ejvlQzThd6kI35_p_XICQYgs'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)




class Server:
    
    
    def __init__(self, host, owner_id, status) -> None:
        self.host = host
        self.owner_id = owner_id
        self.status = status


    
class Watcher:
    
    def __init__(self) -> None:
        self.servers = []
        
    
    def add_server(self, server: Server):
        self.servers.append(server)
    
    
    def is_watching(self, host):
        for server in self.servers:
            if host == server.host:
                return True
        return False
    
    
    async def check_online(self, server: Server) -> bool:
        response = await async_ping(server.host, timeout=5, count=4)
        return response.is_alive
    
    
    async def send_alert(self, server: Server):
        await bot.send_message(
            chat_id=server.owner_id,
            text=f"Сервер {server.host} теперь {'онлайн' if server.status else 'оффлайн'}"
        )        
        
        
    async def watch(self):
        while True:
            try:
                if len(self.servers) == 0:
                    await asyncio.sleep(1)
                    continue
                results = await async_multiping([server.host for server in self.servers], timeout=5, count=4)
                for i, server in enumerate(self.servers):
                    print(results[i])
                    if results[i].is_alive == server.status:
                        continue
                    self.servers[i].status = results[i].is_alive
                    try:
                        await self.send_alert(self.servers[i])
                    except Exception as e:
                        print(e)
            except Exception as e:
                        print(e)
                
            
            
watcher = Watcher()              
       
       
@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer("Добро пожаловать в бота. \nВведите /add {адресс} для добавления роутера")


@dp.message_handler(commands=['add'])
async def add_ip(message: Message):
    args = message.get_args()
    if not args:
        await message.answer("Не верно введена команда")
        return
    server_host = args
    
    if watcher.is_watching(server_host):
        await message.answer("Сервер уже отслеживается")
        return
    await message.answer("Проверяем сайт на доступность...")
    
    server = Server(server_host, message.from_id, True)
    try:
        is_online = await watcher.check_online(server)
    except:
        await message.answer("Не верно введен сервер")
        return
    if is_online:
        watcher.add_server(server)
        await message.answer("Сервер добавлен в мониторинг")
        await message.answer(f"Сервер {server.host} теперь {'онлайн' if server.status else 'оффлайн'}")
    else:
        await message.answer("Сервер офлайн")
        
    
    

async def startup(dp):
    print("Бот запустился")
    asyncio.create_task(watcher.watch())
    
    
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=startup)