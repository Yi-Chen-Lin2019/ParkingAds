#!/usr/bin/env python
import pika
import requests
from bs4 import BeautifulSoup
import json
import seqlog
from pygelf import GelfUdpHandler
import logging

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

def getAvailable():
    response = 'some ads'
    try:
        page = requests.get('http://localhost:83').text
        soup = BeautifulSoup(page, "html.parser")
        ad_text = [t.get_text() for t in soup.find_all("div")]
        response = 'Ad: '+ad_text[0]
    except:
        seqlog.log_to_seq(
        server_url="http://localhost:5341/",
        api_key="14X7q4Dngg8sBbKa72ZK",
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