import sys
import random
from PyQt4 import QtGui, QtCore

class Observable():
	def __init__(self):
		self.obs = []
			
	def addObs(self, obs):
		self.obs.append(obs)
		
	def delObs(self, obs):
		self.obs.remove(obs)
		
	def update(self, arg):
		for o in self.obs:
			o.update(self, arg)

class Cell():
	def __init__(self, grid, x, y):
		self.grid = grid
		self.ship = None
		self.idx = 0
		self.scorched = False
		self.x = x
		self.y = y
		
	def placeShip(self, ship, vert):
		return self.grid.placeShip(ship, self.x, self.y, vert)
		
	def fireAt(self):
		if(self.scorched):
			return False
			
		if(self.ship != None):
			self.ship.scorch()
			
		self.scorched = True
		self.grid.update(self)
		return True
		
	def __str__(self):
		return str(self.ship)[self.idx] if self.ship != None else " "

class Grid(Observable):
	def __init__(self, rows, cols):
		super(Grid, self).__init__()
		
		self.rows = rows
		self.cols = cols
		self.obs = []
		self.matrix = [[Cell(self, i, j) for i in range(cols)] for j in range(rows)]
	
	def placeShip(self, ship, x, y, vert):
		if(vert):
			ship.w = ship.length
			ship.h = 1
		else:
			ship.w = 1
			ship.h = ship.length
		
		if(x < 0 or x + ship.w > self.cols or y < 0 or y + ship.h > self.rows):
			return False
			
		for row in range(y, y + ship.h):
			for col in range(x, x + ship.w):
				if(self.matrix[row][col].ship != None):
					return False
		
		for row in range(y, y + ship.h):
			for col in range(x, x + ship.w):
				ship.x = x
				ship.y = y
				
				cell = self.matrix[row][col]
				cell.ship = ship
				cell.idx = col - ship.x + row - ship.y
				cell.scorched = False
				
		ship.place()
		self.update(ship)
		return True
		
	def fireAt(self, x, y):
		if(x < 0 or x >= self.cols or y < 0 or y >= self.rows):
			return False
			
		cell = self.matrix[y][x]
		
		return cell.fireAt()

class Ship(Observable):
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
		self.placed = True
		self.update(self)
		
	def scorch(self):
		self.health -= 1
		
		return self.health != 0	

	def __str__(self):
		return self.text

class ShipButton(QtGui.QPushButton):
	def __init__(self, bs, ship):
		super(ShipButton, self).__init__()
		self.ship = ship
		self.bs = bs
		self.setText(str(self.ship))
		self.clicked.connect(self.clickEvent)
	
	def update(self, obs, ship):
		if(self.ship.placed):
			self.setEnabled(False)
		else:
			self.setEnabled(True)
			
		self.bs.update()
	
	def clickEvent(self, event):
		self.bs.currentShip = self.ship
		self.update(None, None)
		
class GridButton(QtGui.QPushButton):
	def __init__(self, cell, bs, isTarget):
		super(GridButton, self).__init__(" ")
		self.cell = cell
		self.bs = bs
		self.isTarget = isTarget
		if(isTarget):
			self.clicked.connect(self.clickFireMissile)
		else:
			self.clicked.connect(self.clickPlaceShip)
		
	def update(self, grid, ship):		
		if(self.cell.scorched):
			if(self.cell.ship != None):
				if(self.isTarget):
					self.setText(str(self.cell))
				else:
					self.setText(str(self.cell) + "!")
			else:
				self.setText("!")
		else:
			if(not self.isTarget):
				self.setText(str(self.cell))
		
	def clickPlaceShip(self, event):
		if(self.bs.currentShip == None):
			return
		
		if(self.cell.placeShip(self.bs.currentShip, self.bs.orientVert)):
			self.bs.currentShip = None
			
	def clickFireMissile(self, event):
		print("Clickety " + str(self.cell))
		if(self.bs.gameMode != self.bs.MODE_FIRING):
			return
			
		self.bs.userFire(self.cell)
		
class ButtonGrid(QtGui.QWidget):
	def __init__(self, bs, grid, isTarget):
		super(ButtonGrid, self).__init__()
		self.buttons = [GridButton(cell, bs, isTarget) for sublist in grid.matrix for cell in sublist] # thanks, StackOverflow!
		self.bs = bs
		self.grid = grid
		self.target = False
		self.initGUI()
		
	def initGUI(self):
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		for btn in self.buttons:
			self.grid.addObs(btn)
			self.layout.addWidget(btn, btn.cell.x, btn.cell.y)
			
class AI():
	def __init__(self, bs):
		self.bs = bs
		self.ships = []
		
		self.makeShips()
		
	def makeShips(self):
		for l in self.bs.WORDS:
			self.ships.append(Ship(l))
		
	def placeShips(self):
		shipsToPlace = len(self.ships)
		while(shipsToPlace > 0):
			x = random.randint(0, self.bs.COLS)
			y = random.randint(0, self.bs.ROWS)
			vert = random.randint(0, 1) == 1
			
			if(self.bs.targetGrid.placeShip(self.ships[shipsToPlace - 1], x, y, vert)):
				shipsToPlace -= 1
		print("Enemy ships placed")
				
	def fire(self):
		print("Enemy is firing missiles")
		x = random.randint(0, self.bs.COLS - 1)
		y = random.randint(0, self.bs.ROWS - 1)
		
		while(not self.bs.userGrid.fireAt(x, y)):
			x = random.randint(0, self.bs.COLS - 1)
			y = random.randint(0, self.bs.ROWS - 1)

