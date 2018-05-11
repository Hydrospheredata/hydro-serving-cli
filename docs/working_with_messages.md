# Work with Apache Kafka

hydro-serving can store serving messages in Kafka topic.
Since every serving message serialized with protobuf, sending and receiving messages could be inconvinient.

CLI provides methods to send and retreive messages from Kafka topic with de-/serialization by the way.