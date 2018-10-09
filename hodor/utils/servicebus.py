from azure.servicebus import ServiceBusService, Message, Queue
import json

'''
def send_to_queue(data, queue):
    
    svcbus = ServiceBusService(
        service_namespace='hodor-bus',
        shared_access_key_name='RootManageSharedAccessKey',
        shared_access_key_value='ALTFhEmmX1/Wm62g52DdG0qy5QRIDQlwnHnwyOkCimI=')

    event = Message(json.dumps(data))
    svcbus.send_queue_message(queue, event)

'''


def send_to_queue(data, queue):
    
    svcbus = ServiceBusService(
        service_namespace='botista',
        shared_access_key_name='RootManageSharedAccessKey',
        shared_access_key_value='0/O8pigV09yoxSrSpEjKK+uoMWS1JYYJQEbnbzVxnpA=')

    event = Message(json.dumps(data))
    svcbus.send_queue_message(queue, event)
