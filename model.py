"""These are the 'pure' model classes."""

class Observable():
	"""Implements the Observer pattern. Keeps a list of observers and
	calls their update() method when its update() is fired."""
	def __init__(self):
		self.obs = []
			
	def addObs(self, obs):
		"""Adds the observer."""
		self.obs.append(obs)
		
	def delObs(self, obs):
		"""Removes the observer."""
		self.obs.remove(obs)
		
	def update(self, arg):
		"""Trigger each of the observer's update() to be called."""
		for o in self.obs:
			o.update(self, arg)

class Cell():
	"""A cell in a Battleship Grid. Keeps track of the ship (if it
	contains one), the index in the ship's name, whether it has been hit
	and its position in the grid it is a part of."""
	def __init__(self, grid, x, y):
		self.grid = grid
		self.ship = None
		self.idx = 0
		self.scorched = False
		self.x = x
		self.y = y
		
	def placeShip(self, ship, vert):
		"""Place a ship in the Grid starting on the position of this Cell."""
		return self.grid.placeShip(ship, self.x, self.y, vert)
		
	def fireAt(self):
		"""Fire a missile at this Cell, updates the Ship's health (if 
		there is one here) and returns whether this cell hasn't been
		scorched already."""
		if(self.scorched):
			return False
			
		if(self.ship != None):
			self.ship.scorch()
			
		self.scorched = True
		self.grid.update(self)
		return True
		
	def __str__(self):
		"""Is a single space when there is no Ship here. Otherwise the
		letter in the Ship's name that corresponds to the index of this
		Cell."""
		return str(self.ship)[self.idx] if self.ship != None else " "

class Grid(Observable):
	"""A Battleship Grid. Contains a rows x cols matrix of Cells."""
	def __init__(self, rows, cols):
		super(Grid, self).__init__()
		
		self.rows = rows
		self.cols = cols
		self.obs = []
		self.matrix = [[Cell(self, i, j) for i in range(cols)] for j in range(rows)]
	
	def placeShip(self, ship, x, y, vert):
		"""Place a Ship in the Grid starting at position x, y. Will
		place horizontally unless vert is True. Returns whether the Ship
		has been placed successfully."""
		if(vert):
			ship.w = ship.length
			ship.h = 1
		else:
			ship.w = 1
			ship.h = ship.length
		
		# Check bounds
		if(x < 0 or x + ship.w > self.cols or y < 0 or y + ship.h > self.rows):
			return False
			
		# Check for overlap
		for row in range(y, y + ship.h):
			for col in range(x, x + ship.w):
				if(self.matrix[row][col].ship != None):
					return False
		
		# Place in Cells
		for row in range(y, y + ship.h):
			for col in range(x, x + ship.w):
				ship.x = x
				ship.y = y
				
				cell = self.matrix[row][col]
				cell.ship = ship
				cell.idx = col - ship.x + row - ship.y
				cell.scorched = False
				
		# Tell the Ship it's been placed
		ship.place()
		self.update(ship)
		return True
		
	def fireAt(self, x, y):
		"""Fire a missile at the cell at x, y. Returns False if out of
		bounds, otherwise the value of Cell.fireAt()."""
		if(x < 0 or x >= self.cols or y < 0 or y >= self.rows):
			return False
			
		cell = self.matrix[y][x]
		
		return cell.fireAt()

class Ship(Observable):
	"""A Ship has a name. When it is placed in a Grid it is spread over
	consecutive cells, each cell knows the entire ship and the index in
	the name of the ship that it is to display. Also keeps track of the
	number of hits it has taken. Orientation is determined by width and
	height, it is (by design) theoretically possible to have Ships that 
	are wider than 1 Cell."""
	def __init__(self, name):
		super(Ship, self).__init__()
		
		self.length = len(name)
		self.w = 1 # translate orientation into width / height
		self.h = self.length
		self.x = 0 # from top-left (regardless of orientation)
		self.y = 0
		self.placed = False
		self.text = name
		self.health = self.length
		
	def place(self):
		"""Tell this Ship it's been placed."""
		self.placed = True
		self.update(self)
		
	def scorch(self):
		"""Tell the Ship it's taken a hit, don't call this if it's
		already sunk. Returns whether it has any health left."""
		self.health -= 1
		
		return self.health != 0	

	def __str__(self):
		return self.text
