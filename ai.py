import random

from model import *

"""The AI classes."""

class DumbAI():
	"""Artificial: yes. Intelligent: not so much."""
	def __init__(self, bs, target, own):
		self.bs = bs
		self.ships = []
		self.target = target
		self.own = own
		
		self.makeShips()
		
	def makeShips(self):
		"""Construct my ships."""
		for l in self.bs.WORDS:
			self.ships.append(Ship(l))
		
	def placeShips(self):
		"""Place my ships."""
		shipsToPlace = len(self.ships)
		while(shipsToPlace > 0):
			x = random.randint(0, self.bs.COLS)
			y = random.randint(0, self.bs.ROWS)
			vert = random.randint(0, 1) == 1
			
			if(self.own.placeShip(self.ships[shipsToPlace - 1], x, y, vert)):
				shipsToPlace -= 1
				
	def randomCell(self):
		x = random.randint(0, self.bs.COLS - 1)
		y = random.randint(0, self.bs.ROWS - 1)
		
		return self.target.matrix[y][x]
				
	def fire(self):
		"""Fire at the user. Poor user..."""
		cell = self.randomCell()
		
		while(not cell.fireAt()):
			cell = self.randomCell()
			
		return cell
			
class SmartAI(DumbAI):
	"""We'll see about that."""
	def __init__(self, bs, target, own):
		super(SmartAI, self).__init__(bs, target, own)
		self.lastCell = None
		
	def placeShips(self):
		super(SmartAI, self).placeShips()
		
	def fire(self):
		"""Slightly smarter than DumbAI: remember the cell last fired
		at if that was a hit and fire around it. Otherwise fire at
		random."""
		if(self.lastCell == None):
			cell = super(SmartAI, self).fire()
			
			# We just hit a Ship, but not sunk it
			if(cell.ship != None and cell.ship.health > 0):
				self.lastCell = cell
		else:
			candidates = []
			x = self.lastCell.x
			y = self.lastCell.y
			if(x - 1 >= 0):
				candidates.append(self.target.matrix[y][x - 1])
			if(x + 1 < self.target.cols - 1):
				candidates.append(self.target.matrix[y][x + 1])
			if(y - 1 >= 0):
				candidates.append(self.target.matrix[y - 1][x])
			if(y + 1 < self.target.rows - 1):
				candidates.append(self.target.matrix[y + 1][x])
				
			# filter out scorched ones
			candidates = [cell for cell in candidates if not cell.scorched]
			
			# no smart candidates: just fire random again
			if(len(candidates) == 0):
				self.lastCell = None
				return self.fire()
				
			# pick one at random
			cell = random.choice(candidates)
			cell.fireAt()
			
			# we know the cell is scorched
			if(cell.ship != None and cell.ship.health > 0):
				self.lastCell = cell
			# otherwise leave it at the previous and try another one next turn