class Battleship(QtGui.QWidget):
	ROWS = 10
	COLS = 10
	MODE_SETUP = 1
	MODE_FIRING = 2
	MODE_GAMEOVER = 3
	WORDS = ["in", "or", "def", "for", "none", "else"]
	
	def __init__(self):
		super(Battleship, self).__init__()
		self.ships = []
		# modi
		self.currentShip = None
		self.orientVert = False
		self.gameMode = self.MODE_SETUP
		self.shipsUnplaced = len(self.WORDS)
		
		self.userGrid = Grid(self.ROWS, self.COLS)
		self.targetGrid = Grid(self.ROWS, self.COLS)
		
		self.userBtnGrid = ButtonGrid(self, self.userGrid, False)
		self.targetBtnGrid = ButtonGrid(self, self.targetGrid, True)
		
		self.ai = AI(self)
		self.aisTurn = False
		
		self.makeShips()
		self.initGUI()
		
	def makeShips(self):
		for l in self.WORDS:
			self.ships.append(Ship(l))
		
	def setUpShipBtns(self):
		ret = QtGui.QWidget()
		uiGrid = QtGui.QGridLayout()
		ret.setLayout(uiGrid)
		
		self.orientBtn = QtGui.QPushButton("Horizontal")
		self.orientBtn.clicked.connect(self.clickOrientBtn)
		uiGrid.addWidget(self.orientBtn, 1, 1)
		
		i = 2
		for s in self.ships:
			btn = ShipButton(self, s)
			self.userGrid.addObs(btn)
			uiGrid.addWidget(btn, i, 1)
			i += 1
			
		return ret

	def initGUI(self):
		uiGrid = QtGui.QGridLayout()
		self.setLayout(uiGrid)
		self.scoreWidget = QtGui.QWidget()
		self.scoreGrid = QtGui.QGridLayout()
		self.scoreWidget.setLayout(self.scoreGrid)
		
		self.msgLabel = QtGui.QLabel("Place your Battleships up there ↑")
		
		self.ownShipsLabel = QtGui.QLabel("Own ships: " + str(len(self.ships)))
		self.aiShipsLabel = QtGui.QLabel("Enemy ships: " + str(len(self.ai.ships)))
		self.scoreGrid.addWidget(self.ownShipsLabel, 1, 1)
		self.scoreGrid.addWidget(self.aiShipsLabel, 2, 1)
		
		uiGrid.addWidget(self.userBtnGrid, 1, 1)
		uiGrid.addWidget(self.setUpShipBtns(), 1, 2)
		uiGrid.addWidget(self.msgLabel, 2, 1, 1, -1)
		uiGrid.addWidget(self.targetBtnGrid, 3, 1)
		uiGrid.addWidget(self.scoreWidget, 3, 2)
		
		self.show()
		
	def turn(self):
		if(self.aisTurn):
			self.aisTurn = False
			self.ai.fire()
		else:
			self.msgLabel.setText("Fire your missiles down there ↓")
			
	def userFire(self, cell):
		if(not cell.fireAt()):
			self.msgLabel.setText("You already fired here, choose another target")
		else:
			self.aisTurn = True
			self.update()
		
	def setUpdate(self):
		unplaced = len(self.WORDS)
		for s in self.ships:
			if(s.placed):
				unplaced -= 1
				
		self.shipsUnplaced = unplaced
		
		if(self.shipsUnplaced == 0):
			self.orientBtn.setEnabled(False)
			self.ai.placeShips()
			self.gameMode = self.MODE_FIRING
	
	def livingShips(self, ships):
		shipsAlive = len(ships)
		for s in ships:
			if(s.health == 0):
				shipsAlive -= 1
				
		return shipsAlive
	
	def fireUpdate(self):
		self.turn()
		
		ownShips = self.livingShips(self.ships)
		self.ownShipsLabel.setText("Own ships: " + str(ownShips))
		aiShips = self.livingShips(self.ai.ships)
		self.aiShipsLabel.setText("Enemy ships: " + str(aiShips))
		
		if(ownShips == 0):
			self.msgLabel.setText("You lose!")
			self.gameMode = self.MODE_GAMEOVER
			
		if(aiShips == 0):
			self.msgLabel.setText("You win!")
			self.gameMode = self.MODE_GAMEOVER
		
	def update(self):
		if(self.gameMode == self.MODE_SETUP):
			self.setUpdate()
			
		if(self.gameMode == self.MODE_FIRING):
			self.fireUpdate()
			
		if(self.gameMode == self.MODE_GAMEOVER):
			resetBtn = QtGui.QPushButton("Restart")
			resetBtn.clicked.connect(self.reset)
			self.scoreGrid.addWidget(resetBtn, 3, 1)
			
	def reset(self):
		self.close()
		
		Battleship()
	
	def clickOrientBtn(self):
		self.orientVert = not self.orientVert
		self.orientBtn.setText("Vertical" if self.orientVert else "Horizontal")
		
def main():
	app = QtGui.QApplication(sys.argv)
	bs = Battleship()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
