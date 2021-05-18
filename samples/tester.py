import os
import time
import random
from pyclap.pyclap import ConsoleUI,PanelRect
from datetime import datetime

textPanel=None
tablePanel=None
graphicsPanel=None
rollingTextPanel=None
screen=None
graphicsList=[
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"GAME","fg":"black","bg":"yellow","r":-1,"c":-1},
               {"cldr":"OF","fg":"black","bg":"yellow","r":-1,"c":-1},
               {"cldr":"LIFE","fg":"black","bg":"yellow","r":-1,"c":-1},
               {"cldr":"grinning face","bg":"38","r":-1,"c":-1},
               {"cldr":"grinning face","bg":"38","r":-1,"c":-1},
               {"cldr":"grinning face","bg":"38","r":-1,"c":-1},
               {"cldr":"grinning face","bg":"38","r":-1,"c":-1},
               {"cldr":"upside-down face","bg":"38","r":-1,"c":-1},
               {"cldr":"upside-down face","bg":"38","r":-1,"c":-1},
               {"cldr":"upside-down face","bg":"38","r":-1,"c":-1},
               {"cldr":"upside-down face","bg":"38","r":-1,"c":-1},
               {"cldr":"upside-down face","bg":"38","r":-1,"c":-1},
               {"cldr":"grimacing face","bg":"38","r":-1,"c":-1},
               {"cldr":"grimacing face","bg":"38","r":-1,"c":-1},
               {"cldr":"grimacing face","bg":"38","r":-1,"c":-1},
               {"cldr":"grimacing face","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with sunglasses","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with sunglasses","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with sunglasses","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with sunglasses","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with sunglasses","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"smiling face with smiling eyes","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"sleepy face","bg":"38","r":-1,"c":-1},
               {"cldr":"raised hand","bg":"38","r":-1,"c":-1},
               {"cldr":"raised hand","bg":"38","r":-1,"c":-1},
               {"cldr":"raised hand","bg":"38","r":-1,"c":-1},
               {"cldr":"raised hand","bg":"38","r":-1,"c":-1},
               {"cldr":"raised hand","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
               {"cldr":"zipper-mouth face","bg":"38","r":-1,"c":-1},
             ]

def initDisplay():
   global screen,textPanel,tablePanel,graphicsPanel,rollingTextPanel
   screen = ConsoleUI(bgColor="186")
   screen.setTitle({"title":f"PyClap Emojical Tester App{screen.getEmoji('smiling face with smiling eyes')}"})
   margin=3
   startRow=3
   halfScreenWidth = int((screen.cols() - 3*margin)/2)
   halfScreenHeight = int((screen.rows() - 3*margin)/2)

   textPanelPos = PanelRect(startRow,margin,halfScreenHeight,halfScreenWidth)
   textPanel = screen.createPanel("textPanel",f"Text Panel (Show marked-up text)",textPanelPos,"225","black")
   textPanel.titleIcon(f"{screen.getEmoji('open book')}")

   tablePanelPos = PanelRect(startRow,2*margin+halfScreenWidth,halfScreenHeight,halfScreenWidth)
   tablePanel = screen.createTablePanel("tablePanel",f"Table Panel (Show structured data)",tablePanelPos,"38","white")
   tablePanel.columns([
                           ["sno","No.",round(halfScreenWidth/3),True],
                           ["cldr","CLDR",round(halfScreenWidth/3)],
                           ["emoji","Emoji",round(halfScreenWidth/3)],
                       ]).headerColors("blue").render()
   tablePanel.titleIcon(f"{screen.getEmoji('black square button')}")

   graphicsPanelPos = PanelRect(textPanel.bottom()+margin,margin,halfScreenHeight,halfScreenWidth)
   graphicsPanel = screen.createPanel("graphicsPanel",f"Graphics Panel (Build your own games)",graphicsPanelPos,"38","black")
   graphicsPanel.titleIcon(f"{screen.getEmoji('rainbow')}")

   rollingTextPanelPos = PanelRect(textPanel.bottom()+margin,2*margin+halfScreenWidth,halfScreenHeight,halfScreenWidth)
   rollingTextPanel= screen.createRollingPanel("rollingTextPanel","Rolling Panel (Show logs and progress)",rollingTextPanelPos,"128","white")
   rollingTextPanel.titleIcon(f"{screen.getEmoji('scroll')}")
   btn=screen.getEmoji('small orange diamond')
   rbtn=screen.getEmoji('radio button')
   bbtn=screen.getEmoji('black circle')
   textPanel.printText(
f'''
Hi there!
   <fg:88>Welcome to PyClap!</fg> PyClap is a library that can be used to add jUIce to your python console apps.
   With PyClap, you can easily create and place UI panels anywhere on your terminal screen. Panels can have the following
      {btn} Title Bar with centered title
      {btn} Foreground and Background Color
      {btn} Title Icon (at top left corner)
   You can use panels to show
      {bbtn} Flowing text within a confined area (like this panel)
      {bbtn} Tabular data (with a key column, if needed)
      {bbtn} Positioned text within the panel
      {bbtn} Rolling text (rolls upwards)
   This library also provides apis to place emojis anywhere within the panel. <fg:13>Emjoy{screen.getEmoji('winking face')}</fg>!!
   Refer to the following other sample apps in the package for more examples
      {rbtn} sysmon.py - A console app like 'top' but with UI
      {rbtn} kubectlw.py - A console app like to show details of kuberetes pods
      {rbtn} palette.py - An app to show the palette of foreground and background colors
      {rbtn} emojilist.py - An app to show all the emojis
''',markdown=True)

def updatePanels(counter):
   global screen,textPanel,tablePanel,graphicsPanel,rollingTextPanel
   if(counter%2 == 0):
      for i in range(0,tablePanel.panel_height()-2): 
         rnum = random.randint(0,1500)
         emojiTuple = screen.getEmojiTuple(rnum)
         tablePanel.printRow({"sno":f"{i+1}","cldr":emojiTuple[0],"emoji":emojiTuple[1]})
      now = datetime.now()
      rnum = random.randint(0,1500)
      emojiTuple = screen.getEmojiTuple(rnum)
      rollingTextPanel.append(f"{now.strftime('%H:%M:%S')}: {emojiTuple[0]} {emojiTuple[1]}")

   for g in graphicsList:
      if(g["r"] != -1):
          e = screen.getEmoji(g["cldr"])
          spaces=2
          if(e == g["cldr"]):
             spaces=len(g["cldr"])
          if(spaces == 0):
             spaces=2
          fillText=" "*spaces
          graphicsPanel.printAt(g["r"],g["c"],fillText,None,"38")
          g["r"] = -1
          g["c"] = -1
   for g in graphicsList:
      g["r"] = random.randint(2,graphicsPanel.panel_height()-5)
      g["c"] = random.randint(2,graphicsPanel.panel_width()-10)
      if(screen.getEmoji(g["cldr"]) != None):
          graphicsPanel.printAt(g["r"],g["c"],screen.getEmoji(g["cldr"]),None,g["bg"])
      elif(g["cldr"] != ""):
          graphicsPanel.printAt(g["r"],g["c"],g["cldr"],"black",g["bg"])
      else:
          graphicsPanel.printAt(g["r"],g["c"]," ",None,g["bg"])

def main():
   initDisplay()
   count=0
   while(True):
       updatePanels(count)
       #time.sleep(0.25)
       time.sleep(1)
       count += 1

main()
