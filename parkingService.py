#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()
channel.exchange_declare(exchange='topic_find_parking', exchange_type='topic')

result = channel.queue_declare(queue='parking', exclusive=True)
queue_name = result.method.queue

binding_keys = "find.#"
channel.queue_bind(exchange='topic_find_parking', queue=queue_name, routing_key=binding_keys)

def getAvailableLots(location):
    response = '''
    Hi, welcome to {}
    More content comming...
    ''' .format(location)
    return response

def on_request(ch, method, props, body):
    location = body
    print('parking service on request, location: ',location)
    response = getAvailableLots(location)

    ch.basic_publish(exchange='topic_find_parking',
                     routing_key='response.parking',
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()