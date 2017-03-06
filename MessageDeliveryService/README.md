Q Challenge
Your challenge is to implement a simple message delivery service. This service accepts (enqueues) messages through a single interface. It applies a set of transformation rules to the data, then chooses which output queue should get the message based on a series of dispatching rules. It also delivers the parts of multi-message sequences in order.
