import random
import math
mapWidth = 0
mapHeight = 0
numPlates = 0
maps = {}
numMaps = 0
skewFactor = 0
skewFactor2 = 0
def InitHeightmaps():
    global mapWidth
    global mapHeight
    global maps
    maps = {}
    numMaps = 0
    i = 0
    while math.pow(2,i) <= mapWidth/8:
        maps[i] = {}
        numMaps = numMaps + 1
        factor = math.pow(2,i)
        for x in range( math.ceil(mapWidth/factor)):
            for y in range( math.ceil(mapWidth/factor)):
                q = (y * (math.ceil(mapWidth/factor)+1)) + x
                maps[i][q] = RandomFloat() * 2 - 1
                print(str(maps[i][q]))
        i = i+1
def Interpolate(a, b, x):
    ft = x * 3.1415927
    f = (1 - math.cos(ft)) * 0.5
    return  a*(1.0-f) + b*f
def RandomFloat():
    maxNum = random.randint(1,16384)
    return maxNum/16384.0
def GetHeightFromMap(i,x,y):
    global mapWidth
    global mapHeight
    global maps
    factor = math.pow(2,i)
    indexX = x/factor
    indexY = y/factor
    intX = math.floor(indexX)
    intY = math.floor(indexY)
    fracX = indexX - intX
    fracY = indexY - intY
    q = (intY * (math.ceil(mapWidth/factor)+1)) + intX
    q2 = ((intY+1) * (math.ceil(mapWidth/factor)+1)) + intX
    r1 = Interpolate(maps[i][q], maps[i][q+1], fracX)
    r2 = Interpolate(maps[i][q2], maps[i][q2+1], fracX)
    return Interpolate(r1, r2, fracY)
def GetHeight(x,y,n,f):
    global numMaps
    global maps
    height = 0
    for mapIndex, thisMap in maps.items():
        if mapIndex < numMaps-f:
            height = height + GetHeightFromMap(mapIndex,x,y)/(math.pow(n, numMaps-(mapIndex-1)))
        else: 
            if (x == 100 and y == 100):
                print("PARP") 
    return height
