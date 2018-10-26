import wx
import os
import random
import copy

VERSION = 'v1.0.1'

class Frame(wx.Frame):
	# 定义Frame类
	def __init__(self, title):
		super(Frame, self).__init__(None, -1, title,\
		 style = wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)

		# 各数字方块的颜色，RGB格式
		self.colors = {0: (204, 192, 179), 2: (238, 228, 218), 4: (237, 224, 200),
                8: (242, 177, 121), 16: (245, 149, 99), 32: (246, 124, 95),
                64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 207, 114),
                512: (237, 207, 114), 1024: (237, 207, 114), 2048: (237, 207, 114),
                4096: (237, 207, 114), 8192: (237, 207, 114), 16384: (237, 207, 114)}
		
		self.setIcon() # 设置小图标
		self.initGame() # 初始化

		self.backButton = wx.Button(self, -1, 'BACK', pos = (250, 40), size = (80, 50),style = wx.BORDER_NONE)
		self.backButton.SetBackgroundColour((187,173,160))
		self.backButton.SetForegroundColour((238, 228, 218))
		self.Bind(wx.EVT_BUTTON, self.backMove, self.backButton)
		self.backButton.SetDefault()

		self.initBuffer()
		self.Bind(wx.EVT_SIZE, self.onSize) # use wx.BufferedPaintDC
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.SetClientSize((505,720))
		self.SetFocus()
		self.Center()
		self.Show()

	def onPaint(self, event):
		dc = wx.BufferedPaintDC(self, self.buffer)

	def onClose(self, event):
		self.saveScore()
		self.Destroy()

	def setIcon(self):
		# 设置程序的左上角小图标
		icon = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)

	def loadScore(self):
		# 加载最高分数
		if os.path.exists('bestscore.ini'):
			ff = open('bestscore.ini')
			self.bestScore = int(ff.read())
			ff.close()

	def saveScore(self):
		# 保存最高分数到"bestscore.ini"
		ff = open('bestscore.ini', 'w')
		ff.write(str(self.bestScore))
		ff.close()

	def initGame(self):
		# 初始化游戏

		# 字体
		self.bgFont = wx.Font(50, wx.SWISS, wx.NORMAL, wx.BOLD, faceName = u'Roboto')
		self.scFont = wx.Font(36, wx.SWISS, wx.NORMAL, wx.BOLD, faceName = u'Roboto')
		self.smFont = wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, faceName = u'Roboto')

		# 分数
		self.curScore = 0
		self.bestScore = 0
		self.loadScore()

		# 棋盘
		self.data = [[0, 0, 0, 0],
					 [0, 0, 0, 0],
					 [0, 0, 0, 0],
					 [0, 0, 0, 0]]

		# 初始化随机生成两个2或4的方块
		count = 0
		while count < 2:
			row = random.randint(0, len(self.data)-1) # 行
			col = random.randint(0, len(self.data[0])-1) # 列
			if self.data[row][col] != 0: # 若随机到同一坐标，再随机一次
				continue
			self.data[row][col] = 2 if random.randint(0, 1) else 4
			count += 1

		# 历史步骤
		self.historyData = []
		self.historyData.append(copy.deepcopy(self.data)) # 深复制

	def initBuffer(self):
		w, h = self.GetClientSize()
		self.buffer = wx.Bitmap(w, h)

	def onSize(self, event):
		self.initBuffer()
		self.drawAll()

	def putTile(self):
		# 随机在空的区域生成2或4的方块
		available = []
		for row in range(len(self.data)):
			for col in range(len(self.data[0])):
				if self.data[row][col]==0: available.append((row,col))
			if available:
				row,col = available[random.randint(0,len(available)-1)]
				self.data[row][col] = 2 if random.randint(0,1) else 4
				return True
			return False

	def update(self, vlist, direct):
		# 合并相同方块
		score = 0
		if direct: # 向上或向左移动
			i = 1
			while i < len(vlist):
				if vlist[i-1] == vlist[i]: # 如果两个方块相同
					del vlist[i] # 删除一个方块
					vlist[i-1] *= 2 # 另一个方块的值乘以2
					score += vlist[i-1] # 增加方块对应数字的分数
					i += 1
				i += 1
		else: # 向下或向右移动
			i = len(vlist)-1
			while i > 0:
				if vlist[i-1] == vlist[i]: # 如果两个方块相同
					del vlist[i] # 删除一个方块
					vlist[i-1] *= 2 # 另一个方块的值乘以2
					score += vlist[i-1] # 增加方块对应数字的分数
					i -= 1
				i -= 1
		return score

	def slideUpDown(self, up):
		# 当用户按上或下方向时，对棋盘的列进行处理
		score = 0 # 这一操作所得的分数
		numRows = len(self.data)  # 获取行数
		numCols = len(self.data[0]) # 获取列数
		oldData = copy.deepcopy(self.data) # 备份数据到oldData

		for col in range(numCols):
			cvl = [self.data[row][col] for row in range(numRows) if self.data[row][col] != 0]

			if len(cvl) >= 2:
				score += self.update(cvl, up)
			for i in range(numRows-len(cvl)):
				if up:
					cvl.append(0)
				else:
					cvl.insert(0, 0)
			for row in range(numRows):
				self.data[row][col] = cvl[row]

		return oldData != self.data, score

	def slideLeftRight(self, left):
		# 当用户按左或右方向时，对棋盘的列进行处理
		score = 0 # 这一操作所得的分数
		numRows = len(self.data) # 获取行数
		numCols = len(self.data[0]) # 获取列数
		oldData = copy.deepcopy(self.data) # 备份数据到oldData

		for row in range(numRows):
			rvl = [self.data[row][col] for col in range(numCols) if self.data[row][col]!=0]

			if len(rvl) >= 2:
				score += self.update(rvl,left)
			for i in range(numCols-len(rvl)):
				if left: rvl.append(0)
				else: rvl.insert(0,0)
			for col in range(numCols): self.data[row][col] = rvl[col]

		return oldData!=self.data,score

	def isGameOver(self):
		# 检测游戏是否结束
		# 复制棋盘
		copyData = copy.deepcopy(self.data)
		flag = False # 标志位
		if not self.slideUpDown(True)[0] and not self.slideUpDown(False)[0] and \
				not self.slideLeftRight(True)[0] and not self.slideLeftRight(False)[0]:
			flag = True
		if not flag:
			self.data = copyData
		return flag

	def doMove(self,move,score):
		if move:
			self.putTile()
			self.historyData.append(copy.deepcopy(self.data))
			print(self.historyData)
			self.drawChange(score)
			if self.isGameOver():
				if wx.MessageBox(u'游戏结束，是否重新开始？',u'Game Over',
						wx.YES_NO|wx.ICON_INFORMATION) == wx.YES:
					bestScore = self.bestScore
					self.initGame()
					self.bestScore = bestScore
					self.drawAll()


	def backMove(self, event):
		# 撤回操作
		historyLen = len(self.historyData)
		if historyLen > 1:
			self.historyData.pop() # 删除当前这一步的历史数据
			self.data = copy.deepcopy(self.historyData[-1]) # 将上一步复制到棋盘
			self.drawChange(0) # 绘制变化
			self.SetFocus() # 聚焦棋盘
		else:
			wx.MessageBox('已经是第一步了，不能再撤回了')

	def onKeyDown(self, event): # 按键处理
		keyCode = event.GetKeyCode() # 获取按键码
		if keyCode == wx.WXK_UP: # “↑”的按键码，下同
			self.doMove(*self.slideUpDown(True))
		elif keyCode == wx.WXK_DOWN:
			self.doMove(*self.slideUpDown(False))
		elif keyCode == wx.WXK_LEFT:
			self.doMove(*self.slideLeftRight(True))
		elif keyCode == wx.WXK_RIGHT:
			self.doMove(*self.slideLeftRight(False))        

	def drawBg(self,dc): # 绘制背景
		dc.SetBackground(wx.Brush((250, 248, 239)))
		dc.Clear()
		dc.SetBrush(wx.Brush((187, 173, 160)))
		dc.SetPen(wx.Pen((187, 173, 160)))
		dc.DrawRoundedRectangle(15, 150, 475, 475, 5)

	def drawLogo(self,dc): # 绘制Logo
		dc.SetFont(self.bgFont)
		dc.SetTextForeground((119, 110, 101))
		dc.DrawText(u"2048", 15, 26)

	def drawLabel(self,dc): # 绘制文本
		dc.SetFont(self.smFont)
		dc.SetTextForeground((119, 110, 101))
		dc.DrawText(u"合并相同的数字，得到2048吧!", 15, 114)
		dc.DrawText(u"用上下左右按键来移动方块. \
				\n当两个相同数字的方块碰到一起时，会合成一个!", 15, 639)

	def drawScore(self,dc): # 绘制分数
		dc.SetFont(self.smFont)
		scoreLabelSize = dc.GetTextExtent(u"SCORE")
		bestLabelSize = dc.GetTextExtent(u"BEST")
		curScoreBoardMinW = 15*2+scoreLabelSize[0]
		bestScoreBoardMinW = 15*2+bestLabelSize[0]
		curScoreSize = dc.GetTextExtent(str(self.curScore))
		bestScoreSize = dc.GetTextExtent(str(self.bestScore))
		curScoreBoardNedW = 10+curScoreSize[0]
		bestScoreBoardNedW = 10+bestScoreSize[0]
		curScoreBoardW = max(curScoreBoardMinW,curScoreBoardNedW)
		bestScoreBoardW = max(bestScoreBoardMinW,bestScoreBoardNedW)
		dc.SetBrush(wx.Brush((187,173,160)))
		dc.SetPen(wx.Pen((187,173,160)))
		dc.DrawRoundedRectangle(505-15-bestScoreBoardW,40,bestScoreBoardW,50,3)
		dc.DrawRoundedRectangle(505-15-bestScoreBoardW-5-curScoreBoardW,40,curScoreBoardW,50,3)
		dc.SetTextForeground((238,228,218))
		dc.DrawText(u"BEST",505-15-bestScoreBoardW+(bestScoreBoardW-bestLabelSize[0])/2,48)
		dc.DrawText(u"SCORE",505-15-bestScoreBoardW-5-curScoreBoardW+(curScoreBoardW-scoreLabelSize[0])/2,48)
		dc.SetTextForeground((255,255,255))
		dc.DrawText(str(self.bestScore),505-15-bestScoreBoardW+(bestScoreBoardW-bestScoreSize[0])/2,68)
		dc.DrawText(str(self.curScore),505-15-bestScoreBoardW-5-curScoreBoardW+(curScoreBoardW-curScoreSize[0])/2,68)

	def drawButton(self, dc):
		# 绘制按键
		dc.SetFont(self.smFont)


	def drawTiles(self,dc):
		dc.SetFont(self.scFont)
		for row in range(4):
			for col in range(4):
				value = self.data[row][col]
				color = self.colors[value]
				if value == 2 or value == 4:
					dc.SetTextForeground((119,110,101))
				else:
					dc.SetTextForeground((255,255,255))
				dc.SetBrush(wx.Brush(color))
				dc.SetPen(wx.Pen(color))
				dc.DrawRoundedRectangle(30+col*115,165+row*115,100,100,2)
				size = dc.GetTextExtent(str(value))
				while size[0] > (100-15*2):
					self.scFont = wx.Font(self.scFont.GetPointSize()*4/5, wx.SWISS,wx.NORMAL,wx.BOLD, faceName=u"Roboto")
					dc.SetFont(self.scFont)
					size = dc.GetTextExtent(str(value))
				if value!=0: dc.DrawText(str(value), 30+col*115+(100-size[0])/2, 165+row*115+(100-size[1])/2)

	def drawAll(self):
		# 把界面逐次画出来
		dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		self.drawBg(dc)
		self.drawLogo(dc)
		self.drawLabel(dc)
		self.drawScore(dc)
		self.drawTiles(dc)
		pass

	def drawChange(self, score):
		# 当用户有操作后，把改变的地方重新绘制
		dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
		if score:
			self.curScore += score
			if self.curScore > self.bestScore:
				self.bestScore = self.curScore
			self.drawScore(dc)
		self.drawTiles(dc)	

if __name__ == "__main__":
	app = wx.App()
	Frame(u'2048 '+ VERSION)
	app.MainLoop()

