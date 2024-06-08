import asyncio
from contextlib import asynccontextmanager
import json
from aiokafka import AIOKafkaConsumer
import uvicorn
from fastapi import FastAPI, Response
from proto import serve, client

loop = asyncio.get_event_loop()
consumer = AIOKafkaConsumer("events", bootstrap_servers='kafka:29092', loop=loop)

async def consume():
    while True:
        try:
            await consumer.start()
            break
        except:
            await asyncio.sleep(1)
            continue
    try:
        async for msg in consumer:
            value = msg.value.decode('ascii')
            value = json.loads(value)
            client.insert('snet.posts_stats', [[value['post_id'], value['user_id'], value['type']]], column_names=['post_id', 'user_id', 'type'])
            if value['type'] == 'LIKE':
                client.insert('snet.authors_stats', [[value['author'], value['user_id'], value['post_id']]], column_names=['author', 'user_id', 'post_id'])
    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop.create_task(serve())
    loop.create_task(consume())
    yield
    await consumer.stop()

server = FastAPI(lifespan=lifespan)

@server.get('/stats')
async def get_stats():
    print(client.query('SELECT count FROM (SELECT post_id, count() as count FROM (SELECT DISTINCT user_id, post_id FROM snet.posts_stats WHERE type=\'LIKE\') GROUP BY post_id) WHERE post_id=1').result_rows[0][0])
    return Response(status_code=200)

if __name__ == '__main__':
    uvicorn.run(server, host="0.0.0.0", port=8002)