def GeneratePlotTypes():
    global mapWidth
    global mapHeight
    global numPlates
    global maps
    global numMaps
    global skewFactor
    global skewFactor2
    skewFactor = [ RandomFloat()*2+1, RandomFloat()+1, RandomFloat()+1,  RandomFloat()*6+5, RandomFloat()*3+3, RandomFloat()*2+2,  RandomFloat()*7, RandomFloat()*7, RandomFloat()*7]
    skewFactor2 = [ RandomFloat()*10+5, RandomFloat()*5+5, RandomFloat()*5+3, RandomFloat()*5+3, RandomFloat()*7, RandomFloat()*7, RandomFloat()*7, RandomFloat()*7]
    print("Generating Plates")
    numPlates = 30
    plates = 6
    if (plates == 4):
        plates = 1 + random.randint(1,3)
    if (plates == 1):
        numPlates = (numPlates * 2)/3
    elif (plates == 2):
        numPlates = numPlates
    else:
        numPlates = (numPlates * 4)/3
    print("Plates Option " + str(plates) + " " + str(numPlates))
    mapWidth = 52
    mapHeight = 32
    plates = {}
    for i in range(int(numPlates)):
        plates[i] = {}
        plates[i]["x"] = random.randint(1,mapWidth)
        plates[i]["y"] = random.randint(1,mapHeight)
        plates[i]["mass"] = random.randint(1,7) + 6
        plates[i]["size"] = 0
        plates[i]["terrainType"] = "?"
        plates[i]["neighbours"] = {}
        plates[i]["neighboursBorders"] = {}
        plates[i]["neighboursRelativeMotions"] = {}
        plates[i]["velocity"] = {}
        plates[i]["velocity"]["x"] = random.randint(1,21)-10
        plates[i]["velocity"]["y"] = random.randint(1,21)-10
    print("Calculating Plate Neighbours")
    neighbours = {}
    for i in range(int(numPlates)):
        neighbours[i] = {}
        for j in range(int(numPlates)):
            neighbours[i][j] = 0
        neighbours[i][int(numPlates)] = 0
        neighbours[i][int(numPlates)+1] = 0
        neighbours[i][int(numPlates)+2] = 0
        neighbours[i][int(numPlates)+3] = 0
    for x in range( mapWidth-1):
        for y in range( mapHeight-1):
            currentPlate = partOfPlate(x,y,plates)
            info = getPlateBoundaryInfo(x, y, plates)
            for infoIndex, thisPlateInfo in info.items():
                if (infoIndex != currentPlate):
                    neighbours[currentPlate][infoIndex] = neighbours[currentPlate][infoIndex]+thisPlateInfo      
            neighbours[currentPlate][int(numPlates)+3] = neighbours[currentPlate][int(numPlates)+3]+info[int(numPlates)+3]
            neighbours[currentPlate][int(numPlates)+2] = neighbours[currentPlate][int(numPlates)+2]+info[int(numPlates)+2]
            neighbours[currentPlate][int(numPlates)+1] = neighbours[currentPlate][int(numPlates)+1]+info[int(numPlates)+1]
            neighbours[currentPlate][int(numPlates)] = neighbours[currentPlate][int(numPlates)]+info[int(numPlates)]
    for plateIndex, thisPlate in plates.items():
        thisPlate["neighboursBorders"] = neighbours[plateIndex]
    print("Creating Base Heightmap")
    InitHeightmaps()
    print("Calculating Relative Plate Motions")
    for plateIndex, thisPlate in plates.items():
        motions = {}
        for plateIndex2, thatPlate in plates.items():
            motions[plateIndex2] = {}
            if (thisPlate["neighboursBorders"][plateIndex2] > 0):
                x = thatPlate["velocity"]["x"] - thisPlate["velocity"]["x"]
                y = thatPlate["velocity"]["y"] - thisPlate["velocity"]["y"]
                motions[plateIndex2]["x"] = x
                motions[plateIndex2]["y"] = y
                mag = math.sqrt(x*x+y*y)
                if (mag < 5):
                    motions[plateIndex2]["boundaryType"] = "Passive"
                else:
                    xNorm = x/mag
                    yNorm = y/mag
                    dirX = thatPlate["x"] - thisPlate["x"]
                    dirY = thatPlate["y"] - thisPlate["y"]
                    dirMag = math.sqrt(dirX*dirX+dirY*dirY)
                    dirXNorm = dirX/dirMag
                    dirYNorm = dirY/dirMag
                    dotProduct = xNorm*dirXNorm + yNorm*dirYNorm
                    if (dotProduct < -0.5):
                        motions[plateIndex2]["boundaryType"] = "Collision"
                    elif (dotProduct > 0.5):
                        motions[plateIndex2]["boundaryType"] = "Rift"
                    else:
                        motions[plateIndex2]["boundaryType"] = "Transform"
        thisPlate["neighboursRelativeMotions"] = motions
    print("Calculating Plate Size")
    for x in range( mapWidth-1):
        for y in range( mapHeight-1):
            currentPlate = partOfPlate(x, y, plates)
            plates[currentPlate]["size"] = plates[currentPlate]["size"] + 1 
    print("Calculating Plate Types")
    oceanAmount = 0
    oceanAmountD = 0
    oceanAmountNS = 0
    oceanAmountREG = 0
    landAmount = 0
    arcAmount = 0
    fractalAmount = 0
    spiffiness = 0
    islands = 1
    if (islands == 5):
        islands = 1 + random.randint(1,4)
    islandsModifier = 0
    if (islands == 1):
        islandsModifier = -10
    elif (islands == 2):
        islandsModifier = -0.05
    elif (islands == 3):
        islandsModifier = 0
    else:
        islandsModifier = 0.1
    print ("Islands Option" + str(islands))     
    land = 4
    if (land == 4):
        land = 1 + random.randint(1,3)
    landModifier = 0
    if (land == 1):
        landModifier = -0.2
    elif (land == 2):
        landModifier = 0
    else:
        landModifier = 0.2
    print ("Land Option" + str(land))
    continents = 4
    if (continents == 4):
        continents = 1 + random.randint(1,3)
    continents_modifier = 0
    if (continents == 1):
        continents_modifier = -0.5
    elif (continents == 2):
        continents_modifier = 0.0
    else:
        continents_modifier = 1.5
    for plateIndex, thisPlate in plates.items():
        if (thisPlate["neighboursBorders"][int(numPlates)] > 5 or thisPlate["neighboursBorders"][int(numPlates)+2] > 5):
            thisPlate["terrainType"] = "Deep Ocean"
            oceanAmount = oceanAmount + thisPlate["size"]
            oceanAmountD = oceanAmountD + thisPlate["size"]
        elif ((thisPlate["neighboursBorders"][int(numPlates)+1] > 20 or thisPlate["neighboursBorders"][int(numPlates)+3] > 20) and RandomFloat() > 0.375 + (landModifier/2)):
            thisPlate["terrainType"] = "Ocean"
            oceanAmount = oceanAmount + thisPlate["size"]
            oceanAmountNS = oceanAmountNS + thisPlate["size"]
        elif (thisPlate["size"]/(mapHeight*mapWidth) * RandomFloat() * numPlates > 0.5 + landModifier):
            thisPlate["terrainType"] = "Ocean"
            oceanAmount = oceanAmount + thisPlate["size"]
            oceanAmountREG = oceanAmountREG + thisPlate["size"]
        elif (thisPlate["size"]/(mapHeight*mapWidth) * RandomFloat() * numPlates < 0.2 + islandsModifier):
            thisPlate["terrainType"] = "Island Arcs"
            arcAmount = arcAmount + thisPlate["size"]
        else:
            thisPlate["terrainType"] = "Continental"
        print("terrain " + plates[plateIndex]['terrainType'])
        neighbouringContinentAmount = 0
        for neighbourIndex, thisNeighbour in thisPlate["neighboursBorders"].items():
            if (plates.get(neighbourIndex) != None and plates[neighbourIndex]["terrainType"] == "Continental"):
                neighbouringContinentAmount = neighbouringContinentAmount + thisNeighbour
        neighbouringContinentAmount = neighbouringContinentAmount / (mapWidth*mapHeight) * 100
        if thisPlate["terrainType"] == "Continental" and RandomFloat() - neighbouringContinentAmount < 0.1:
            thisPlate["terrainType"] = "Fractal"
            fractalAmount = fractalAmount + thisPlate["size"]
        else: 
            landAmount = landAmount + thisPlate["size"]
        if thisPlate["terrainType"] == "Ocean" and RandomFloat() - (neighbouringContinentAmount * continents_modifier) < 0.0:
            thisPlate["terrainType"] = "Continental"
            spiffiness = spiffiness + thisPlate["size"]
    print("Amount of ocean:       " + str((oceanAmount*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of deep ocean:  " + str((oceanAmountD*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of N/S ocean:   " + str((oceanAmountNS*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of random ocean:" + str((oceanAmountREG*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of land:        " + str((landAmount*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of island arc:  " + str((arcAmount*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Amount of fractal:     " + str((fractalAmount*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Ocean converted to land:" + str((spiffiness*100)/(oceanAmount+landAmount+arcAmount+fractalAmount))+ "%")
    print("Generating Terrain")
    plate_motion = 5
    if (plate_motion == 5):
        plate_motion = 1 + random.randint(1,4)
    plate_motionModifier = 0
    plate_motionMultiplier = 0
    if (plate_motion == 1):
        plate_motionModifier = -0.05
        plate_motionMultiplier = 0.66
    elif (plate_motion == 2):
        plate_motionModifier = 0
        plate_motionMultiplier = 1
    elif (plate_motion == 3):
        plate_motionModifier = 0.1
        plate_motionMultiplier = 1.66
    else:
        plate_motionModifier = 0.3
        plate_motionMultiplier = 3
    print ("Plate Motion Option" + str(plate_motion))
    continents = 4
    if (continents == 4):
        continents = 1 + random.randint(1,3)
    continents_modifier1 = 0
    continents_modifier2 = 0
    if (continents == 1):
        continents_modifier1 = -0.2
        continents_modifier2 = -0.1
    elif (continents == 2):
        continents_modifier1 = 0.05
        continents_modifier2 = 0.05
    else:
        continents_modifier1 = 0.3
        continents_modifier2 = 0.1
    print ("Continents Option" + str(continents))     
    sea_level = 4
    if (sea_level == 4):
        sea_level = 1 + random.randint(1,3)
    sea_levelModifier = 0
    if (sea_level == 1):
        sea_levelModifier = -0.1
    elif (sea_level == 2):
        sea_levelModifier = 0
    else:
        sea_levelModifier = 0.1
    print ("Sea Level Option" + str(sea_level))
    arr = []
    for x in range( mapWidth-1):
        arr.append([])
        for y in range( mapHeight-1):
            i = y * 53 + x
            currentPlate = partOfPlate(x, y, plates)
            neighbour = adjacentToPlate(x,y,plates)
            value = 0
            if (plates[currentPlate]["terrainType"] == "Ocean"):
                value = GetHeight(x,y,1.5,0)-0.5+islandsModifier
            elif (plates[currentPlate]["terrainType"] == "Deep Ocean"):
                value = -1
            elif (plates[currentPlate]["terrainType"] == "Continental"):
                value = GetHeight(x,y,1.9+continents_modifier1,0)+0.1+continents_modifier2
                if (value < 0 + sea_levelModifier and numAdjacentLandTiles(x,y,1.9+continents_modifier1,0,sea_levelModifier,0.1+continents_modifier2) >= 4):
                    value = 0.11  
            elif (plates[currentPlate]["terrainType"] == "Island Arcs"):
                value = GetHeight(x,y,1.4,2)-0.2
                if (value > 0 + sea_levelModifier and numAdjacentLandTiles(x,y,1.4,2,sea_levelModifier,-0.2) <= 1):
                    value = -0.5  
            elif (plates[currentPlate]["terrainType"] == "Fractal"): 
                value = GetHeight(x,y,2.0,2)-0.05-sea_levelModifier/2
                if (value < 0 + sea_levelModifier and numAdjacentLandTiles(x,y,1.5,1,sea_levelModifier,0.05) >= 3):
                    value = 0.1  
            else:
                value = 1
            if (neighbour > 0):
                g = {}
                g = plates[currentPlate]
                if(bool(g.get(neighbour)) != False):
                    boundaryType = plates[currentPlate]["neighboursRelativeMotions"][neighbour]["boundaryType"]
                    if (boundaryType == "Collision"):
                        terrainType = plates[currentPlate]["terrainType"]
                        terrainTypeN = plates[neighbour]["terrainType"]
                        if (terrainType == "Continental"):
                            value = value + 0.05 + RandomFloat()/5.0 + plate_motionModifier
                        elif (terrainType == "Fractal"):
                            if (terrainTypeN == "Ocean" or terrainTypeN == "Island Arcs"):
                                value = value + RandomFloat()/5.0 + plate_motionModifier
                            else:
                                value = value + 0.05 + RandomFloat()/5.0 + plate_motionModifier
                        elif (terrainType == "Island Arcs"):
                            value = value + 0.15 + RandomFloat()/2.5 + plate_motionModifier
                        else:
                            if (terrainTypeN == "Continental"):
                                value =  RandomFloat()/2.5 - 0.05
                            else:
                                value = value + 0.1 + RandomFloat()/2.5
                        if (value < 0.1 + RandomFloat()/5.0 and RandomFloat() < 0.5):
                            value = value - 0.5
                    elif (boundaryType == "Transform"):
                        value = value - (0.05 - RandomFloat()/10.0) * plate_motionMultiplier
                    elif (boundaryType == "Rift"):
                        value = value - 0.05 - RandomFloat()/20.0 - plate_motionModifier/2
                        if (RandomFloat() > 0.97):
                            value = 0.5 
            if (value < 0 + sea_levelModifier):
                arr[x].append('~')
            elif (value < 0.05 + RandomFloat()/2.0):
                arr[x].append('"')
            elif (value < 0.2 + RandomFloat()/2.0):
                arr[x].append('n')
            else:
                arr[x].append('^')
    for i in arr:
        print()
        for o in i:
            print(o,end='')
def partOfPlate(x, y, plates):
    global skewFactor
    global skewFactor2
    global mapWidth
    global mapHeight
    if x < 0:
        return int(numPlates)
    elif y < 0:
        return int(numPlates)+1
    elif x >= mapWidth:
        return int(numPlates)+2
    elif y >= mapHeight:
        return int(numPlates)+3
    yShift = skewFactor[0]*math.sin(x/skewFactor[3]+skewFactor[6]) + skewFactor[1]*math.sin(x/skewFactor[4]+skewFactor[7]) + skewFactor[2]*math.sin(x/skewFactor[5]+skewFactor[8])
    xShift = skewFactor[0]*math.sin(y/skewFactor[4]+skewFactor[8]) + skewFactor[1]*math.sin(y/skewFactor[5]+skewFactor[6]) + skewFactor[2]*math.sin(y/skewFactor[3]+skewFactor[7])
    yFuddle = math.pow((0.5*math.sin(x/skewFactor2[0]+skewFactor2[4])+0.5*math.sin(x/skewFactor2[1]+skewFactor2[5])),2)*(math.sin(x*skewFactor2[2]+skewFactor2[6])+math.sin(x*skewFactor2[3]+skewFactor2[7]))
    xFuddle = math.pow((0.5*math.sin(y/skewFactor2[0]+skewFactor2[5])+0.5*math.sin(y/skewFactor2[1]+skewFactor2[6])),2)*(math.sin(y*skewFactor2[2]+skewFactor2[7])+math.sin(y*skewFactor2[3]+skewFactor2[4]))
    xAdj = x + xShift+xFuddle
    yAdj = y + yShift+yFuddle
    distanceToPlate = {}
    for plateIndex, thisPlate in plates.items():
        yMod = 1 + (((mapHeight/2.0) - yAdj) * ((mapHeight/2.0) - yAdj)) / (mapHeight*2.0)
        xMod = 1 + (((mapWidth/2.0) - xAdj) * ((mapWidth/2.0) - xAdj)) / (mapWidth*2.0)
        distanceToPlate[plateIndex] = ((xAdj-thisPlate["x"])*(xAdj-thisPlate["x"])*xMod+(yAdj-thisPlate["y"])*(yAdj-thisPlate["y"])*yMod)/thisPlate["mass"]
    nearestPlate = 10
    nearestPlateDist = 10000
    nearestPlateDist2 = 10000
    for distIndex, thisDiscance in distanceToPlate.items():
        if (thisDiscance < nearestPlateDist):
            nearestPlate = distIndex
            nearestPlateDist2 = nearestPlateDist
            nearestPlateDist = thisDiscance   
    return nearestPlate
def adjacentToPlate(x,y,plates):
    currentPlate = partOfPlate(x,y,plates)
    if (isAtPlateBoundary(x, y, plates,currentPlate)):
        info = getPlateBoundaryInfo(x, y, plates)
        biggest = 0
        biggestIndex = -1
        for infoIndex, thisInfo in info.items():
            if (int(infoIndex) != int(currentPlate) and thisInfo > biggest):
                biggest = thisInfo
                biggestIndex = infoIndex
        return biggestIndex
    else:
        return -1
def getPlateBoundaryInfo(x, y, plates):
    info = {}
    for plateIndex, thisPlate in plates.items():
        info[plateIndex] = 0
    info[int(numPlates)] = 0
    info[int(numPlates)+1] = 0
    info[int(numPlates)+2] = 0
    info[int(numPlates)+3] = 0
    index1 = partOfPlate(x-1+(y%2), y+1,plates)
    if (info[index1] != None):
        info[index1] = info[index1]+1
    index2 = partOfPlate(x+(y%2), y+1,plates)
    if (info[index2] != None):
        info[index2] = info[index2]+1
    index3 = partOfPlate(x-1, y,plates)
    if (info[index3] != None):
        info[index3] = info[index3]+1
    index4 = partOfPlate(x+1, y,plates)
    if (info[index4] != None):
        info[index4] = info[index4]+1
    index5 = partOfPlate(x-1+(y%2), y-1,plates)
    if (info[index5] != None):
        info[index5] = info[index5]+1
    index6 = partOfPlate(x+(y%2), y-1,plates)
    if (info[index6] != None):
        info[index6] = info[index6]+1
    return info
def numAdjacentLandTiles(x, y, n, f, s, d):
    global mapWidth
    global mapHeight
    if (x <= 0 or y <= 0 or x >= mapWidth-1 or y >= mapHeight-1):
        return 0 
    adjacentLandTiles = 0
    height = GetHeight(x-1+(y%2), y+1, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1
    height = GetHeight(x+(y%2), y+1, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1
    height = GetHeight(x-1, y, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1  
    height = GetHeight(x+1, y, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1 
    height = GetHeight(x-1+(y%2), y-1, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1
    height = GetHeight(x+(y%2), y-1, n, f) + d
    if (height > 0 + s):
        adjacentLandTiles = adjacentLandTiles+1   
    return adjacentLandTiles
def isAtPlateBoundary(x, y, plates,currentPlate):
    if (partOfPlate(x-1+(y%2), y+1,plates) != currentPlate):
        return True  
    if (partOfPlate(x+(y%2), y+1,plates) != currentPlate):
        return True   
    if (partOfPlate(x-1, y,plates) != currentPlate):
        return True
    if (partOfPlate(x+1, y,plates) != currentPlate):
        return True
    if (partOfPlate(x-1+(y%2), y-1,plates) != currentPlate):
        return True  
    if (partOfPlate(x+(y%2), y-1,plates) != currentPlate):
        return True
    return False
GeneratePlotTypes()
