#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_find_parking', exchange_type='topic')

routing_key = 'find.parking'
message = 'Paris'
channel.basic_publish(
    exchange='topic_find_parking', routing_key=routing_key, body=message)
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()