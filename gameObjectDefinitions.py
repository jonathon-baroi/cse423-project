def defineGameObjects():    
    from main import Engine
    
    playerX = 50
    playerY = 100
    playerWalkSpeed = 300
    playerJumpSpeed = 200
    playerGravity = 200

    wallDrawParams = ["co", [0,1,1], "l", [0, 0], [30, 0], [30, 30], [0, 30], [0, 0], "co", [1, 1, 0]]
    enemyDrawParams = ["co", [1, 0, 1], "c", [10, 10, 10], "co", [1, 0, 0], "c", [15, 15, 3], "c", [15, 15, 5], "c", [5, 15, 3], "c", [5, 15, 5]]
    spikeDrawParams = ["co", [1, 0.5, 0], "l", [0, 0], [15, 15], [30, 0]]    
    endPointDrawParams = ["co", [1,1,0],"c", [15, 15, 15], "c", [15, 15, 10], "c", [15, 15, 5]]   
    playerDrawParams = ["co", [1,0,0], "c", [0, 0, 10], "c", [0, 0, 9], "c", [0, 0, 8], "c", [0, 0, 7], "c", [0, 0, 6]]

    player = Engine().createPlayer(
        playerX, playerY,
        [
            *playerDrawParams            
        ], 
        [playerWalkSpeed, playerJumpSpeed, playerGravity], 
        True)    

    def addWall(x, y):
        wall = Engine().createGameObject(
        x, y,
        [
            *wallDrawParams      
        ], True, True)      
        Engine().addCollisionPair(player, wall)
        return wall
    
    def addSpike(x, y):
        spike = Engine().createGameObject(
        x, y,
        [
            *spikeDrawParams  
        ], True, False)      
        Engine().addCollisionPair(player, spike, Engine().touchEnemy)
        return spike
    
    def addEnemy(x, y, speed, direction):
        enemy = Engine().createEnemy(
        x, y,
        [
             *enemyDrawParams          
        ], speed, direction)              
        Engine().addCollisionPair(player, enemy, Engine().touchEnemy)
        return enemy
    
    def addEndPoint(x, y):
        endPoint = Engine().createGameObject(
        x, y,
        [
                *endPointDrawParams     
        ], True, False)              
        Engine().addCollisionPair(player, endPoint, Engine().gameEnd)
        return endPoint

    Engine().setPlayerStartPosition(playerX, playerY)


    for x in range(0, 1280, 30):
        addWall(x, 0)
        
    for y in range(30, 720, 30):
        addWall(0, y)
        addWall(1260, y)
    for x in range(300, 500, 30):
        addWall(x, 70)
    for y in range(70, 200, 30):
        addWall(510, y)
    for x in range(30, 200, 30):
        addWall(x, 160)
    for x in range(300, 400, 30):
        addWall(x, 210)    

    for x in range(300, 400, 30):
        addWall(x, 300)   

    addWall(450, 360)
    addWall(600, 400)    
    addWall(750, 440)

    for y in range(500, 720, 30):
        addWall(800, y)

    for y in range(30, 500, 30):
        addWall(700, y)

    for x in range(730, 900, 30):
        addWall(x, 70)

    addEndPoint(800, 100)
    addSpike(360, 330)
    addSpike(390, 330)
    
    addEnemy(300, 400, 100, "left-right")
    addEnemy(300, 550, 100, "left-right")
    addWall(200, 500)
    addEnemy(200, 200, 100, "up-down")
    addWall(650, 600)
    addEnemy(650, 200, 100, "up-down")
    for x in range(500, 680, 30):
        addSpike(x, 30)
    
