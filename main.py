from typing import List
import uuid
import Server.Communications as Communications
import fastapi
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
manager = Communications.ServerManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    servercomms = Communications.ServerComms(websocket)
    print(f"got websocket connection")
    await manager.connect(servercomms)

    try:
        server_working = True
        while server_working:
            # continuously listen to everything thats going on
            data = await websocket.receive_text()
            # give the manager that data
            await manager.listen(data, servercomms)
    except WebSocketDisconnect:
        print("client left the chat")

    finally:
        await servercomms.disconnect()


    # else:
    #     print("An Error Occured :(")

app.mount("/static", StaticFiles(directory="User/Frontend/static"), name="static")

@app.get("/")
async def get():
    # return "Hello World"
    return FileResponse('User/Frontend/main.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, reload=True)
