from AI import AI
from Action import Action


class MyAI( AI ):

	class __Tile():
		covered = True
		flag = False
		number = -2
		effLab = 0
		uncovLab = 0

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self._rowDimension = rowDimension
		self._colDimension = colDimension
		self._totalMines = totalMines
		self._moveCount = 1
		self._flagCount = 0
		self._agentX = startX
		self._agentY = startY
		self._board = [[self.__Tile() for i in range(self._rowDimension)] for j in range(self._colDimension)]
		self._unCovQue = []
		self._flagQue = []
		self._frontier = []
		self._unCovFront = []
		self._unCovGrouped = []
		self._trackDict = {}
		self._listCounter = 0

	def getSurroundings(self, xVal, yVal):
		retList = []
		for x in range(-1,2):
			for y in range(-1,2):
				tempX = xVal + x
				tempY = yVal + y
				if((tempX != xVal or tempY != yVal) and tempX >= 0 and tempX < self._colDimension and tempY >= 0 and tempY < self._rowDimension):
					retList.append([tempX,tempY])
		return retList

	def findNum(self, valList):
		min = 50
		for x in [-1,1]:
			tempX = valList[0] + x
			if(tempX >= 0 and tempX < self._colDimension and not self._board[tempX][valList[1]].covered):
				effVal = self._board[tempX][valList[1]].effLab
				if(effVal < min):
					min = effVal
		for y in [-1,1]:
			tempY = valList[1] + y
			if(tempY >= 0 and tempY < self._rowDimension and not self._board[valList[0]][tempY].covered):
				effVal = self._board[valList[0]][tempY].effLab
				if(effVal < min):
					min = effVal    
		return min

	def recurseTrial(self, tryList, ind, mineList, noMineList):
		if(ind >= len(tryList)):
			for val in mineList:
				self._trackDict[tuple(val)] += 1
			self._listCounter += 1
			return

		surround = self.getSurroundings(tryList[ind][0],tryList[ind][1])
		mineCounter = 0
		noMineCounter = 0
		numCovSurround = 0
		canBe1 = True
		canBe0 = True
		for val in surround:
			if(not self._board[val[0]][val[1]].covered):
				tempSurround = self.getSurroundings(val[0], val[1])
				for x in tempSurround:
					if x in mineList:
						mineCounter += 1
					elif(not x in noMineList and self._board[x[0]][x[1]].covered):
						numCovSurround += 1
				if(self._board[val[0]][val[1]].effLab - mineCounter == numCovSurround):
					canBe0 = False
				if(self._board[val[0]][val[1]].effLab - mineCounter == 0):
					canBe1 = False
				mineCounter = 0
				numCovSurround = 0
		if(canBe0):
			tempNoMineList = noMineList.copy()
			tempNoMineList.append([tryList[ind][0],tryList[ind][1]])
			self.recurseTrial(tryList,ind+1,mineList,tempNoMineList)
		if(canBe1):
			tempMineList = mineList.copy()
			tempMineList.append([tryList[ind][0],tryList[ind][1]])
			if(len(tempMineList) <= self._totalMines - self._flagCount):
				self.recurseTrial(tryList,ind+1,tempMineList,noMineList)

	def trialError(self, tryList):
		self._trackDict = {}
		for key in tryList:
			self._trackDict[tuple(key)] = 0
		self._listCounter = 0
		self.recurseTrial(tryList,0,[],[])
		print(self._trackDict)
		for key in self._trackDict.keys():
			if(self._trackDict[key] == self._listCounter):
				self._flagQue.append(list(key))
		self._unCovQue.append(list(sorted(self._trackDict.items(), key=lambda x:x[1])[0][0]))
            
	def separateFront(self):
		keepTrackList = []
		tempList = []
		tempInd = -1
		isInSurrounding = False
		while(self._unCovFront):
			uncov = self._unCovFront.pop(0)
			frontX = uncov[0]
			frontY = uncov[1]
			if(self._board[frontX][frontY].covered and not self._board[frontX][frontY].flag and not uncov in tempList and not uncov in keepTrackList):
				if(not tempList or tempList[tempInd] in self.getSurroundings(frontX, frontY)):
					tempList.append(uncov)
					tempList.sort(key=lambda x: (x[0],x[1]))
					keepTrackList.append(uncov)
					tempInd += 1
				else:
					if(tempList):
						self._unCovGrouped.append(tempList)
						return
						tempList = []
					tempInd = -1
		if(tempList):
			self._unCovGrouped.append(tempList)

	#MAIN ALGORITHM
	def getAction(self, number: int) -> "Action Object":
		if(self._moveCount == self._rowDimension * self._colDimension - self._totalMines):
			return Action(AI.Action.LEAVE, self._agentX, self._agentY)
        
		if(number != -1):
			self._board[self._agentX][self._agentY].covered = False
			self._board[self._agentX][self._agentY].number = number     

		if(self._moveCount >= self._rowDimension * self._colDimension * 0.6):
			for i in range(self._colDimension):
				for j in range(self._rowDimension):
					if(self._board[i][j].covered and not self._board[i][j].flag):
						self._unCovFront.append([i,j])

		numFlag = 0
		coveredList = []
		for val in self.getSurroundings(self._agentX,self._agentY):
			if(self._board[val[0]][val[1]].flag):
				numFlag+=1
			elif(self._board[val[0]][val[1]].covered):
				coveredList.append([val[0],val[1]])
				if(self._board[self._agentX][self._agentY].number == 0):
					self._unCovQue.append([val[0],val[1]])
			elif(self._board[val[0]][val[1]].number > 0):
				self._frontier.append([val[0],val[1]])

		fLab = self._board[self._agentX][self._agentY].number - numFlag
		self._board[self._agentX][self._agentY].effLab = fLab
		if(fLab == 0):
			self._unCovQue.extend(coveredList)
		elif(fLab == len(coveredList)):
			self._flagQue.extend(coveredList)
		elif(fLab > 0):
			self._unCovFront.extend(coveredList)

		while(self._frontier):
			newCover = []
			uncov = self._frontier.pop(0)
			frontX = uncov[0]
			frontY = uncov[1]
			frontFlag = 0

			for val in self.getSurroundings(frontX,frontY):
				if(self._board[val[0]][val[1]].flag):
					frontFlag += 1
				elif(self._board[val[0]][val[1]].covered):
					newCover.append([val[0],val[1]])
			fLab = self._board[frontX][frontY].number - frontFlag
			self._board[frontX][frontY].effLab = fLab
			if(fLab == 0):
				self._unCovQue.extend(newCover)
			elif(fLab == len(newCover)):
				self._flagQue.extend(newCover)
			elif(fLab > 0):
				self._unCovFront.extend(newCover)
        
		while(self._unCovQue):
			uncov = self._unCovQue.pop(0)
			self._agentX = uncov[0]
			self._agentY = uncov[1]
			if(self._board[self._agentX][self._agentY].covered):
				self._moveCount += 1
				for val in self.getSurroundings(self._agentX,self._agentY):
					if(self._board[val[0]][val[1]].covered):
						self._board[val[0]][val[1]].uncovLab += 1
				return Action(AI.Action.UNCOVER, self._agentX, self._agentY)

		while(self._flagQue):
			uncov = self._flagQue.pop(0)
			self._agentX = uncov[0]
			self._agentY = uncov[1]
			if(not self._board[self._agentX][self._agentY].flag and self._board[self._agentX][self._agentY].covered):
				self._board[self._agentX][self._agentY].flag = True
				for val in self.getSurroundings(self._agentX,self._agentY):
					self._frontier.append([val[0],val[1]])
				self._flagCount += 1
				#return self.getAction(number)
				return Action(AI.Action.FLAG, self._agentX, self._agentY)

		if(self._unCovFront):
			self.separateFront()    
		testList = []
		groupIter = 0
		indIter = 0
		groupLen = len(self._unCovGrouped)

		
		if(self._unCovGrouped):
			self.trialError(self._unCovGrouped.pop(0))
		
		while(self._unCovQue):
			uncov = self._unCovQue.pop(0)
			self._agentX = uncov[0]
			self._agentY = uncov[1]
			if(self._board[self._agentX][self._agentY].covered):
				self._moveCount += 1
				for val in self.getSurroundings(self._agentX,self._agentY):
					if(self._board[val[0]][val[1]].covered):
						self._board[val[0]][val[1]].uncovLab += 1   
				return Action(AI.Action.UNCOVER, self._agentX, self._agentY)

		while(self._flagQue):
			uncov = self._flagQue.pop(0)
			self._agentX = uncov[0]
			self._agentY = uncov[1]
			if(not self._board[self._agentX][self._agentY].flag and self._board[self._agentX][self._agentY].covered):
				self._board[self._agentX][self._agentY].flag = True
				for val in self.getSurroundings(self._agentX,self._agentY):
					self._frontier.append([val[0],val[1]])
				self._flagCount += 1
				#return self.getAction(number)
				return Action(AI.Action.FLAG, self._agentX, self._agentY)

		return Action(AI.Action.LEAVE, self._agentX, self._agentY)
