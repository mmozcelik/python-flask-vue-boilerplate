# -*- coding:utf-8 -*-

import json, boto3, config, logging
from app.utils.redis import redis

queue_url = None
sqs_client = None
try:
    queue_url = config.SQS_QUEUE_URL
    sqs_client = boto3.client('sqs', config.REGION)
except:
    pass

CUSTOM_QUEUES = ["export"]


def send_task(queue_name, params, name=None, countdown=0, retry_count=0, expires=0, retry_wait=3):
    if config.ENV.lower() == 'development':
        import _thread, time
        from werkzeug import import_string

        def delayed_task(queue_name, params, delay):
            time.sleep(delay)
            formatted_queue = queue_name.replace('massive-', 'massive.').replace('-', '')
            method = import_string('app.workers.{0}.process'.format(formatted_queue))

            method(**params)

        delayed_task(queue_name, params, countdown)
        #_thread.start_new_thread(delayed_task, (queue_name, params, countdown))

        return {'MessageId': '3'}
    else:
        if name and expires > 0:
            if redis.get('task_{0}'.format(name)):
                raise Exception('Task already exists with same name!')
            else:
                redis.set('task_{0}'.format(name), "1", expire=expires)

        queue_url_suffix = 'default'
        for queue_prefix in CUSTOM_QUEUES:
            if queue_prefix in queue_name:
                queue_url_suffix = queue_prefix
                break

        result = sqs_client.send_message(
            QueueUrl=queue_url + "-" + queue_url_suffix,
            MessageBody=json.dumps(params),
            DelaySeconds=countdown,
            MessageAttributes={
                'queueName': {
                    'DataType': 'String',
                    'StringValue': queue_name
                },
                'retryCount': {
                    'DataType': 'Number',
                    'StringValue': str(retry_count)
                },
                'retryWait': {
                    'DataType': 'Number',
                    'StringValue': str(retry_wait)
                }
            }
        )

        logging.info("sendtask: for queue {0}(suffix {1}) with retry count {2} and params {3}".format(queue_name, queue_url_suffix, retry_count, json.dumps(params)))
        return result


def remove_task(queue_name, message_id):
    logging.info("removetask: for queue {0} with message id {1}".format(queue_name, message_id))
    redis.set('delete_queue_{0}_item_{1}'.format(queue_name, message_id), 1, expire=24 * 3600)
