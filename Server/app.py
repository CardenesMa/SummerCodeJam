from typing import List
import uuid
import Communications
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()
    
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id):
    manager = Communications.ServerManager(websocket, client_id)
    await manager.connect()
    
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



import uvicorn
if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)