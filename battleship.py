import sys
from PyQt4 import QtGui

class Battleship(QtGui.QWidget):

	ROWS = 10
	COLUMNS = 10

	def __init__(self):
		super(Battleship, self).__init__()
		self.initUI()

	def initUI(self):
		grid = QtGui.QGridLayout()
		self.setLayout(grid)

		userGrid = QtGui.QTableWidget(self.ROWS, self.COLUMNS, self)
		enemyGrid = QtGui.QTableWidget(self.ROWS, self.COLUMNS, self)
		grid.addWidget(userGrid, 1, 1)
		grid.addWidget(enemyGrid, 1, 2)
		self.show()

def main():
	app = QtGui.QApplication(sys.argv)
	bs = Battleship()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()