import sys
import random
from PyQt4 import QtGui, QtCore

from model import *
from ai import *

class ShipButton(QtGui.QPushButton):
	"""Selects a Ship for placement in the user-grid."""
	def __init__(self, bs, ship):
		super(ShipButton, self).__init__()
		self.ship = ship
		self.bs = bs
		self.setText(str(self.ship))
		self.clicked.connect(self.clickEvent)
	
	def update(self, obs, ship):
		"""Called by the Observable."""
		if(self.ship.placed):
			self.setEnabled(False)
		else:
			self.setEnabled(True)
			
		self.bs.update(self, ship)
	
	def clickEvent(self, event):
		"""Selects the Ship this button belongs to."""
		self.bs.currentShip = self.ship
		self.update(None, None)
		
class GridButton(QtGui.QPushButton):
	"""Is used for both the user-grid when placing ships, and the target
	grid when firing."""
	def __init__(self, cell, bs, isTarget):
		super(GridButton, self).__init__(" ")
		self.cell = cell
		self.bs = bs
		# Am I in the user-grid or target-grid?
		self.isTarget = isTarget
		if(isTarget):
			self.clicked.connect(self.clickFireMissile)
		else:
			self.clicked.connect(self.clickPlaceShip)
		
	def update(self, grid, ship):
		"""Called by Observable. Updates the label of the button."""	
		if(self.cell.scorched):
			if(self.cell.ship != None):
				if(self.isTarget):
					# Show a Ship(-part) in the target-grid when hit
					self.setText(str(self.cell))
				else:
					# Hit in user-grid
					self.setText(str(self.cell) + "#")
			else:
				# In either grid, but no ship
				self.setText("#")
		else:
			# In user grid, but not hit
			if(not self.isTarget):
				self.setText(str(self.cell))
		
	def clickPlaceShip(self, event):
		"""Called within setup-mode, when clicked. Places the currently
		selected Ship (if one is selected at all)."""
		if(self.bs.currentShip == None):
			return
		
		if(self.cell.placeShip(self.bs.currentShip, self.bs.orientVert)):
			self.bs.currentShip = None
			
	def clickFireMissile(self, event):
		"""Called within firing mode, when clicked. Fires a missile at
		the Cell of this button."""
		if(self.bs.gameMode != self.bs.MODE_FIRING):
			return
			
		self.bs.userFire(self.cell)
		
class ButtonGrid(QtGui.QWidget):
	"""The buttonated front-end for Grid."""
	def __init__(self, bs, grid, isTarget):
		super(ButtonGrid, self).__init__()
		self.buttons = [GridButton(cell, bs, isTarget) for sublist in grid.matrix for cell in sublist] # thanks, StackOverflow!
		self.bs = bs
		self.grid = grid
		self.target = False
		self.initGUI()
		
	def initGUI(self):
		"""Adds the buttons to the UI."""
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		for btn in self.buttons:
			self.grid.addObs(btn)
			self.layout.addWidget(btn, btn.cell.x, btn.cell.y)

