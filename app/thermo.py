# Copyright (C) 2024 Aleksei Rogov <alekzzzr@gmail.com>. All rights reserved.

import binascii
import hashlib
import zlib
from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from time import time
from typing import Annotated
from uuid import uuid4
from app.schemas import ThermoAddSchema, KeyAddSchema, ResponseSchema, KeySchema, DeleteSchema
from app.models import Base, ThermoModel, KeyModel
from app.database import SessionDep, engine
from app.config import settings


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def auth_check(token: str, session: SessionDep, perm: str):
    field = None
    match perm:
        case "perm_delete_key":
            field = KeyModel.perm_delete_key
        case "perm_delete_thermo":
            field = KeyModel.perm_delete_thermo
        case "perm_read_key":
            field = KeyModel.perm_read_key
        case "perm_read_thermo":
            field = KeyModel.perm_read_thermo
        case "perm_add_key":
            field = KeyModel.perm_add_key
        case "perm_add_thermo":
            field = KeyModel.perm_add_thermo

    query = select(KeyModel).where(KeyModel.key == token and field is True)
    result = await session.execute(query)
    result = result.scalars().first()
    if result is None:
        raise HTTPException(status_code=401, detail="invalid key")

    return result


@router.post("/setup_db", description="Init database")
async def setup_db(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> ResponseSchema:
    if token != settings.root_key:
        raise HTTPException(status_code=401, detail="invalid root key")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    key = KeyModel(
        name="root",
        email=settings.root_email,
        key=settings.root_key,
        created=int(time()),
        perm_add_key=True,
        perm_add_thermo=True,
        perm_delete_key=True,
        perm_delete_thermo=True,
        perm_read_key=True,
        perm_read_thermo=True,
        enabled=True,
    )
    session.add(key)
    await session.commit()

    return ResponseSchema(status=True, reason=f"database created")


@router.get("/keys", description="Get users keys")
async def get_keys(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> list[KeySchema]:
    await auth_check(token, session, "perm_read_key")

    query = select(KeyModel)
    result = await session.execute(query)

    return result.scalars().all()


@router.post("/keys", status_code=status.HTTP_201_CREATED, description="Add user key")
async def add_key(data: KeyAddSchema, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    await auth_check(token, session, "perm_add_key")

    key = KeyModel(
        name=data.name,
        email=data.email,
        key=str(uuid4()),
        created=int(time()),
        perm_add_key=data.perm_add_key,
        perm_add_thermo=data.perm_add_thermo,
        perm_delete_key=data.perm_delete_key,
        perm_delete_thermo=data.perm_delete_thermo,
        perm_read_key=data.perm_read_key,
        perm_read_thermo=data.perm_read_thermo,
        enabled=True,
    )
    session.add(key)
    await session.commit()

    return {"status": True, "reason": "key added", "name": key.name,
            "email": key.email, "key": key.key, "created": key.created}


@router.delete("/keys", description="Delete key")
async def del_key(data: DeleteSchema, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    await auth_check(token, session, "perm_delete_key")

    query = select(KeyModel).where(KeyModel.id == data.id)
    result = await session.execute(query)
    result = result.scalars().first()
    if result is None:
        raise HTTPException(status_code=403, detail="key does not exist")

    await session.delete(result)
    await session.commit()

    return {"status": True, "reason": "key deleted"}


@router.get("/thermo", description="Get thermo data")
async def get_thermo(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    await auth_check(token, session, "perm_read_thermo")

    query = select(ThermoModel)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/thermo", status_code=status.HTTP_201_CREATED, description="Post thermo data")
async def add_thermo(data: ThermoAddSchema, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    result = await auth_check(token, session, "perm_add_thermo")

    thermo = ThermoModel(
        key_id=result.id,
        sid=data.sid,
        mac=data.mac,
        temp=data.temp,
        pres=data.pres,
        hum=data.hum,
        adc=data.adc,
        timestamp=int(time()),
    )
    session.add(thermo)
    await session.commit()

    if data.update is True:
        with open(settings.fw_file, 'rb') as fw_file:
            fw_content = fw_file.read()
        fw_sha1 = binascii.hexlify(hashlib.sha1(fw_content).digest()).decode('utf-8')

        if fw_sha1 != data.sha1:
            fw_content_z = zlib.compress(fw_content, 9)
            fw_content_zb = binascii.b2a_base64(fw_content_z)
            return {"status": True, "reason": "data accepted", "sha1": fw_sha1, "content": fw_content_zb}

    return {"status": True, "reason": "data added"}


@router.delete("/thermo")
async def del_thermo(data: DeleteSchema, token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> ResponseSchema:
    await auth_check(token, session, "perm_delete_thermo")

    query = select(ThermoModel).where(ThermoModel.id == data.id)
    result = await session.execute(query)
    result = result.scalars().first()
    if result is None:
        raise HTTPException(status_code=403, detail="thermo does not exist")

    session.delete(result)
    await session.commit()

    return ResponseSchema(status=True, reason="Deleted")
