#!/usr/bin/env python
import pika
import requests
from bs4 import BeautifulSoup
import seqlog
import logging
import os

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.environ["RABBITMQ_HOST"]))

channel = connection.channel()

def getAvailable():
    response = 'some ads'
    try:
        page = requests.get(os.environ["ADSERVICE"]).text
        soup = BeautifulSoup(page, "html.parser")
        ad_text = [t.get_text() for t in soup.find_all("div")]
        response = 'Ad: '+ad_text[0]
    except:
        seqlog.log_to_seq(
        server_url=os.environ["SEQ"],
        api_key=os.environ["SEQ_API_KEY"],
        level=logging.error("Cannot fetch ad from service"))
    return response

def on_request(ch, method, props, body):
    print('ad service on request')
    response = getAvailable()

    ch.basic_publish(exchange='topic_find_parking',
                     routing_key=props.reply_to+'.ad',
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ad', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()