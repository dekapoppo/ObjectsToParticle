##
##　Objencts to nParticle for Maya2018
##
#  2020.04.17 v2.0 dekapoppo
#
#
# 使い方：　GUI起動後
#        オブジェクトを複数選択してSTEP1実行　⇒ nParticle作成（位置反映）
#        できればそのままSTEP2実行　⇒　RotationPP追加（回転反映）
#
# 補足：　オブジェクトの位置データは処理を軽くするため丸めてます（精度は　rC で変更可）
#
#
#
import maya.cmds as mc
import math


pName = ["",""]

##ウインドウが既存なら閉じて開きなおす
if mc.window("objects2nParticeWindow", exists = True):
    mc.deleteUI("objects2nParticeWindow")
##ウインドウのサイズと並べ方設定
rWindow = mc.window("objects2nParticeWindow", t="Objects convert nPartice v2.0")
mc.columnLayout(cal="left",  adj=True, rowSpacing=5, columnWidth=450)
##GUI
#オブジェクトからnParticle作成　（nParticleからnParticle再作成）
mc.text("■ Object to nParticle / nParticle to nParticle")
mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 60), (2,240), (3, 300)],cal=[2,"left"] )
mc.text("STEP1")
mc.text("選択したオブジェクト or Particlesの位置に\nparticleを持つnParticleを作成") 

mc.rowColumnLayout( numberOfColumns=4, columnWidth=[(1, 100), (2,100), (3,5),(4, 95)],cal=[2,"left"] )
mc.button(l="Select Objects\ngen nParticle!", c = "start(0)", bgc=[0.7,0.7,0.9])
mc.button(l="Select Particles\ngen nParticle!", c = "start(1)", bgc=[0.9,0.7,0.7])
mc.text("")
cmds.rowColumnLayout( numberOfRows=2, rowHeight=[(1, 30), (2, 30)] )
mc.button(l=" Select MASH\npre run ", c = "MASHp2ptc_pre()", bgc=[0.7,0.9,0.7])
mc.button(l=" gen nParticle! ", c = "MASHp2ptc_main()", bgc=[0.7,0.9,0.7])
mc.setParent("..")
mc.setParent("..")
mc.setParent("..")

mc.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 60), (2,240), (3, 300)],cal=[2,"left"] )
mc.text("STEP2")
mc.text("RotationPPを追加してオブジェクトの回転値を代入")
mc.button(l="set RotationPP", c = "setRotationPP()", bgc=[0.9,0.9,0.6])
mc.text("  ")
rotPPckBox = mc.checkBoxGrp('checkBoxTz', numberOfCheckBoxes=3, labelArray3=['rotX','rotY', 'rotZ'],columnWidth3=[50,50,50], valueArray3=[1,1,1], ann="""【加算】　相対値で変化します。既定では絶対値で値は入替られます。【ワールド空間】　ワールド座標軸で変化します。既定ではオブジェクト軸です。""")
mc.text("   ")
mc.setParent("..")

mc.text("※ エラーあればnParticleShapeのPerParticleのタブを開くと解決")

#nParticleの位置にオブジェクト複製
mc.text("----------------------------------------------------------------------------------------------------------------------------------------------------")
mc.text("■ nParticle to Object")
mc.text("パーティクルの位置にオブジェクトを複製　（ソースオブジェクト → nParticle　を選択して実行）")
mc.button(l="Duplicate(instance) to particels", c = "dupObj()", bgc=[0.6,0.8,0.9])
mc.text("\n")

#nParticleの位置にオブジェクト複製
mc.text("----------------------------------------------------------------------------------------------------------------------------------------------------")
mc.button(l="View ComponentEditor", c = "mc.ComponentEditor()", bgc=[0.9,0.9,0.9])
##ウインドウ表示
mc.showWindow(rWindow)


