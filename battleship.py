import sys
from PyQt4 import Qt

class Battleship(QWidget):

	def __init__(self):
		super(Battleship, self).__init__()

def main():
	app = QtGui.QApplication(sys.argv)
	bs = Battleship()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()