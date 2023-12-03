import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from obsync.routes import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["app://obsidian.md", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(vault_router)
app.include_router(user_router)
app.include_router(subscript_router)
app.include_router(ws_router)
app.include_router(api_router)
app.include_router(publish_router)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=6666, reload=True)


if __name__ == "__main__":
    main()
