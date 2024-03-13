from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import datetime, uvicorn, jwt
from fastapi import FastAPI, Depends, HTTPException, Response
from passlib.context import CryptContext
from datetime import datetime, timedelta

from db import SessionLocal
import models, schemas

SECRET_KEY = "some_secret_key"
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=30)

server = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None

@server.post('/register')
async def register(auth_user: schemas.AuthSchema, db=Depends(get_db)):
    auth_user.password = pwd_context.hash(auth_user.password)
    if db.query(models.User).filter((models.User.login == auth_user.login)).first() is not None:
        raise HTTPException(status_code=400, detail="User with this login already exists")
    entity = models.User(**auth_user.dict())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity.id

@server.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    query = db.query(models.User).filter((models.User.login == form_data.username))
    if query.first() is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = query.first()
    is_password_equals = pwd_context.verify(form_data.password, user.password)
    if not is_password_equals:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    jwt_token = create_jwt_token({"sub": user.login})
    return {"access_token": jwt_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(models.User).filter((models.User.login == decoded_data["sub"]))
    if user.first() is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user.first()

@server.get('/users', response_model=list[schemas.UserSchema])
async def list_users(db=Depends(get_db)):
    users = db.query(models.User).all()
    return users

@server.post('/user/update')
async def update_user(user: schemas.UserCanBeChangedSchema, current_user: models.User = Depends(get_current_user), db = Depends(get_db)):
    query = db.query(models.User).filter((models.User.login == current_user.login))

    if query.first() is None:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    query.update(user.dict(), synchronize_session=False)
    db.commit()
    return Response(status_code=200)

if __name__ == '__main__':
    uvicorn.run(server, host="0.0.0.0", port=8000)
