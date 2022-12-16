from asyncio import sleep
import geocoder
import pika
import uuid
import sys

class ParkingAdsClient():

    def __init__(self, input_location: None):
        """
        Get location from user's ip address and
        assign message variable with location
        """
        location = geocoder.ip('me')
        self.message = location.json["city"] if input_location is None else input_location
        """
        Send find parking lots request with location to messaging system.
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()
        #self.channel.exchange_declare(exchange='topic_find_parking', exchange_type='topic')

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        print('call back queue: ', self.callback_queue)

        self.channel.queue_bind(
            exchange='topic_find_parking', 
            queue=self.callback_queue,
            routing_key='{}.*'.format(self.callback_queue)
            )

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            print(body)
        else:
            print('wrong corrid')
    def call(self):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='topic_find_parking',
            routing_key='find.parking',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                #delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE # make sure message persistent, won't lost
            ),
            body=self.message)
        self.connection.process_data_events(time_limit=None)

some_location = sys.argv[1]
parkme = ParkingAdsClient(input_location=some_location)

print(" [x] Requesting parking information...")
parkme.call()
parkme.channel.start_consuming()