import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from obsync.routes import vault_router, user_router, subscript_router, ws_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(vault_router)
app.include_router(user_router)
app.include_router(subscript_router)
app.include_router(ws_router)


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=6666, reload=True)


if __name__ == "__main__":
    main()
