from Actor import Actor
from Container import Container

class ActorContainer(Actor, Container):
	"""
	Base class for containers which are also actors
	"""
	
	def __init__(self, parent):
		Actor.__init__(self, parent)
		Container.__init__(self)
	
	def update(self, deltaT):
		for actor in self.actors:
			actor.update(deltaT)
	
	def draw(self):
		for actor in self.actors:
			actor.draw()
	
	def die(self):
		# FIXME: awkward hack (?) to make sure actors clean up their signal
		# handlers
		for actor in set(self.actors):
			actor.die()
		Actor.die(self)

# vim: set ts=4 sts=4 sw=4 ai noet :
