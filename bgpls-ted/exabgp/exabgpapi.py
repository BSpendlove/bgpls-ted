import logging
import json
from os import environ

from modules.rabbitmq import Publisher
from sys import stdin

logging.basicConfig(level=logging.DEBUG)


def message_parser(line):
    temp_message = None
    try:
        temp_message = normalize_keys(json.loads(line), convert)
    except Exception as error:
        logging.debug("Error trying json.loads() on line: \n{}".format(line))
        logging.debug("Exception Error was: {}".format(error))
    return temp_message


def normalize_keys(obj, convert):
    # Recursively goes through the dictionary obj and replaces keys with the convert function.
    # https://stackoverflow.com/questions/11700705/python-recursively-replace-character-in-keys-of-nested-dictionary/38269945 by baldr
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = normalize_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(normalize_keys(v, convert) for v in obj)
    else:
        return obj
    return new


def convert(k):
    # Convert - and . to _
    return k.replace("-", "_").replace(".", "_")


publisher = Publisher(
    config={
        "host": environ.get("RABBITMQ_HOST"),
        "username": environ.get("RABBITMQ_USERNAME"),
        "password": environ.get("RABBITMQ_PASSWORD"),
    }
)

# Initial connect (however publisher.publish will try to handle reconnections)
publisher.connect()

counter = 0
while True:
    try:
        line = stdin.readline().strip()

        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0

        message = message_parser(line)
        url = None
        if message:
            logging.debug(
                "Message received from peer...\n{}".format(json.dumps(message))
            )
            # Send all messages to RabbitMQ Exchange (bgplsapi)
            publisher.publish(message)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")
        publisher.close()
        pass
    except IOError:
        logging.info("IOError")
        publisher.close()
        pass
