import decimal
import asyncio
import aio_pika
from common import config
from common.schemas import Event, MessageDTO, NewStateDTO, NewCoefficientDTO
from common.enumerations import MessageType, EventState


class MessageQueue:
    """
    Класс отвечающий за отправку сообщений в очередь сообщений.
    """

    async def send_new_event(self, event: Event) -> None:
        model = MessageDTO(type=MessageType.NEW_EVENT.value, payload=event)
        await self._send_message(model)

    async def send_initial_events(self, events: list[Event]) -> None:
        model = MessageDTO(type=MessageType.INITIAL.value, payload=events)
        await self._send_message(model)

    async def send_new_state(self, event_id: str, state: EventState) -> None:
        model = MessageDTO(
            type=MessageType.EVENT_STATE_CHANGED.value,
            payload=NewStateDTO(event_id=event_id, new_state=state.value),
        )
        await self._send_message(model)

    async def send_new_coefficient(
        self, event_id: str, new_coefficient: decimal.Decimal
    ) -> None:
        model = MessageDTO(
            type=MessageType.EVENT_STATE_CHANGED.value,
            payload=NewCoefficientDTO(
                event_id=event_id, new_coefficient=new_coefficient
            ),
        )
        await self._send_message(model)

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

    async def _send_message(self, message: MessageDTO) -> None:
        connection = await self._establish_connection()
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.model_dump_json().encode()),
                routing_key=config.AMQP_QUEUE,
            )
