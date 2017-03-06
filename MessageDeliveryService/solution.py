#!/usr/bin/python3.6
#***Author: Luc iBATA
#***ibataluc@gmail.com
#***https://github.com/ibata
#***https://www.hackerrank.com/lucibata
#***http://linkedin.com/in/lucibata
#***https://itunes.apple.com/sa/developer/luc-ibata-okalobe/id990945101
#***Date: 03/06/2017


import queue
import json
import hashlib
import base64
from collections import OrderedDict
from operator import itemgetter

"""Q Challenge
Your challenge is to implement a simple message delivery service. This service accepts (enqueues) messages through a single interface. It applies a set of transformation rules to the data, then chooses which output queue should get the message based on a series of dispatching rules. It also delivers the parts of multi-message sequences in order."""

class MessageDeliveryService:
	
	def __init__(self):
		#***Constructor Initialisation: There are five output queues, numbered 0 through 4.
		self.msg_queue_list = [queue.Queue(), queue.Queue(),queue.Queue(),queue.Queue(),queue.Queue()]
		#***Certain messages may be parts of a sequence. Such messages include some special fields:
		self.sequenced_msgs= []
		self.seq_dict= {}
		
    """You must add a field hash to any message that has a field _hash. The value of _hash may be the name of another field. The value of your new field hash must contain the base64-encoded SHA-256 digest of the UTF-8-encoded value of that field"""
	@staticmethod 
	def encode(value):
	  valueutf8 = value.encode(encoding='UTF-8',errors='strict')
	  valuebase64 = base64.b64encode(valueutf8)
	  valuesha256 = hashlib.sha256(valuebase64).hexdigest()
	  return valuesha256


	
	#***Dispatch Rules
	"""You must implement the following "dispatch" rules to decide which queue gets a message. These rules must be applied in order; the first rule that matches is the one you should use. """
	@staticmethod 
	def dispatch(msg):
	  if "_special" in msg:
	    return 0
	  elif "hash" in msg:
	    return 1
	  else:
	    for key, value in msg.items():
	      if not key.startswith("_"):
	        if isinstance (value, str):
	          if 'muidaQ' in value:
	            return 2
	        elif isinstance(value,int):
	          return 3
	  return 4
	
	#***Transformation Rules
	"""You must implement the following transformations on input messages. These rules must be applied in order, using the transformed output in later steps. Multiple rules may apply to a single tuple."""
	@staticmethod 
	def transform(message):
	  for key, value in message.items():
	    """You must string-reverse any string value in the message that contains the exact string Qadium.
	   For instance, {"company": "Qadium, Inc.", "agent": "007"} changes to {"company": ".cnI ,muidaQ", "agent": "007"}."""
	    if value == "Qadium, Inc.":
	      message[key] = value[::-1]
	
	    """You must replace any integer values with the value produced by computing the bitwise negation of that integer's value.
	For instance, {"value": 512} changes to {"value": -513}"""
	    if isinstance(value,int):
	      n = int(value)
	      message[key] = ~n
	    else:
	      pass
	      
	    if '_hash' in key:
	      message['hash'] = encode(value)
	
	
	    """Transformation rules, except the hash rule, must ignore the values of "private" fields whose names begin with an underscore (_)."""
	
	    if key.startswith( '_') and not key.startswith( '_hash' ):
	      message[key] = "ignored"
	
	  #***Return tranformation result
	  return message
	

	#***The output queue must enqueue messages from a sequence as soon as it can; don't try to wait to output all messages of a sequence at a time. The output queue must return messages within a sequence in the correct order by part number (message 0 before message 1, before message 2 ...).
	def enqueue_sequence(self, msg):
		seq_name = msg['_sequence']
		#***Is first message in sequence?
		if msg['_part'] == 0:
			qnum = self.dispatch(msg)
			self.seq_dict = { seq_name: {'route': qnum, 'last': 0}}
			self.msg_queue_list[qnum].put(json.dumps(msg))
		else:
			self.sequenced_msgs.append(msg)

		self.sequenced_msgs.sort(key = itemgetter('_sequence', '_part'), reverse = True)
		for i in reversed(range(len(self.sequenced_msgs))):
			if seq_name in self.seq_dict:
				if self.sequenced_msgs[i].get('_sequence') == seq_name and self.sequenced_msgs[i].get('_part') == self.seq_dict[seq_name]['last']+1:
					self.msg_queue_list[self.seq_dict[seq_name]['route']].put(json.dumps(self.sequenced_msgs.pop(i))) 
					self.seq_dict[seq_name]['last'] += 1  
	
	
	def enqueue(self, msg):
		#***Loads JSON to a List 
		message = json.loads(msg, object_pairs_hook=OrderedDict)
		#***Transformation rules
		transformed_msg = self.transform(message)

		if '_sequence' in transformed_msg:
			self.enqueue_sequence(transformed_msg)
		else:
			#***dispatch rules 
			qnum = self.dispatch(transformed_msg)
			qmsg= json.dumps(transformed_msg)
			self.msg_queue_list[qnum].put(qmsg)

	def next(self, qnum):
		return self.msg_queue_list[qnum].get(block=False)
			
def get_message_service():
	"""function that we can use to get a clean instance of your solution"""
	return MessageDeliveryService()