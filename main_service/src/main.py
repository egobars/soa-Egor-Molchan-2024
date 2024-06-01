import asyncio
from contextlib import asynccontextmanager
import json
from aiokafka import AIOKafkaProducer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import datetime, uvicorn, jwt, grpc, google.protobuf.json_format
from fastapi import FastAPI, Depends, HTTPException, Response
from passlib.context import CryptContext
from datetime import datetime, timedelta

from db import SessionLocal
import models, schemas, posts_service_pb2, posts_service_pb2_grpc

SECRET_KEY = "some_secret_key"
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=30)

loop = asyncio.get_event_loop()
aioproducer = AIOKafkaProducer(loop=loop, bootstrap_servers='kafka:29092')

@asynccontextmanager
async def lifespan(app: FastAPI):
    while True:
        try:
            await aioproducer.start()
            break
        except:
            await asyncio.sleep(1)
            continue
    yield
    await aioproducer.stop()

server = FastAPI(lifespan=lifespan)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_stub():
    channel = grpc.insecure_channel('posts_service:50051')
    stub = posts_service_pb2_grpc.PostServiceStub(channel)
    return stub

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

@server.post('/post', response_model=schemas.Post)
async def create_post(post: schemas.PostWithoutAuthor, current_user: models.User = Depends(get_current_user), stub=Depends(get_stub)):
    request = posts_service_pb2.PostInfoRequest(
        userId=current_user.id,
        userLogin=current_user.login,
        title=post.title,
        text=post.text
    )
    response = stub.CreatePost(request)
    response = google.protobuf.json_format.MessageToDict(response)
    if 'isOk' not in response:
        raise HTTPException(status_code=response['errorCode'], detail=response['errorText'])
    return response['postInfo']

@server.post('/post/update', response_model=schemas.Post)
async def update_post(post: schemas.UpdatePost, current_user: models.User = Depends(get_current_user), stub=Depends(get_stub)):
    request = posts_service_pb2.UpdatePostInfoRequest(
        postId=post.post_id,
        userId=current_user.id,
        userLogin=current_user.login,
        title=post.title,
        text=post.text
    )
    response = stub.UpdatePost(request)
    response = google.protobuf.json_format.MessageToDict(response)
    print(response)
    if 'isOk' not in response:
        print(response)
        raise HTTPException(status_code=response['errorCode'], detail=response['errorText'])
    return response['postInfo']

@server.delete('/post/{post_id}')
async def delete_post(post_id: str, current_user: models.User = Depends(get_current_user), stub=Depends(get_stub)):
    request = posts_service_pb2.SpecificPostRequest(
        userId=current_user.id,
        postId=int(post_id)
    )
    response = stub.DeletePost(request)
    response = google.protobuf.json_format.MessageToDict(response)
    if 'isOk' not in response:
        raise HTTPException(status_code=response['errorCode'], detail=response['errorText'])
    return Response(status_code=200)

@server.get('/post/{post_id}')
async def get_post(post_id: str, stub=Depends(get_stub)):
    request = posts_service_pb2.SpecificPostRequest(
        postId=int(post_id),
    )
    response = stub.GetPost(request)
    response = google.protobuf.json_format.MessageToDict(response)
    if 'isOk' not in response:
        raise HTTPException(status_code=response['errorCode'], detail=response['errorText'])
    return response['postInfo']

@server.get('/posts', response_model=list[schemas.Post])
async def get_all_posts(cursor: schemas.Cursor, stub=Depends(get_stub), db=Depends(get_db)):
    query = db.query(models.User).filter((models.User.login == cursor.login))
    if query.first() is None:
        raise HTTPException(status_code=404, detail="User doesn't exist")

    request = posts_service_pb2.PostsRequest(
        userLogin=cursor.login,
        cursorStart=cursor.cursor_start,
        cursorEnd=cursor.cursor_end
    )
    response = stub.GetAllPosts(request)
    response = google.protobuf.json_format.MessageToDict(response)
    if 'isOk' not in response:
        raise HTTPException(status_code=response['errorCode'], detail=response['errorText'])
    if 'posts' not in response:
        return []
    return response['posts']

@server.get('/like')
async def like(post: int, current_user: models.User = Depends(get_current_user)):
    value = {
        'post_id': post,
        'user_id': current_user.id,
        'type': 'LIKE'
    }
    await aioproducer.send('events', json.dumps(value).encode("ascii"))
    return Response(status_code=200)

@server.get('/view')
async def view(post: int):
    value = {
        'post_id': post,
        'type': 'VIEW'
    }
    await aioproducer.send('events', json.dumps(value).encode("ascii")) 
    return Response(status_code=200)

if __name__ == '__main__':
    uvicorn.run(server, host="0.0.0.0", port=8000)
