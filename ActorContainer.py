from Actor import Actor
from Container import Container

class ActorContainer(Actor, Container):
	"""
	Base class for containers which are also actors
	"""
	
	def __init__(self):
		Actor.__init__(self)
		Container.__init__(self)
	
	def update(self, deltaT):
		for actor in self.actors:
			actor.update(deltaT)
	
	def die(self):
		# FIXME: awkward hack (?) to make sure actors clean up their signal
		# handlers
		for actor in self.actors:
			actor.die()
		Actor.die(self)

# vim: set ts=4 sts=4 sw=4 ai noet :
