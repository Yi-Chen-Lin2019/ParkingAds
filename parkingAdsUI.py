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
        self.channel.exchange_declare(exchange='topic_find_parking', exchange_type='topic')

        result = self.channel.queue_declare(queue='UI', exclusive=True)
        self.callback_queue = result.method.queue

        binding_keys = "response.#"
        self.channel.queue_bind(exchange='topic_find_parking', queue=self.callback_queue, routing_key=binding_keys)

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response)

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
            ),
            body=self.message)
        self.connection.process_data_events(time_limit=None)


parkme = ParkingAdsClient()

print(" [x] Requesting parking information")
parkme.call()