from scene import *
from random import shuffle
from time import time
from PIL import Image
from math import modf
from datetime import date
import shelve

imgHidden = Image.open('pzl:Gray3')
imgHidden.size = (64, 64)
l = imgHidden.load()
for x in list(range(0, 4)) + list(range(60, 64)):
	for y in range(64):
		l[x, y] = (119, 119, 119, 255)


imgShowing = imgHidden.copy()
l = imgShowing.load()
for x in range(4, 60):
	for y in range(4, 60):
		l[x, y] = (216, 216, 216, 255)
		
imgRed = imgHidden.copy()
l = imgRed.load()
for x in range(4, 60):
	for y in range(4, 60):
		l[x, y] = (255, 0, 0, 255)
		
		
imgHidden = load_pil_image(imgHidden)
imgShowing = load_pil_image(imgShowing)
imgRed = load_pil_image(imgRed)

f = 'Arial Rounded MT Bold'


class Main(Scene):
	def setup(self):
		self.state = 'Menu'
		self.timing = False
		self.swipeDistance = 25
		self.iw = min(self.size.w, self.size.h) * 0.25
		self.showingHighscores = 'Very Easy'
		self.rowHeight = 60  # for highscore screen
		self.highscoreScroll = 0
		self.timeDigits = 3
		self.width = 0
		self.height = 0
		self.mines = 0
		self.minesPlaced = False
		self.colours = ['#ffffff', '#0000ff', '#00dd00', '#ff0000', '#ff00ff', '#884400', '#00dddd', '#000000', '#888888']
		file = shelve.open('Minesweeper')
		if 'Highscores' in file.keys():
			self.highscores = file['Highscores']
		else:
			self.highscores = {'Very Easy': [], 'Easy': [], 'Medium': [], 'Hard': [], 'Expert': []}
			file['Highscores'] = self.highscores
		file.close()
		self.did_change_size()
		
		self.tryLoadingGame()
		
	def pause(self):
		self.trySavingGame()
		
	def stop(self):
		self.trySavingGame()
	
	def draw(self):
		if self.state == 'Menu':
			self.drawMenuScreen()
		elif self.state == 'Custom':
			self.drawCustomScreen()
		elif self.state == 'Highscores':
			self.drawHighscoresScreen()
		elif self.state.endswith('Entry'):
			self.drawEntryScreen()
		else:
			self.drawGameScreen()
		self.update()
		
	def drawMenuScreen(self):
		w = self.size.w
		h = self.size.h
		
		if self.orientation != PORTRAIT:
			background('#000000')
			tint('#ffffff')
			text('Please change the orientation.', f, 40 if self.orientation == LANDSCAPE else 25, w * 0.5, h * 0.5)
			return
			
		text('Minesweeper', f, 55, w * 0.5, h * 0.93)
		
		text('Very Easy', f, 40, w * 0.5, h * 0.75)
		text('Easy', f, 40, w * 0.5, h * 0.65)
		text('Medium', f, 40, w * 0.5, h * 0.55)
		text('Hard', f, 40, w * 0.5, h * 0.45)
		text('Expert', f, 40, w * 0.5, h * 0.35)
		text('Custom', f, 40, w * 0.5, h * 0.25)
		
		iw = self.iw
		image('iow:stats_bars_256', 0, 0, iw, iw)
		image('iow:help_circled_256', w - iw, 0, iw, iw)
		
	def drawCustomScreen(self):
		w = self.size.w
		h = self.size.h
		text('Custom', f, 70, w * 0.5, h * 0.93)
		
		text('Width: ' + str(self.width), f, 65, 0, h * 0.7, alignment=6)
		text('Height: ' + str(self.height), f, 65, 0, h * 0.5, alignment=6)
		text('Mines: ' + str(self.mines), f, 65, 0, h * 0.3, alignment=6)
		
		text('Back', f, 50, w * 0.17, h * 0.05)
		text('Play', f, 50, w * 0.85, h * 0.05)
		
	def drawHighscoresScreen(self):
		w = self.size.w
		h = self.size.h
		
		row = 0
		for i in range(int(h * 0.915 + self.highscoreScroll - self.rowHeight), -self.rowHeight,  -self.rowHeight):
			
			if row == len(self.highscores[self.showingHighscores]):
				break
				
			t, s = render_text(str(row + 1) + '.', f, 40)
			image(t, 5, i, s[0] * (self.rowHeight / s[1]), self.rowHeight)
			tw = s[0] * (self.rowHeight / s[1])
			
			t, s = render_text(self.highscores[self.showingHighscores][row][1], f, 40)
			image(t, w - 5 - (s[0] * ((self.rowHeight * 0.45) / s[1])), i + self.rowHeight * 0.1, s[0] * ((self.rowHeight * 0.45) / s[1]), self.rowHeight * 0.45)
			
			t, s = render_text(str(self.getT(t=self.highscores[self.showingHighscores][row][0])), f, 40)
			image(t, w - 5 - (s[0] * ((self.rowHeight * 0.45) / s[1])), i + self.rowHeight * 0.5, s[0] * ((self.rowHeight * 0.45) / s[1]), self.rowHeight * 0.45)
			
			rect(0, i, w, 2.5)
			row += 1
	
		fill(0, 0, 0)
		rect(0, h * 0.915, w, h * 0.085)
				
		text(self.showingHighscores, f, 45, w * .01, h * 1.005, alignment=3)
		
		tint(1, 0, 0)
		text('Menu', f, 40, w, h * 0.915, alignment=7)
		
		fill(1, 1, 1)
		rect(0, h * 0.915, w, 4)
		
	def drawEntryScreen(self):
		w = self.size.w
		h = self.size.h
		v = self.state.split()[0]
		text(v, f, 100, w * 0.5, h * 0.92)
		
		if v == 'Width':
			text(str(self.width), f, 100, w * 0.5, h * 0.72)
		elif v == 'Height':
			text(str(self.height), f, 100, w * 0.5, h * 0.72)
		else:
			text(str(self.mines), f, 100, w * 0.5, h * 0.72)
			
		text('1', f, 80, w * 0.25, h * 0.5)
		text('2', f, 80, w * 0.5, h * 0.5)
		text('3', f, 80, w * 0.75, h * 0.5)
		
		text('4', f, 80, w * 0.25, h * 0.375)
		text('5', f, 80, w * 0.5, h * 0.375)
		text('6', f, 80, w * 0.75, h * 0.375)
		
		text('7', f, 80, w * 0.25, h * 0.25)
		text('8', f, 80, w * 0.5, h * 0.25)
		text('9', f, 80, w * 0.75, h * 0.25)
		
		image('typw:Check', w * 0.14, h * 0.125 - w * 0.1, w * 0.2, w * 0.2)
		text('0', f, 80, w * 0.5, h * 0.125)
		image('typw:Delete', w * 0.64, h * 0.125 - w * 0.1, w * 0.2, w * 0.2)
	
	def drawGameScreen(self):
		if not self.setup_finished:
			return
		w = self.size.w
		h = self.size.h
		if self.orientation != self.preferred:
			background('#000000')
			tint('#ffffff')
			text('Please change the orientation.', f, 40 if self.orientation == LANDSCAPE else 25, w * 0.5, h * 0.5)
		elif self.state in ['Won', 'Lost']:
			self.drawEndScreen()
		else:
			self.drawGame()
		
	def drawGame(self):
		w = self.size.w
		h = self.size.h
		tw = self.tileWidth
		background('#cccccc')
		
		rect(0, 0, w, (h * 0.9) if self.orientation == PORTRAIT else (h * 0.8))
		t = self.getT()
		
		# Draw the top menu bar (if the game isn't over)
		if self.state == 'Play':  # make sure the game isnt won or lost
			t = render_text(t, f, (30 if self.orientation == PORTRAIT else 40))
			t, s = t[0], t[1]
			image(t, ((w * 0.99) - s.w) if self.orientation == PORTRAIT else ((w * 0.99) - s.w), (h * 0.9) if self.orientation == PORTRAIT else (h * 0.79))
			
			tint('#ff0000')
			t = render_text(str(self.mines - self.flagged), f, (60 if self.orientation == PORTRAIT else 80))[0]
			image(t, (w * 0.02) if self.orientation == PORTRAIT else (w * 0.015), (h * 0.9) if self.orientation == PORTRAIT else (h * 0.78))
			
			t = render_text('Menu', f, (30 if self.orientation == PORTRAIT else 40))
			t, s = t[0], t[1]
			text('Menu', f, (30 if self.orientation == PORTRAIT else 40), w * 0.5, h, 2)
			tint('#ffffff')
		
		# Draw the board
		xo = (w - (tw * self.width)) / 2
		yo = min((h - (tw * self.height)) / 2, ((h * 0.9) if self.orientation == PORTRAIT else (h * 0.8)) - (tw * self.height))
		for x in range(self.width):
			for y in range(self.height):
				image(imgHidden if not self.showing[x][y] else imgRed if self.showing[x][y] == 'r' else imgShowing, x * tw + xo, y * tw + yo, tw, tw)
				if self.showing[x][y] in [True, 'r']:
					if self.board[x][y] > 8:
						image('Bomb', (x + 0.1) * tw + xo, (y + 0.1) * tw + yo, tw * 0.8, tw * 0.8)
					elif self.board[x][y] > 0:
						tint(self.colours[self.board[x][y]])
						text(str(self.board[x][y]), f, tw, (x + 0.5) * tw + xo, (y + 0.5) * tw + yo)
						tint('#ffffff')
				if self.showing[x][y] == 'f':
					image('plf:Item_FlagRed2', (x + 0.1) * tw + xo, (y + 0.1) * tw + yo, tw * 0.8, tw * 0.8)
				if self.showing[x][y] == 'w':
					image('Bomb', (x + 0.1) * tw + xo, (y + 0.1) * tw + yo, tw * 0.8, tw * 0.8)
					image('emj:Cross_Mark', (x + 0.05) * tw + xo, (y + 0.05) * tw + yo, tw * 0.9, tw * 0.9)
					
	def drawEndScreen(self):
		w = self.size.w
		h = self.size.h
	
		self.drawGame()
		
		t = self.getT(self.timerEnd)
		t = render_text(t, f, (30 if self.orientation == PORTRAIT else 40))
		t, s = t[0], t[1]
		image(t, ((w * 0.99) - s.w) if self.orientation == PORTRAIT else ((w * 0.99) - s.w), (h * 0.9) if self.orientation == PORTRAIT else (h * 0.79))
			
		text('You won!' if self.state == 'Won' else 'You lost.', f, 40 if self.orientation == PORTRAIT else 60, w * 0.5, h * (0.9 if self.orientation == LANDSCAPE else 0.97))
		
		tint('#ff0000')
		t = render_text('Menu', f, (30 if self.orientation == PORTRAIT else 40))[0]
		image(t, (w * 0.02) if self.orientation == PORTRAIT else (w * 0.015), (h * 0.9) if self.orientation == PORTRAIT else (h * 0.78))
		tint('#ffffff')
		
	def touch_began(self, touch):
		w = self.size.w
		h = self.size.h
		l = touch.location
		
		if self.state == 'Play':
			
			if self.orientation == self.preferred:
				if self.orientation == PORTRAIT:
					menuRect = Rect(w * 0.395, h * 0.95, w * 0.21, h * 0.05)
				else:
					menuRect = Rect(w * 0.4215, h * 0.875, w * 0.157, h * 0.125)
					
				if l in menuRect:
					self.tappedMenu = True
				
				tw = self.tileWidth
				xo = (w - (tw * self.width)) / 2
				yo = min((h - (tw * self.height)) / 2, ((h * 0.9) if self.orientation == PORTRAIT else (h * 0.8)) - (tw * self.height))
				x = (l.x - xo) / tw
				y = (l.y - yo) / tw
				
				if x < 0 or x > self.width or y < 0 or y > self.height:
					return
					
				self.x = int(x)
				self.y = int(y)
				
				self.l = l
				
		elif self.state == 'Highscores':
			self.y = l.y
				
	def touch_moved(self, touch):
		l = touch.location
		w = self.size.w
		h = self.size.h
		
		if self.state == 'Play':
			if self.x is not None and abs(l - self.l) > self.swipeDistance:
				try:
					if self.showing[self.x][self.y] == 'f':
						self.showing[self.x][self.y] = False
						self.flagged -= 1
						
					elif not self.showing[self.x][self.y]:
						self.showing[self.x][self.y] = 'f'
						self.flagged += 1
						
				except IndexError:
					return
					
				self.x = None
				
		elif self.state == 'Highscores':
			self.highscoreScroll += l.y - self.y
			self.highscoreScroll = max(0, self.highscoreScroll)
			self.highscoreScroll = min(max(0, self.rowHeight * len(self.highscores[self.showingHighscores]) - h * 0.915), self.highscoreScroll)
			self.y = l.y
		
	def touch_ended(self, touch):
		l = touch.location
		w = self.size.w
		h = self.size.h
		
		self.touchTime = time()
		
		if self.state == 'Play':
			self.x = None
		
			if self.orientation == self.preferred:
				if self.orientation == PORTRAIT:
					menuRect = Rect(w * 0.395, h * 0.95, w * 0.21, h * 0.05)
				else:
					menuRect = Rect(w * 0.4215, h * 0.875, w * 0.157, h * 0.125)
						
				if l in menuRect and self.tappedMenu:
					self.state = 'Menu'
					self.timing = False
					return
			
			if self.orientation == self.preferred and self.l:
				tw = self.tileWidth
				xo = (w - (tw * self.width)) / 2
				yo = min((h - (tw * self.height)) / 2, ((h * 0.9) if self.orientation == PORTRAIT else (h * 0.8)) - (tw * self.height))
				x = int((l.x - xo) / tw)
				y = int((l.y - yo) / tw)
				try:
					if abs(l - self.l) < self.swipeDistance:
						self.reveal(x, y)
					
				except IndexError:
					pass
					
			self.trySavingGame()  # save after every tap
			self.tappedMenu = False
		
		elif self.state == 'Menu':
			
			if l in Rect(w * 0.25, h * 0.72, w * 0.75, h * 0.05):
				self.setupGame(4, 4, 3)
				self.difficulty = 'Very Easy'
				self.state = 'Play'
				
			elif l in Rect(w * 0.38, h * 0.62, w * 0.25, h * 0.05):
				self.setupGame(8, 8, 10)
				self.difficulty = 'Easy'
				self.state = 'Play'
				
			elif l in Rect(w * 0.32, h * 0.52, w * 0.41, h * 0.05):
				self.setupGame(16, 16, 40)
				self.difficulty = 'Medium'
				self.state = 'Play'
			
			elif l in Rect(w * 0.38, h * 0.42, w * 0.25, h * 0.05):
				self.setupGame(16, 30, 99)
				self.difficulty = 'Hard'
				self.state = 'Play'
				
			elif l in Rect(w * 0.34, h * 0.32, w * 0.35, h * 0.05):
				self.setupGame(24, 30, 148)
				self.difficulty = 'Expert'
				self.state = 'Play'
			
			elif l in Rect(w * 0.32, h * 0.23, w * 0.39, h * 0.05):
				self.difficulty = None
				self.state = 'Custom'
				self.width = max(1, self.width)
				self.height = max(1, self.height)
				
			elif l in Rect(0, 0, self.iw, self.iw):
				for i in self.highscores.keys():
					self.highscores[i] = sorted(self.highscores[i], key=lambda x: x[0])
					
				self.state = 'Highscores'
				
		elif self.state in ['Won', 'Lost']:
			if self.orientation == PORTRAIT:
				menuRect = Rect(0, h * 0.9, w * 0.25, h * 0.05)
			else:
				menuRect = Rect(0, h * 0.78, w * 0.25, h * 0.05)
			if menuRect:
				self.state = 'Menu'
				
		elif self.state == 'Custom':
			
			if h * 0.66 < l.y < h * 0.74:
				self.state = 'Width Entry'
				
			if h * 0.46 < l.y < h * 0.54:
				self.state = 'Height Entry'
				
			if h * 0.26 < l.y < h * 0.34:
				self.state = 'Mines Entry'
				
			if l in Rect(w * 0.75, 0, h * 0.09, w * 0.25):
				self.setupGame(self.width, self.height, self.mines)
				self.state = 'Play'
				
			if l in Rect(w * 0, 0, h * 0.09, w * 0.25):
				self.state = 'Menu'
				
		elif self.state.endswith('Entry'):
			if self.state.startswith('Width'):
				x = self.width
			if self.state.startswith('Height'):
				x = self.height
			if self.state.startswith('Mines'):
				x = self.mines
			
			if l in Rect(w * 0.2, h * 0.45, w * 0.1, h * 0.1):
				x = x * 10 + 1
			if l in Rect(w * 0.45, h * 0.45, w * 0.1, h * 0.1):
				x = x * 10 + 2
			if l in Rect(w * 0.7, h * 0.45, w * 0.1, h * 0.1):
				x = x * 10 + 3
			if l in Rect(w * 0.2, h * 0.325, w * 0.1, h * 0.1):
				x = x * 10 + 4
			if l in Rect(w * 0.45, h * 0.325, w * 0.1, h * 0.1):
				x = x * 10 + 5
			if l in Rect(w * 0.7, h * 0.325, w * 0.1, h * 0.1):
				x = x * 10 + 6
			if l in Rect(w * 0.2, h * 0.2, w * 0.1, h * 0.1):
				x = x * 10 + 7
			if l in Rect(w * 0.45, h * 0.2, w * 0.1, h * 0.1):
				x = x * 10 + 8
			if l in Rect(w * 0.7, h * 0.2, w * 0.1, h * 0.1):
				x = x * 10 + 9
			if l in Rect(w * 0.2, h * 0.075, w * 0.1, h * 0.1):
				self.state = 'Custom'
				self.mines = min(self.mines, self.width * self.height)
				self.width = max(1, self.width)
				self.height = max(1, self.height)
			if l in Rect(w * 0.45, h * 0.075, w * 0.1, h * 0.1):
				x *= 10
			if l in Rect(w * 0.7, h * 0.075, w * 0.1, h * 0.1):
				x = int(x / 10)
				
			if self.state.startswith('Width'):
				if x <= 100:
					self.width = x
			if self.state.startswith('Height'):
				if x <= 100:
					self.height = x
			if self.state.startswith('Mines'):
				if x <= self.width * self.height:
					self.mines = x
				
		elif self.state == 'Highscores':
			
			if l in Rect(w - 105, h * 0.915, 105, h * 0.085):
				self.state = 'Menu'
				
			elif l in Rect(0, h * 0.915, 240, h * 0.085):
				a = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Expert']
				i = a.index(self.showingHighscores)
				self.highscoreScroll = 0
				self.showingHighscores = a[(i + 1) % len(a)]
		
	def setupGame(self, width, height, mines):
		self.width = width
		self.height = height
		self.mines = mines
		
		small = min(self.size.w, self.size.h)
		big = max(self.size.w, self.size.h)
		s = min(self.width, self.height)
		b = max(self.width, self.height)
		
		portrait = min(small / s, (big * 0.9) / b)
		landscape = min(big / b, (small * 0.8) / s)
		
		if portrait > landscape:
			self.preferred = PORTRAIT
			self.height = b
			self.width = s
		else:
			self.preferred = LANDSCAPE
			self.height = s
			self.width = b
			
		self.tileWidth = max(portrait, landscape)
		
		self.board = [[0 for j in range(self.height)] for i in range(self.width)]
		self.showing = [[False for j in range(self.height)] for i in range(self.width)]  # False = hidden, True = showing, 'f' = flagged, 'r' = red, 'w' = wrong (incorrectly flagged)
		
		self.revealed = 0
		self.flagged = 0
		self.lost = False
		self.minesPlaced = False
		
		self.needsReveal = []
		
		self.x = None
		self.y = None
		self.l = None
		
		self.tappedMenu = False
		
	def trySavingGame(self):
		if self.state != 'Play' or not self.minesPlaced:
			file = shelve.open('Minesweeper')
			file['IsGameSaved'] = False
			file.close()
			return
		try:
			file = shelve.open('Minesweeper')
			file['IsGameSaved'] = True
			file['Revealed'] = self.revealed
			file['Flagged'] = self.flagged
			file['Lost'] = self.lost
			file['MinesPlaced'] = self.minesPlaced
			file['Board'] = self.board
			file['Showing'] = self.showing
			file['Time'] = self.getT(num=True)
			file['Difficulty'] = self.difficulty
			file.close()
		except AttributeError:
			pass
		
	def tryLoadingGame(self):
		file = shelve.open('Minesweeper')
		dontLoad = False
		if not dontLoad and 'IsGameSaved' in file.keys() and file['IsGameSaved']:
			mines = 0
			for i in file['Board']:
				for j in i:
					if j > 8:
						mines += 1
			self.setupGame(len(file['Board']), len(file['Board'][0]), mines)
			self.revealed = file['Revealed']
			self.flagged = file['Flagged']
			self.lost = file['Lost']
			self.minesPlaced = file['MinesPlaced']
			self.board = file['Board']
			self.showing = file['Showing']
			try:
				self.timerStart = time() - file['Time']
			except:
				pass
			self.difficulty = file['Difficulty']
			self.timing = True
			self.state = 'Play'
		file.close()
			
	def clearSavedGame(self):
		file = shelve.open('Minesweeper')
		file['IsGameSaved'] = False
		file.close()
		
	def placeMines(self, x, y):
		w = self.width
		h = self.height
		m = self.mines
		
		points = [(i, j) for i in range(w) for j in range(h)]
		
		if len(points) - 9 >= m:
			for a in range(x - 1, x + 2):
				for b in range(y - 1, y + 2):
					if a < 0 or b < 0:
						continue
					try:
						points.remove((a, b))
					except ValueError:
						pass
						
		elif len(points) - 1 >= m:
			points.remove((x, y))
						
		shuffle(points)
						
		for i in range(m):
			x, y = points[i][0], points[i][1]
			self.board[x][y] = 9
			for a in range(x - 1, x + 2):
				for b in range(y - 1, y + 2):
					if a < 0 or b < 0:
						continue
					try:
						self.board[a][b] += 1
					except:
						pass
	
		self.minesPlaced = True
		
	def reveal(self, x, y):
		self.needsReveal.append((x, y))
		while len(self.needsReveal) >= 0:
			self._reveal(*self.needsReveal.pop())
		
	def _reveal(self, x, y):
		if self.showing[x][y]:
			s = 0
			
			for a in range(x - 1, x + 2):
				for b in range(y - 1, y + 2):
					if (a == x and b == y) or (a < 0 or b < 0):
						continue
					else:
						try:
							if self.showing[a][b] == 'f':
								s += 1
						except IndexError:
							pass
							
			if s == self.board[x][y]:
				for a in range(x - 1, x + 2):
					for b in range(y - 1, y + 2):
						if (a == x and b == y) or (a < 0 or b < 0):
							continue
						try:
							if not self.showing[a][b]:
								self.needsReveal.append((a, b))
						except IndexError:
							pass
			
			return
			
		elif self.showing[x][y] == 'f':
			self.showing[x][y] = False
			self.flagged -= 1
			return
			
		else:
					
			self.showing[x][y] = True
			self.revealed += 1
			if self.revealed == self.width * self.height - self.mines:
				self.timerEnd = self.touchTime
				self.timing = False
				self.state = 'Won'
				self.addTime()
				self.showAll()
			
		if not self.minesPlaced:
			self.placeMines(x, y)
			self.timerStart = self.touchTime
			self.timing = True
			self.lastAutosave = 0
			
		if self.board[x][y] == 0:
			for a in range(x - 1, x + 2):
				for b in range(y - 1, y + 2):
					
					if (a == x and b == y) or (a < 0 or b < 0):
						continue
					try:
						if not self.showing[a][b]:
							self.needsReveal.append((a, b))
					except IndexError:
						pass
						
		elif self.board[x][y] > 8:
			self.timerEnd = self.touchTime
			self.timing = False
			self.state = 'Lost'
			self.showBombsAndIncorrectFlags()
			self.showing[x][y] = 'r'
			self.clearSavedGame()
			
	def showAll(self):
		for x in range(self.width):
			for y in range(self.height):
				self.showing[x][y] = True
				
	def showBombsAndIncorrectFlags(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.board[x][y] > 8:
					self.showing[x][y] = True
				if self.board[x][y] <= 8 and self.showing[x][y] == 'f':
					self.showing[x][y] = 'w'
		
	def getT(self, end=0, t=None, num=False):
		if end == 0:
			end = time()
		
		if t is not None:
			if t >= 60:
				minutes = int(t / 60)
				seconds = int(t % 60)
				centiseconds = modf(t)[0] * (10 ** self.timeDigits)
				return ('%s:%02d.%0' + str(self.timeDigits) + 'd') % (minutes, seconds, centiseconds)
			else:
				return ('%.0' + str(self.timeDigits) + 'f') % t

		if self.timing or self.minesPlaced:
			t = end - self.timerStart
			if num:
				return t
			if t >= 60:
				minutes = int(t / 60)
				seconds = int(t % 60)
				centiseconds = modf(t)[0] * (10 ** self.timeDigits)
				return ('%s:%02d.%0' + str(self.timeDigits) + 'd') % (minutes, seconds, centiseconds)
				
			else:
				return ('%.0' + str(self.timeDigits) + 'f') % t
		else:
			if num:
				return 0
			return '0.' + ('0' * self.timeDigits)
			
	def displayDate(self, date):
		weekday = False
		d = str(date.day)
		weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		ending = 'st' if d.endswith('1') else 'nd' if d.endswith('2') else 'rd' if (d.endswith('3') and d != '13') else 'th'
		return ((weekdays[date.weekday()] + ', ') if weekday else '') + months[date.month - 1] + ' ' + d + ending + ', ' + str(date.year)
		
	def addTime(self):
		if self.difficulty:
			self.highscores[self.difficulty].append((self.timerEnd - self.timerStart, self.displayDate(date.today())))
			if len(self.highscores[self.difficulty]) > 100:
				self.highscores[self.difficulty] = self.highscores[self.difficulty][:100]
			
			file = shelve.open('Minesweeper')
			file['Highscores'] = self.highscores
			file.close()
			
	def did_change_size(self):
		self.orientation = PORTRAIT
		if self.size.w > self.size.h:
			self.orientation = LANDSCAPE
		
run(Main())
