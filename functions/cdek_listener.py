import logging
import config

def handler(event, context):
    logging.info(event['body'])

    return {
        'statusCode': 200,
        'body': '!',
    }