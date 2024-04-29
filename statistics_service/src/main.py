import asyncio
from contextlib import asynccontextmanager
import json
from aiokafka import AIOKafkaConsumer
import uvicorn
import clickhouse_connect
from fastapi import FastAPI, Response

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
            if 'user_id' not in value:
                value['user_id'] = None 
            client.insert('snet_statistics.stats', [[value['post_id'], value['user_id'], value['type']]], column_names=['post_id', 'user_id', 'type'])
    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop.create_task(consume())
    yield
    await consumer.stop()

server = FastAPI(lifespan=lifespan)
client = clickhouse_connect.get_client(host='snet-clickhouse')

@server.get('/stats')
async def get_stats():
    return Response(status_code=200)

if __name__ == '__main__':
    uvicorn.run(server, host="0.0.0.0", port=8002)
