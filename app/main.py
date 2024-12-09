# Copyright (C) 2024 Aleksei Rogov <alekzzzr@gmail.com>. All rights reserved.

import uvicorn
from fastapi import FastAPI, Depends
from app import thermo
from app.schemas import ResponseSchema


app = FastAPI()


app.include_router(thermo.router, tags=['Thermo'], prefix='/api/thermo')


@app.get("/api/thermo/health")
def health_check() -> ResponseSchema:
    return ResponseSchema(status=True, reason="healthchecker route")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0")
