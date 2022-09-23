from os import environ
from modules.exabgp_message_handler import exabgp_generic_handler
import multiprocessing
import pika
import os, sys
import json


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=environ.get("RABBITMQ_HOST"),
            credentials=pika.PlainCredentials(
                environ.get("RABBITMQ_USERNAME"), environ.get("RABBITMQ_PASSWORD")
            ),
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=environ.get("RABBITMQ_EXCHANGE", "bgpls"))
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange=environ.get("RABBITMQ_EXCHANGE", "bgpls"),
        queue=queue_name,
        routing_key=environ.get("RABBITMQ_ROUTING_KEY", "bgplsapi"),
    )

    def callback(ch, method, properties, body):
        bgp_update = json.loads(body.decode())
        p = multiprocessing.Process(target=exabgp_generic_handler, args=(bgp_update,))
        p.start()

    channel.basic_consume(queue="", auto_ack=True, on_message_callback=callback)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
