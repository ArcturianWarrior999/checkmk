# IBM MQ

Monitoring for **IBM MQ** (formerly IBM WebSphere MQ) message-queue middleware.

An agent plugin collects the output of the `runmqsc` administration commands
and the queue-manager process list. The check plugins in this package monitor
queue managers, channels and queues (status, message depths and queue-time
performance), and contribute the discovered managers, channels and queues to
the HW/SW inventory.