#=======================================================================
rC = 3 #小数点以下の桁数指定★★
#========================================================================
def start(type):
    global selObj
    selObj = mc.ls(sl=True,fl=True)
    if len(selObj)<1:
        mc.confirmDialog( title=("Error"), message='Select more than 1 Object!', button=['OK'] )
    else:    
        #オブジェクトの数確認画面
        window = mc.confirmDialog( title=("Objects convert nParticles"), message=('SelectObjectsPosition to nParticle !\n\ncount :'+str(len(selObj))), button=['OK','Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel' )
        if window=="OK":
            if type==0:
                main()
            if type==1:
                dupPtc()      


def getPosrot():
    global pPos
    global pRot
    pPos=[]
    pRot=[]
    #convert ObjectPosition to pythonList (選択したオブジェクトの位置と回転取得）　リスト化
    for i in selObj:
        pos = mc.xform(i,q=True,ws=True,t=True) # 絶対位置取得
        pPos.append((round(pos[0],rC),round(pos[1],rC),round(pos[2],rC)))
        rot = mc.xform(i,q=True,a=True,ro=True) # 回転値取得
        pRot.append((round(rot[0],rC),round(rot[1],rC),round(rot[2],rC)))


def getSelPtcPosrot():
    global pPos
    global pRot
    global pName
    pPos=[]
    pRot=[]
    #nParticleのパーティクルを選択して実行→位置とrotationPPが取得されます
    #選択したnParticleのidリスト取得
    rC = 3 #小数点以下の精度指定
    selPtc = mc.ls(sl=True,fl=True)
    selIndexList = []
    for i in selPtc:
        num = i.split("[")[1][:-1]
        selIndexList.append(int(num))
    #nParticle名取得
    pName[0] = selPtc[0].split("[")[0][:-3]
    pName[1] = mc.listRelatives(pName[0],shapes=True,f=True) #fでフルパス指定！ネームスペースがあるときはこれ必須
    #nParticleの移動値を反映する
    offset = [mc.getAttr(pName[0]+".translateX"),mc.getAttr(pName[0]+".translateY"),mc.getAttr(pName[0]+".translateZ")]
    moveRotY = mc.getAttr(pName[0]+".rotateY")
    #print selIndexList
    #指定したidのパーティクルの位置にnParticle新規作成
    for i in selIndexList:
        pos = mc.nParticle(pName[0], q=True, at="position",id=i)
        #nParticleの回転を回転移動で反映
        newPosZ = round(pos[2]*math.cos(math.radians(moveRotY))-pos[0]*math.sin(math.radians(moveRotY)), rC)
        newPosX = round(pos[2]*math.sin(math.radians(moveRotY))+pos[0]*math.cos(math.radians(moveRotY)), rC)
        #位置代入
        pPos.append((newPosX+offset[0],round(pos[1]+offset[1],rC),newPosZ+offset[2]))
        rot = mc.nParticle(pName[0], q=True, at="rotationPP", id=i)
        pRot.append((round(rot[0],rC),round(rot[1],rC),round(rot[2],rC)))


    
def genPtc():
    global pName
    #位置と回転のリストからnParticle作成
    pName = mc.nParticle(p=pPos, c=True)
    mc.setAttr(pName[1]+".forcesInWorld",0) #ワールドフォースを無効にして動かないように固定
    mc.setAttr(pName[1]+".collide",0) #コリジョン無効に
    mc.setAttr(pName[1]+".computeRotation",1) #後に変更できるようにrotationPPを有効に


def main():
    getPosrot()
    genPtc()


def dupPtc():
    getSelPtcPosrot()
    genPtc()


def setRotationPP():
    #チェックボックスから有効にする回転値を判断して、リスト再処理
    rotCk = []
    rotCk.append(mc.checkBoxGrp(rotPPckBox, q=True, v1=True))
    rotCk.append(mc.checkBoxGrp(rotPPckBox, q=True, v2=True))
    rotCk.append(mc.checkBoxGrp(rotPPckBox, q=True, v3=True))
    newRot = [ (pRot[i][0]*rotCk[0], pRot[i][1]*rotCk[1], pRot[i][2]*rotCk[2]) for i in range(len(pRot))]
    #print newRot
    #あとは nParticleに反映
    for j in range(len(newRot)):
        mc.nParticle(pName[0], e=True, attribute='rotationPP', id=j, vv=newRot[j] ) 

def dupObj():
    selList = mc.ls(sl=True) #オブジェクト → nParticle の順に選択
    count = mc.nParticle(selList[1], q=True, count=True)
    copySet = [] #最後にグループまとめるためのリスト
    #nParticleの移動値を反映する
    offset = [mc.getAttr(selList[1]+".translateX"),mc.getAttr(selList[1]+".translateY"),mc.getAttr(selList[1]+".translateZ")]
    #複製処理
    for i in range(count):
        #まずオブジェクトを複製（インスタンス）
        copyA = mc.duplicate(selList[0],rr=True,un=0,instanceLeaf=1,renameChildren=0,n=selList[0]+"ins1") #複製
        copySet.append(copyA[0]) #追加
        #パーティクルの位置取得して、複製オブジェクトを移動
        posP = mc.nParticle(selList[1], q=True, at="position",id=i)
        rotP = mc.nParticle(selList[1], q=True, at="rotationPP", id=i)
        #まず位置から
        posA = mc.xform(copyA,q=True,ws=True,rp=True) # Aコピーの原点に対する相対位置取得
        mc.move(posP[0]-posA[0]+offset[0],posP[1]-posA[1]+offset[1],posP[2]-posA[2]+offset[2],copyA,r=True) # Aコピーの移動
        #次に回転
        rotA = mc.xform(copyA,q=True,ro=True,a=True) # Aコピーの回転値取得
        mc.rotate(rotP[0],rotP[1],rotP[2],copyA[0],a=True) # Aコピーの回転
    #最後にアクティブorグループ化にして終了
    mc.group(copySet,n=selList[0]+"_dupSet")



#============
#MASH専用機能
#============
import maya.mel as mel
import openMASH
import MASH.deleteMashNode as dmn

def MASHp2ptc_pre(): #MashPythonNode作成
    sel = mc.ls(sl=True) #MASHノード選択
    mel.eval('MASHaddNode("MASH_Python","%s");' %sel[0])#Pythonノード追加
    global pyNodeName
    pyNodeName = mc.ls(sl=True)[0]
    mc.setAttr(pyNodeName+".enable",0)#無効化

def MASHp2ptc_main(): #位置のリスト作成してPythonNode削除
    #OpenMASH
    md = openMASH.MASHData(pyNodeName)
    count = md.count()
    #MASHポイントの位置・回転をリスト化
    global pPos
    global pRot
    pPos=[]
    pRot=[]
    for i in range(count):
        pPos.append((round(md.outPosition[i].x,rC),round(md.outPosition[i].y,rC),round(md.outPosition[i].z,rC)))
        pRot.append((round(md.outRotation[i].x,rC),round(md.outRotation[i].y,rC),round(md.outRotation[i].z,rC)))
    #追加したPythonノードを削除(★★注意★★step1と連続で実行するとフリーズします）
    dmn.deleteMashNode(pyNodeName)
    #nParticle作成
    genPtc()




      