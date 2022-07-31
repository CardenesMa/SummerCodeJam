from typing import List
import uuid
import Communications
import fastapi
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
manager = Communications.ServerManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id):
    print(f"got websocket connection: {client_id}")
    await manager.connect(websocket, client_id)
    
    try:
        server_working = True
        while server_working:
            # continuously listen to everything thats going on
            await manager.listen()
            
    except WebSocketDisconnect:
        manager.disconnect()
        print(client_id, " left the chat")
        
    else:
        print("An Error Occured :(")

app.mount("/static", StaticFiles(directory="../User/Frontend"), name="static")

@app.get("/")
async def get():
    # return "Hello World"
    return FileResponse('../User/Frontend/main.html')

import uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)