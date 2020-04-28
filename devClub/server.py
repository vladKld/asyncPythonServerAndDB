import asyncio
import json
import websockets
import dataBaseController

class WebSocketServer:

    def __init__(self):
        start_server = websockets.serve(self.handler, 'localhost', 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def handler(self, websocket, path):

        process = ProcessingSocket(websocket)
        while(True):
            consumer_task = asyncio.ensure_future(
                process.get_message())
            producer_task = asyncio.ensure_future(
                process.produce())
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            if consumer_task in done:
                await process.consume()
            else:
                consumer_task.cancel()

            if producer_task in done:
                message = producer_task.result()
                await process.send_message(message)
            else:
                producer_task.cancel()

class User:
    def __init__(self, login, password, name = None, phone_number = None):
        self.login = login
        self.password = password
        self.name = name
        self.phone_number = phone_number
    def addUserToDataBase(self):
        db = dataBaseController.DataBase('ARConf', 'postgres', 'postgres')
        db.createTable('Users', 'ID SERIAL, USERNAME TEXT NOT NULL, PASSWORD TEXT NOT NULL, NAME TEXT, PHONE TEXT')
        
        if len(db.findByField('Users', "'" + self.login + "'")) != 0:
            return 'This user already exists'
        else:
            db.insertRow('Users (USERNAME, PASSWORD, NAME, PHONE)', "'" + self.login + "'" + ', ' + 
            "'" + self.password + "'" + ', ' + "'" + self.name + "'" + ', ' + "'" + self.phone_number + "'")
            return 'Sign up success'

    def checkUserInDataBase(self):
        db = dataBaseController.DataBase('ARConf', 'postgres', 'postgres')
        db.createTable('Users', 'ID SERIAL, USERNAME TEXT NOT NULL, PASSWORD TEXT NOT NULL, NAME TEXT, PHONE TEXT')
        user = db.findByField('Users', "'" + self.login + "'")
        print(user)
        if len(user) != 0:
            #return json.dumps(user, indent=4)
            return "Sign in success"
        else:
            return 'This user is not exists'

class ProcessingSocket:

    def __init__(self, websocket):
        self.ws = websocket
        self.incoming = asyncio.Queue()
        self.outgoing = asyncio.Queue()

    async def get_message(self):
        message = await self.ws.recv()
        await self.incoming.put(message)

    async def send_message(self, message):
        await self.ws.send(message)

    async def consume(self):
        consume_message = await self.incoming.get()
        print(consume_message)
        pyMessage = json.loads(consume_message)
        #Work with DATABASE

        if pyMessage['type'] == 'log in':
            await self.outgoing.put(User(pyMessage['email'], pyMessage['pass']).checkUserInDataBase())
        elif pyMessage['type'] == 'sign up':
            await self.outgoing.put(User(pyMessage['email'], pyMessage['pass'], 
                                    pyMessage['name'], pyMessage['phone']).addUserToDataBase())
        #----------------------

    async def produce(self):
        message_out = await self.outgoing.get()
        return message_out

if __name__ == "__main__":
    WebSocketServer()