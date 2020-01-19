import os
import sys
import boto3

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
region = os.getenv('REGION', None)
instance = os.getenv('INSTANCE', None)
instances = []
instances.append(instance)

if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def lambda_handler(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        text = line_event.message.text
        ec2 = boto3.client('ec2', region_name=region)

        if text == 'start':
            ec2.start_instances(InstanceIds=instances)
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text='ec2 server start'))
        elif text == 'stop':
            ec2.stop_instances(InstanceIds=instances)
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text='ec2 server stop'))

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json