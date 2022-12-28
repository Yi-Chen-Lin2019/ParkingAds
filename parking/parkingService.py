#!/usr/bin/env python
import pika
import os

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))

channel = connection.channel()

def getAvailable(location):
    response = '''
    Hi, welcome to {}
    Here are the nearest parking lots:
    ''' .format(location)
    return response

def on_request(ch, method, props, body):
    location = body
    print('parking service on request, location: ',location)
    response = getAvailable(location)

    print('reply to: ', props.reply_to)

    ch.basic_publish(exchange='topic_find_parking',
                     routing_key=props.reply_to+'.parking',
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='parking', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()