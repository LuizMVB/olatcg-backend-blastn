from blastn.blastn_callback import blastn_callback
from consumer import RabbitmqConsumer

rabitmq_consumer = RabbitmqConsumer(blastn_callback)
rabitmq_consumer.start()