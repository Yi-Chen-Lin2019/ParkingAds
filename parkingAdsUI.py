import geocoder
import pika
import uuid

class ParkingAdsClient():

    def __init__(self):
        """
        Get location from user's ip address
        Assign message variable to location json value
        """
        location = geocoder.ip('me')
        self.message = location.city
        """
        Publish find parking lots with location request to messaging system.
        """
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
   )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=self.message)
        self.connection.process_data_events(time_limit=None)
        return str(self.response)


parkme = ParkingAdsClient()

print(" [x] Requesting parking information")
response = parkme.call()
print(" [.] Got %r" % response)