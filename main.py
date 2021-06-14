import json
import math
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal
from PIL import Image, ImageDraw

boost = 5 * 130 / 123 * 1.02


def points_to_gaussian_heatmap(centers, height, width, scale):
    gaussians = []
    for y, x in centers:
        s = np.eye(2) * scale
        g = multivariate_normal(mean=(x, y), cov=s)
        gaussians.append(g)

    # create a grid of (x,y) coordinates at which to evaluate the kernels
    x = np.arange(0, width)
    y = np.arange(-height / 2, height / 2)
    xx, yy = np.meshgrid(x, y)
    xxyy = np.stack([xx.ravel(), yy.ravel()]).T

    # evaluate kernels at grid points
    zz = sum(g.pdf(xxyy) for g in gaussians)

    img = zz.reshape((height, width))
    return img


def makeMap(centarr, title,folder,type):
    if len(centarr)>0:
        if type==1:
            xmin=0
            xmax=0
            ymin=99
            ymax=0
            centarrshift=[]
            for x,y in centarr:
                x=x/boost
                y=y/boost
                if x<xmin:
                    xmin=x
                if x>xmax:
                    xmax=x
                if y<ymin:
                    ymin=y
                if y>ymax:
                    ymax=y

            for x, y in centarr:
                if not (x == 0 and y == 0):
                    centarrshift.append((x,y-ymin*boost))
            W = math.ceil((ymax - ymin) * boost)  # width of heatmap

            H = math.ceil((xmax - xmin) * boost)  # height of heatmap

            SCALE = 100  # increase scale to make heat map more blended

            img = points_to_gaussian_heatmap(centarrshift, H, W, SCALE)
            plt.imsave("tempheat.png", img)
            im1 = Image.open("tempheat.png")
            back_im = im1.copy()
            back_im.save(folder + '/' + title + '.png')

        else:
            W = math.ceil(120 * boost)  # width of heatmap

            H = math.ceil(55 * boost)  # height of heatmap
            SCALE = 100  # increase scale to make heat map more blended

            img = points_to_gaussian_heatmap(centarr, H, W, SCALE)

            plt.imshow(img)
            plt.show()
            plt.imsave("tempheat.png", img)

            im1 = Image.open("audl_field_of_play.png")
            im2 = Image.open("tempheat.png")
            back_im = im1.copy()
            mask_im = Image.new("L", im2.size, 0)
            draw = ImageDraw.Draw(mask_im)
            shape = [(0, 0), (W, H)]
            draw.rectangle(shape, fill=220)
            back_im.paste(im2, (65, 78), mask_im)
            back_im.save(folder+'/'+title + '.png')


teamKeyArr=["TB","ALL","ATL","AUS","BOS","CHI","DAL","DC","MAD","MIN","DET","IND","LA","NY","PHI","PIT","RAL","SD","SJ","SEA"]
evCodeArr = [3,4,8,19,198,20,22]
"""
3 Where pull landed
4 ?? reverse brink mark
8 Where turnover landed
19 drop
20 catches
22 goals
19+8=198 turnover combine



HM for each team/players turnovers/completions

Histo/ for players throwing tendencies. distance downfield / cross field turnovers/completions
I think I can see where turnover are thrown from and how far they were thrown. 
We can see if a team/Player tends to throw away a lot of throws when it's over X yard.
ID shooters
ID deep threats and players who dont go deep (resets/unders)



"""

playerCode = 0

"""
9185 billy
9187 brad
9179 adam
9210 tanner
9204 bode
9191 trava
9208 hiser
9200 javi
"""






