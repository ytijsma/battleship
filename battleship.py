import sys
import random
from PyQt4 import QtGui, QtCore

class Ship():
	def __init__(self, length, btn):
		self.length = length
		self.w = 1 # translate orientation into width / height
		self.h = length
		self.x = 0 # from top-left (regardless of orientation)
		self.y = 0
		self.placed = False
		self.text = "abcdefghijklmnop"[:self.length]
		self.btn = btn
	
	def placeIn(self, grid, x, y, vertical):
		if(self.placed):
			return False
			
		if(vertical): # it defies all logic
			self.h = 1
			self.w = self.length
		else:
			self.h = self.length
			self.w = 1
			
		if(x < 0 or x + self.w > grid.COLUMNS):
			return False
			
		if(y < 0 or y + self.h > grid.ROWS):
			return False
			
		for row in range(y, y + self.h):
			for col in range(x, x + self.w):
				if(grid.grid[row][col].ship != None):
					return False
		
		self.x = x
		self.y = y
		
		for row in range(y, y + self.h):
			for col in range(x, x + self.w):
				grid.grid[row][col].setShip(self)
				self.placed = True
		
		self.btn.update()
		return True
				
	def remove(self, grid):
		for row in range(y, y + self.h):
			for col in range(x, x + self.w):
				grid.grid[row][col].setShip(None)
				self.placed = False
		
		self.btn.update()

	def __str__(self):
		return self.text

class ShipButton(QtGui.QPushButton):
	def __init__(self, bs, length):
		super(ShipButton, self).__init__()
		self.ship = Ship(length, self)
		self.bs = bs
		self.setText(str(self.ship))
		self.clicked.connect(self.clickEvent)
	
	def update(self):
		if(self.ship.placed):
			self.setEnabled(False)
		else:
			self.setEnabled(True)
			
		self.bs.update()
	
	def clickEvent(self, event):
		self.bs.currentShip = self.ship
		
class GridButton(QtGui.QPushButton):
	def __init__(self, x, y, visible, grid):
		super(GridButton, self).__init__(" ", grid)
		self.x = x
		self.y = y
		self.grid = grid
		self.ship = None
		self.showShip = visible
		self.hit = False
		self.clicked.connect(self.clickEvent)
		
	def update(self):
		if(self.showShip and self.ship != None):
			self.setText(str(self.ship))
		else:
			self.setText(" ")
			
		if(self.hit):
			if(self.ship != None):
				self.setText(str(self.ship))
			else:
				self.setText("!")
		
	def setShip(self, ship):
		self.ship = ship
		self.update()
		
	def clickEvent(self, event):
		print("Clickety")
		print(str(not self.grid.bs.settingUp) + ", " + str(self.grid.target))
		
		if((not self.grid.bs.settingUp) and self.grid.target):
			self.hit = True
			
		if(self.grid.bs.currentShip != None):
			if(self.grid.bs.currentShip.placeIn(self.grid, self.x, self.y, self.grid.bs.orientVert)):
				self.grid.bs.currentShip = None
		
		self.update()
		
class ShipGrid(QtGui.QWidget):
	ROWS = 10
	COLUMNS = 10
	
	def __init__(self, bs):
		super(ShipGrid, self).__init__()
		self.grid = [[0 for cell in range(self.COLUMNS)] for row in range(self.ROWS)]
		self.bs = bs
		self.target = False
		self.initGUI()
		
	def initGUI(self):
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		for (y, x) in [(y, x) for y in range(self.ROWS) for x in range(self.COLUMNS)]:
			btn = GridButton(x, y, True, self)
			self.grid[y][x] = btn
			self.layout.addWidget(btn, x, y)
			
class TargetGrid(QtGui.QWidget):
	ROWS = 10
	COLUMNS = 10
	
	def __init__(self, bs):
		super(TargetGrid, self).__init__()
		self.grid = [[0 for cell in range(self.COLUMNS)] for row in range(self.ROWS)]
		self.bs = bs
		self.target = True
		self.initGUI()
		
	def initGUI(self):
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		for (y, x) in [(y, x) for y in range(self.ROWS) for x in range(self.COLUMNS)]:
			btn = GridButton(x, y, False, self)
			self.grid[y][x] = btn
			self.layout.addWidget(btn, x, y)
		

class Battleship(QtGui.QWidget):
	SHIPLENGTHS = [2, 2 ]#, 3, 3, 4, 4]
	
	def __init__(self):
		super(Battleship, self).__init__()
		self.currentShip = None
		self.orientVert = False
		self.settingUp = True
		self.shipsUnplaced = len(self.SHIPLENGTHS)
		self.targetGrid = None
		self.initUI()

	def initUI(self):
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		self.shipBtns = [ShipButton(self, length) for length in self.SHIPLENGTHS]

		self.userGrid = ShipGrid(self)
		
		# self.enemyGrid = QtGui.QTableWidget(self.ROWS, self.COLUMNS, self)
		self.grid.addWidget(self.userGrid, 1, 1)
		
		btnGrid = QtGui.QWidget(self)
		btnLayout = QtGui.QGridLayout()
		btnGrid.setLayout(btnLayout)
		
		row = 1
		for i in self.shipBtns:
			btnLayout.addWidget(i, row, 1)
			row += 1
		
		self.grid.addWidget(btnGrid, 1, 2)
		self.orientBtn = QtGui.QPushButton("Horizontal")
		self.orientBtn.clicked.connect(self.clickOrientBtn)
		btnLayout.addWidget(self.orientBtn, 0, 1)
		
		self.show()
		
	def setupShips(self):
		if(self.targetGrid != None):
			return
			
		self.targetGrid = TargetGrid(self)
		shipsToPlace = len(self.SHIPLENGTHS)
		while(shipsToPlace > 0):
			randX = random.randint(0, 10)
			randY = random.randint(0, 10)
			randV = random.randint(0, 1) == 1	
			ship = ShipButton(self, self.SHIPLENGTHS[shipsToPlace - 1])
			ship.showShip = False
			ship = ship.ship # a ship shipping ship shipping shipping ships
			if(ship.placeIn(self.targetGrid, randX, randY, randV)):
				shipsToPlace -= 1
		
	def update(self):
		self.shipsUnplaced = len(self.SHIPLENGTHS)
		for btn in self.shipBtns:
			if(btn.ship.placed):
				self.shipsUnplaced -= 1 # fuck your lack of increment/decrement operators, Python
				
		if(self.shipsUnplaced == 0):
			self.orientBtn.setEnabled(False)
			self.settingUp = False
			
		if(not self.settingUp):
			self.grid.addWidget(self.targetGrid, 2, 1)
			self.setupShips()
		
	def clickOrientBtn(self):
		self.orientVert = not self.orientVert
		self.orientBtn.setText("Vertical" if self.orientVert else "Horizontal")
		
def main():
	app = QtGui.QApplication(sys.argv)
	bs = Battleship()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
