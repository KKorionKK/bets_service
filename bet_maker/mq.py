import aio_pika
import json
import asyncio
from common import config
from common.schemas import MessageDTO
from common.enumerations import MessageType
from bet_maker.redis_controller import RedisController


class MessageQueue:
    def __init__(self, redis: RedisController):
        self.redis = redis

    async def on_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            data = MessageDTO(**json.loads(message.body))
            print(data)
            if data.type == MessageType.NEW_EVENT:
                await self.redis.save_new_event(data.payload)
            elif data.type == MessageType.EVENT_STATE_CHANGED:
                await self.redis.change_event_status(data.payload)
            elif data.type == MessageType.EVENT_COEFFICIENT_CHANGED:
                await self.redis.change_event_coefficient(data.payload)
            elif data.type == MessageType.INITIAL:
                if data.payload:
                    await self.redis.flush()
                    await self.redis.bulk_save_events(data.payload)
                else:
                    await self.redis.flush()
            else:
                print(f"Undefined message type.\nMessage: {data}")

    async def _establish_connection(self):
        retries = 5
        for i in range(1, retries + 1):
            try:
                connection = await aio_pika.connect_robust(
                    f"amqp://{config.AMQP_USERNAME}:{config.AMQP_PASSWORD}@{config.AMQP_HOST}:{config.AMQP_PORT}{config.AMQP_VIRTUALHOST}",
                )
                print("Connection established")
                return connection
            except Exception as e:
                print(
                    f"Try {i}: Troubles with connecting to RabbitMQ. Retry in 5 seconds..."
                )
                await asyncio.sleep(5)

    async def start_consumer(self) -> None:
        connection = await self._establish_connection()
        try:
            async with connection:
                channel = await connection.channel()

                messages = await channel.declare_queue(config.AMQP_QUEUE)

                messages_exchange = await channel.declare_exchange(
                    config.AMQP_QUEUE,
                    aio_pika.ExchangeType.DIRECT,
                )

                await messages.bind(messages_exchange)

                await messages.consume(self.on_message)

                await asyncio.Future()
        except asyncio.CancelledError:
            print("Consumer task cancelled")
        except Exception as e:
            print(f"Consumer task encountered an error: {e}")
        finally:
            await connection.close()