status=0
for teamKey in teamKeyArr:
    print(str(status) +" of " + str(len(teamKeyArr)))
    status+=1
    for evCode in evCodeArr:
        centerArrIndi = []
        centerArrTot = []
        centerArrGame = []
        centerArrFromThrowerO = []
        centerArrFromThrowerD = []
        throwDict = {}
        throwDictDF = {}
        throwDictCF = {}
        receiverDict = {}
        receiverDictDF = {}
        playerDict = {}
        print(evCode)
        try:
            os.stat(teamKey)
        except:
            os.mkdir(teamKey)

        for filename in os.listdir("GameSheets"):
            gameinfo = filename.split('-')

            # print result
            #print("Game info for game on {year}-{month}-{day} where {home} was home vs visiting {away}".format(year=gameinfo[0],month=gameinfo[1],day=gameinfo[2],away=gameinfo[3],home=gameinfo[4]))


            with open('GameSheets/' + filename) as f:
                data = json.load(f)
                #Player Dictionary
                for player in data["rostersHome"]:
                    if player["id"] in playerDict:
                        pass
                    else:
                        playerDict[player["id"]]=[player["player"]["first_name"],player["player"]["last_name"],gameinfo[4]]

                for player in data["rostersAway"]:
                    if player["id"] in playerDict:
                        pass
                    else:
                        playerDict[player["id"]] = [player["player"]["first_name"], player["player"]["last_name"], gameinfo[3]]



                try:
                    if teamKey == gameinfo[3] or teamKey == gameinfo[4] or teamKey == "ALL":
                        eventArray = np.array(data["tsgAway"]["events"])
                        for line in eventArray:
                            event = line
                            if (event['t'] == 20 or event['t'] == 8 or event['t'] == 22 or event['t'] == 19) and prevcode == 20:
                                cent = ((event['x']-prevx) * boost, ((event['y']-prevy)) * boost )
                                if teamKey == gameinfo[3] or teamKey == "ALL":
                                    centerArrFromThrowerO.append(cent)
                                else:
                                    centerArrFromThrowerD.append(cent)

                            if event['t'] == 20:
                                prevx = event['x']
                                prevy = event['y']
                            prevcode = event['t']

                        eventArray = np.array(data["tsgHome"]["events"])
                        for line in eventArray:
                            event = line
                            if (event['t'] == 20 or event['t'] == 8 or event['t'] == 22 or event['t'] == 19) and prevcode == 20:
                                cent = ((event['x'] - prevx) * boost, (event['y'] - prevy) * boost)
                                if teamKey == gameinfo[4] or teamKey == "ALL":
                                    centerArrFromThrowerO.append(cent)
                                else:
                                    centerArrFromThrowerD.append(cent)

                            if event['t'] == 20:
                                prevx = event['x']
                                prevy = event['y']
                            prevcode = event['t']


                    if teamKey == gameinfo[3] or teamKey == "ALL":
                        thrower = "DEAD"
                        centerArrGame = []
                        prevcode = 0
                        eventArray = np.array(data["tsgAway"]["events"])
                        for line in eventArray:
                            event = line
                            if event['t'] == evCode:
                                cent = (event['x'] * boost, event['y'] * boost)
                                if(event['x']!=0 and event['y']!=40 ):
                                    centerArrTot.append(cent)
                                    centerArrGame.append(cent)
                            elif evCode==198 and (event['t']==19 or event['t']==8):
                                cent = (event['x'] * boost, event['y'] * boost)
                                if (event['x'] != 0 and event['y'] != 40):
                                    centerArrTot.append(cent)
                                    centerArrGame.append(cent)


                            if playerCode > 0 and event['t'] == 20 and 'r' in event and event['r'] == playerCode:
                                cent = (event['x'] * boost, event['y'] * boost)
                                centerArrIndi.append(cent)
                            if playerCode > 0 and event['t'] == 22 and 'r' in event and event['r'] == playerCode:
                                cent = (event['x'] * boost, event['y'] * boost)
                                centerArrIndi.append(cent)
                            if teamKey =="ALL":
                                if prevcode == 20 and event['t'] == 20 and thrower in throwDict:
                                    throwDictDF[thrower].append((event['y'] - prevy, "completion",gameinfo[3],gameinfo[4]))
                                    throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'completion',gameinfo[3],gameinfo[4]))
                                    throwDictCF[thrower].append((event['x'] - prevx, "completion", gameinfo[3], gameinfo[4]))

                                elif prevcode == 20 and event['t'] == 20:
                                    throwDictDF[thrower] = [(event['y'] - prevy, "completion",gameinfo[3],gameinfo[4])]
                                    throwDictCF[thrower] = [(event['x'] - prevx, "completion", gameinfo[3], gameinfo[4])]
                                    throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "completion",gameinfo[3],gameinfo[4])]

                                if prevcode == 20 and event['t'] == 20 and 'r' in event and event['r'] in receiverDict:
                                    receiverDict[event['r']].append((math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[3],gameinfo[4]))
                                    receiverDictDF[event['r']].append((event['y'] - prevy,gameinfo[3],gameinfo[4]))
                                elif prevcode == 20 and event['t'] == 20 and 'r' in event:
                                    receiverDict[event['r']] = [(math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[3],gameinfo[4])]
                                    receiverDictDF[event['r']] = [(event['y'] - prevy,gameinfo[3],gameinfo[4])]

                                if event['t'] == 8 and prevcode == 20:
                                    if thrower in throwDict:
                                        throwDictDF[thrower].append((event['y'] - prevy, 'turnover',gameinfo[3],gameinfo[4]))
                                        throwDictCF[thrower].append((event['x'] - prevx, 'turnover', gameinfo[3], gameinfo[4]))
                                        throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'turnover',gameinfo[3],gameinfo[4]))
                                    else:
                                        throwDictDF[thrower] = [(event['y'] - prevy, "turnover",gameinfo[3],gameinfo[4])]
                                        throwDictCF[thrower] = [(event['x'] - prevx, "turnover", gameinfo[3], gameinfo[4])]
                                        throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "turnover",gameinfo[3],gameinfo[4])]

                                if event['t'] == 22 and prevcode == 20:
                                    if thrower in throwDict:
                                        throwDictDF[thrower].append((event['y'] - prevy, 'goal',gameinfo[3],gameinfo[4]))
                                        throwDictCF[thrower].append((event['x'] - prevx, 'goal', gameinfo[3], gameinfo[4]))
                                        throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'goal',gameinfo[3],gameinfo[4]))
                                    else:
                                        throwDictDF[thrower] = [(event['y'] - prevy, "goal",gameinfo[3],gameinfo[4])]
                                        throwDictCF[thrower] = [(event['x'] - prevx, "goal", gameinfo[3], gameinfo[4])]
                                        throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "goal",gameinfo[3],gameinfo[4])]

                                    if 'r' in event and event['r'] in receiverDict:
                                        receiverDict[event['r']].append((math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[3],gameinfo[4]))
                                        receiverDictDF[event['r']].append((event['y'] - prevy,gameinfo[3],gameinfo[4]))
                                    else:
                                        if 'r' in event:
                                            receiverDict[event['r']] = [(math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[3],gameinfo[4])]
                                            receiverDictDF[event['r']] = [(event['y'] - prevy,gameinfo[3],gameinfo[4])]

                            if 'r' in event and  event['t'] == 20:
                                thrower = event['r']
                                prevx = event['x']
                                prevy = event['y']
                            prevcode = event['t']

                        if teamKey != "ALL":
                            makeMap(centerArrGame, str(teamKey)+"_vs_"+gameinfo[4]+"_For_"+str(evCode)+"_code",teamKey,0)


                    if teamKey == gameinfo[4] or teamKey == "ALL":
                        prevcode = 0
                        thrower = "DEAD"
                        centerArrGame = []
                        eventArray = np.array(data["tsgHome"]["events"])
                        for line in eventArray:
                            event = line
                            if event['t'] == evCode:
                                cent = (event['x'] * boost, event['y'] * boost)
                                if (event['x'] != 0 and event['y'] != 40):
                                    centerArrTot.append(cent)
                                    centerArrGame.append(cent)
                            elif evCode==198 and (event['t']==19 or event['t']==8):
                                cent = (event['x'] * boost, event['y'] * boost)
                                if (event['x'] != 0 and event['y'] != 40):
                                    centerArrTot.append(cent)
                                    centerArrGame.append(cent)

                            if playerCode > 0 and event['t'] == 20 and 'r' in event and event['r'] == playerCode:
                                centerArrIndi.append(cent)
                            if playerCode > 0 and event['t'] == 22 and 'r' in event and event['r'] == playerCode:
                                centerArrIndi.append(cent)
                            if teamKey == "ALL":
                                if prevcode == 20 and event['t'] == 20 and thrower in throwDict:
                                    throwDictDF[thrower].append((event['y'] - prevy, "completion",gameinfo[4],gameinfo[3]))
                                    throwDictCF[thrower].append((event['x'] - prevx, "completion", gameinfo[4], gameinfo[3]))
                                    throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'completion',gameinfo[4],gameinfo[3]))

                                elif prevcode == 20 and event['t'] == 20:
                                    throwDictDF[thrower] = [(event['y'] - prevy, "completion",gameinfo[4],gameinfo[3])]
                                    throwDictCF[thrower] = [(event['x'] - prevx, "completion", gameinfo[4], gameinfo[3])]
                                    throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "completion",gameinfo[4],gameinfo[3])]

                                if prevcode == 20 and event['t'] == 20 and 'r' in event and event['r'] in receiverDict:
                                    receiverDict[event['r']].append((math.hypot(event['x'] - prevx, event['y'] - prevy), gameinfo[4],gameinfo[3]))
                                    receiverDictDF[event['r']].append((event['y'] - prevy, gameinfo[4],gameinfo[3]))
                                elif 'r' in event and prevcode == 20 and event['t'] == 20 :
                                    receiverDict[event['r']] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), gameinfo[4],gameinfo[3])]
                                    receiverDictDF[event['r']] = [(event['y'] - prevy, gameinfo[4],gameinfo[3])]



                                if event['t'] == 8 and prevcode == 20:
                                    if thrower in throwDict:
                                        throwDictDF[thrower].append((event['y'] - prevy, 'turnover',gameinfo[4],gameinfo[3]))
                                        throwDictCF[thrower].append((event['x'] - prevx, 'turnover', gameinfo[4], gameinfo[3]))
                                        throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'turnover',gameinfo[4],gameinfo[3]))
                                    else:
                                        throwDictDF[thrower] = [(event['y'] - prevy, "turnover",gameinfo[4],gameinfo[3])]
                                        throwDictCF[thrower] = [(event['x'] - prevx, "turnover", gameinfo[4], gameinfo[3])]
                                        throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "turnover",gameinfo[4],gameinfo[3])]

                                if event['t'] == 22 and prevcode == 20:
                                    if thrower in throwDict:
                                        throwDictDF[thrower].append((event['y'] - prevy, 'goal',gameinfo[4],gameinfo[3]))
                                        throwDictCF[thrower].append((event['x'] - prevx, 'goal', gameinfo[4], gameinfo[3]))
                                        throwDict[thrower].append((math.hypot(event['x'] - prevx, event['y'] - prevy), 'goal',gameinfo[4],gameinfo[3]))
                                    else:
                                        throwDictDF[thrower] = [(event['y'] - prevy, "goal",gameinfo[4],gameinfo[3])]
                                        throwDictCF[thrower] = [(event['x'] - prevx, "goal", gameinfo[4], gameinfo[3])]
                                        throwDict[thrower] = [(math.hypot(event['x'] - prevx, event['y'] - prevy), "goal",gameinfo[4],gameinfo[3])]

                                    if 'r' in event and event['r'] in receiverDict:
                                        receiverDict[event['r']].append((math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[4],gameinfo[3]))
                                        receiverDictDF[event['r']].append((event['y'] - prevy,gameinfo[4],gameinfo[3]))
                                    elif 'r' in event:
                                        receiverDict[event['r']] = [(math.hypot(event['x'] - prevx, event['y'] - prevy),gameinfo[4],gameinfo[3])]
                                        receiverDictDF[event['r']] = [(event['y'] - prevy,gameinfo[4],gameinfo[3])]

                            if 'r' in event and event['t'] == 20:
                                thrower = event['r']
                                prevx = event['x']
                                prevy = event['y']
                            prevcode = event['t']

                        if teamKey != "ALL":
                            makeMap(centerArrGame, str(teamKey)+"_vs_"+gameinfo[3]+"_For_"+str(evCode)+"_code",teamKey,0)

                except Exception as e:
                    print(str(teamKey) + "not found")
                    print("Error Found was: "+str(e))

        if len(centerArrIndi) > 0:
            makeMap(centerArrIndi, "All_Games_For_Player_"+str(playerCode),teamKey,0)
        makeMap(centerArrTot, str(teamKey) + "_ALL_GAMES_"+str(evCode)+"_code", teamKey, 0)
        if evCode == 20:
            makeMap(centerArrFromThrowerO, str(teamKey)+"_O_From_Thrower",teamKey,1)
            makeMap(centerArrFromThrowerD, str(teamKey)+"_D_From_Thrower",teamKey,1)
    if teamKey == "ALL":
        with open('ALL\playDir.csv', 'w', newline='') as csvfile:
            count = 1
            playerWriter = csv.writer(csvfile, delimiter=',')
            playerWriter.writerow(["ID", "First name", "Last Name", "Full Name", "Team"])
            for key in playerDict:
                playerWriter.writerow(
                    [key, playerDict[key][0], playerDict[key][1], playerDict[key][0] + " " + playerDict[key][1],
                     playerDict[key][2]])

        with open(str(teamKey) + '/' + str(teamKey) + '_throwInfo.csv', 'w', newline='') as csvfile:
            count = 1
            throwWriter = csv.writer(csvfile, delimiter=',')
            throwWriter.writerow(["ID", "Player", "Dist", "Type", "O", "D"])
            for key in throwDict:
                for dist, type, o, d in throwDict[key]:
                    throwWriter.writerow([count, key, dist, type, o, d])
                    count += 1

        with open(str(teamKey) + '/' + str(teamKey) + '_throwInfoCF.csv', 'w', newline='') as csvfile:
            throwWriter = csv.writer(csvfile, delimiter=',')
            throwWriter.writerow(["ID", "Player", "Dist", "Type", "O", "D"])
            count = 1
            for key in throwDictCF:
                for dist, type, o, d in throwDictCF[key]:
                    throwWriter.writerow([count, key, dist, type, o, d])
                    count += 1

        with open(str(teamKey) + '/' + str(teamKey) + '_throwInfoDF.csv', 'w', newline='') as csvfile:
            throwWriter = csv.writer(csvfile, delimiter=',')
            throwWriter.writerow(["ID", "Player", "Dist", "Type", "O", "D"])
            count = 1
            for key in throwDictDF:
                for dist, type, o, d in throwDictDF[key]:
                    throwWriter.writerow([count, key, dist, type, o, d])
                    count += 1

        with open(str(teamKey) + '/' + str(teamKey) + '_receiverInfo.csv', 'w', newline='') as csvfile2:
            receiverWriter = csv.writer(csvfile2, delimiter=',')
            receiverWriter.writerow(["ID", "Player", "Dist", "O", "D"])
            count = 1
            for key in receiverDict:
                for dist, o, d in receiverDict[key]:
                    receiverWriter.writerow([count, key, dist, o, d])
                    count += 1

        with open(str(teamKey) + '/' + str(teamKey) + '_receiverInfoDF.csv', 'w', newline='') as csvfile2:
            receiverWriter = csv.writer(csvfile2, delimiter=',')
            receiverWriter.writerow(["ID", "Player", "Dist", "O", "D"])
            count = 1
            for key in receiverDictDF:
                for dist, o, d in receiverDictDF[key]:
                    receiverWriter.writerow([count, key, dist, o, d])
                    count += 1




