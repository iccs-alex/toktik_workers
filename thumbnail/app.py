import redis
import config
import thumbnail
from json import loads
from s3 import getVideo, putVideo
import io

def redis_db():
    redisDB = redis.Redis(host=config.REDIS_HOST,
                          port=config.REDIS_PORT,
                          db=config.REDIS_DB_NUM,
                          decode_responses=True
                          )
    return redisDB


def redis_queue_push(redisDB, message):
    redisDB.publish(config.REDIS_QUEUE_NAME, message)


def redis_queue_pop(redisDB):
    _, message_json = redisDB.brpop(config.REDIS_QUEUE_NAME)
    return message_json


def process_message(redisDB, message_json: str):
    message = loads(message_json)
    print(f"Message received: id={message['id']}, message={message}.")


def main():
    redisDB = redis_db()
    pubsub = redisDB.pubsub()
    pubsub.subscribe(config.REDIS_LISTEN_QUEUE_NAME)
    for message in pubsub.listen():
        redisDB.publish("backend", "having thumbnail extracted")
        channel = message['channel']
        data = message['data']
        if type(data) is not str:
            print("Invalid data type: " + str(type(data)))
            continue
        print("Message data: " + str(data))
        videoFile = getVideo(data)
        videoBytes = videoFile["Body"].read()
        thumbnailBytes = thumbnail.retrieve_thumbnail(videoBytes)
        putVideo(data, thumbnailBytes)
        redisDB.publish(config.REDIS_PUSH_QUEUE_NAME, data)
        print("Message processed")


if __name__ == "__main__":
    main()