class Battleship(QtGui.QWidget):
	"""The main window & controller for the game (which you just lost!)."""
	ROWS = 10
	COLS = 10
	MODE_SETUP = 1
	MODE_FIRING = 2
	MODE_GAMEOVER = 3
	WORDS = ["in", "or", "def", "for", "none", "else"]
	
	def __init__(self):
		"""Initialize all but the UI."""
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
		
		self.smartAI = False
		self.aisTurn = False
		self.ai = None
		
		self.makeShips()
		self.initGUI()
		
		self.show()
		screen = QtGui.QDesktopWidget().screenGeometry()
		w = self.width()
		h = self.height()
		self.setGeometry(screen.width() / 2 - w / 2, screen.height() / 2 - h / 2, w, h)
		
	def makeShips(self):
		"""Make the user's Ships."""
		for l in self.WORDS:
			self.ships.append(Ship(l))
		
	def setUpShipBtns(self):
		"""Make the buttons for selecting user Ships."""
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
		"""Build UI."""
		uiGrid = QtGui.QGridLayout()
		self.setLayout(uiGrid)
		self.scoreWidget = QtGui.QWidget()
		self.scoreGrid = QtGui.QGridLayout()
		self.scoreWidget.setLayout(self.scoreGrid)
		
		self.msgLabel = QtGui.QLabel("Place your Battleships up there ↑")
		
		self.ownShipsLabel = QtGui.QLabel("Own ships: " + str(len(self.ships)))
		self.aiShipsLabel = QtGui.QLabel("Enemy ships: 0")
		self.scoreGrid.addWidget(self.ownShipsLabel, 1, 1)
		self.scoreGrid.addWidget(self.aiShipsLabel, 2, 1)
		self.aiBtn = QtGui.QPushButton("AI: Dumb")
		self.aiBtn.clicked.connect(self.switchAI)
		self.scoreGrid.addWidget(self.aiBtn, 3, 1)
		
		uiGrid.addWidget(self.userBtnGrid, 1, 1)
		uiGrid.addWidget(self.setUpShipBtns(), 1, 2)
		uiGrid.addWidget(self.msgLabel, 2, 1, 1, -1)
		uiGrid.addWidget(self.targetBtnGrid, 3, 1)
		uiGrid.addWidget(self.scoreWidget, 3, 2)
		
		self.setWindowTitle("Battleshipses")
		
	def turn(self):
		"""Either have the AI fire, or the user."""
		if(self.aisTurn):
			self.aisTurn = False
			self.ai.fire()
		else:
			self.msgLabel.setText("Fire your missiles down there ↓")
			
	def userFire(self, cell):
		"""User has clicked a GridButton."""
		if(not cell.fireAt()):
			self.msgLabel.setText("You already fired here, choose another target")
		else:
			self.aisTurn = True
			self.update(self, None)
		
	def setUpdate(self, obs, arg):
		"""User has placed a Ship."""
		unplaced = len(self.WORDS)
		for s in self.ships:
			if(s.placed):
				unplaced -= 1
				
		self.shipsUnplaced = unplaced
		
		if(self.shipsUnplaced == 0):
			self.orientBtn.setEnabled(False)
			self.aiBtn.setEnabled(False)
			
			# save some line width
			params = (self, self.userGrid, self.targetGrid)
			self.ai = SmartAI(*params) if self.smartAI else DumbAI(*params)
			self.ai.placeShips()
			
			self.gameMode = self.MODE_FIRING
	
	def livingShips(self, ships):
		"""Count the number of ships still alive."""
		shipsAlive = len(ships)
		for s in ships:
			if(s.health == 0):
				shipsAlive -= 1
				
		return shipsAlive
	
	def fireUpdate(self, obs, arg):
		"""Someone has fired a missile."""
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
		
	def update(self, obs, arg):
		"""Some update has happened."""
		if(self.gameMode == self.MODE_SETUP):
			self.setUpdate(obs, arg)
			
		if(self.gameMode == self.MODE_FIRING):
			self.fireUpdate(obs, arg)
			
		if(self.gameMode == self.MODE_GAMEOVER):
			resetBtn = QtGui.QPushButton("Restart")
			resetBtn.clicked.connect(self.reset)
			self.scoreGrid.addWidget(resetBtn, 4, 1)
			
	def reset(self):
		"""Make a new game."""
		self.close()
		
		Battleship()
	
	def clickOrientBtn(self):
		"""Switch ship placement orientation."""
		self.orientVert = not self.orientVert
		self.orientBtn.setText("Vertical" if self.orientVert else "Horizontal")
		
	def switchAI(self):
		self.smartAI = not self.smartAI
		self.aiBtn.setText("AI: Less dumb" if self.smartAI else "AI: Dumb")
		
def main():
	app = QtGui.QApplication(sys.argv)
	bs = Battleship()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
