from fastapi import APIRouter, HTTPException, status

from db.schemas.user import user_schema
from db.models.user import User
from db.client import db_client
from bson import ObjectId

router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={status.HTTP_404_NOT_FOUND: {"Message": "No encontrado"}},
)


# Entidad user


users_fake = []


@router.get("/", response_model=list[User])
async def users():
    return user_schema(db_client.users.find())


# path
@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))


# Query
@router.get("/")
async def user(id: int):
    return search_user(id)


# PATH PARAMETRO OBLIGATORIO. URL DINAMICO/USER/ID/PALABRAFIJA/OBJETO/CARACTERISTICA

# QUERY PARAMETROS NO SON NECESARIOS PARA LA PETICIÓN


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe"
        )

    user_dict = dict(user)

    del user_dict["id"]  # se autogenera en mongodb

    id = db_client.users.insert_one(user_dict).inserted_id

    new_user = db_client.users.find_one({"_id": id})

    return User(**new_user)  # Crear tipo usuario


@router.put("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
    user_dict = dict(user)
    del user_dict["id"]

    try:
        db_client.local.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict
        )
    except:
        return {"error": "No se ha encontrado el usuario"}

    return search_user("_id", ObjectId(user.id))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"Error": "No se ha encontrado usuario"}


def search_user(field: str, key):
    try:
        user = db_client.users.find_one({field: key})
        return User(**user_schema(user))
    except:
        return {"error": "No se ha encontrado nada"}
