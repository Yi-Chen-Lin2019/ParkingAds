#!/usr/bin/env python
import pika
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='IGhg5sxWUxzQlck2GqHWkRgbc7aGA4RM',
    client_secret='h4BFfroouLoPFac3'
)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

def getAvailable(location):
    return amadeus.reference_data.locations.hotel.get(keyword=location, subType='HOTEL_LEISURE').data[0:5]

def on_request(ch, method, props, body):
    response = getAvailable(body)
    print('parking service on request, location: ',body)

    ch.basic_publish(exchange='topic_find_parking',
                     routing_key=props.reply_to+'.hotel',
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='hotel', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()