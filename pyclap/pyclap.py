#!/usr/local/bin/python3

import os
import time
from pyclap.emojis import emojilist

# Default values to start with
rows=20
cols=80

#Some macros for screen control
CLEAR_SCREEN="\033[2J"
HOME_CURSOR="\033[0;0H"
CURSOR_OFF="\033[?25l"
CURSOR_ON="\033[?25h"
WIDE_SCREEN="\033[?3h"
NORMAL_SCREEN="\033[?3l"
UNDER_ON="\033[4m"
INSERT_LINE="\033[1L"
DELETE_LINE="\033[1M"
REVERSE_VIDEO="\033[7m"
NORMAL_VIDEO="\033[0m"

#Foreground color codes by color name
fgColorCode = {
  "black":"\033[30m",
  "red":"\033[31m",
  "green":"\033[32m",
  "orange":"\033[33m",
  "blue":"\033[34m",
  "magenta":"\033[35m",
  "cyan":"\033[36m",
  "lightgray":"\033[37m",
  "white":"\033[97m",
  "reset":"\033[39m"
}
#Background color codes by color name
bgColorCode = {
  "black":"\033[40m",
  "red":"\033[41m",
  "green":"\033[42m",
  "orange":"\033[43m",
  "blue":"\033[44m",
  "magenta":"\033[45m",
  "cyan":"\033[46m",
  "lightgray":"\033[47m",
  "darkgray":"\033[100m",
  "lightred":"\033[101m",
  "lightgreen":"\033[102m",
  "yellow":"\033[103m",
  "lightblue":"\033[104m",
  "lightpurple":"\033[105m",
  "teal":"\033[106m",
  "white":"\033[107m",
  "reset":"\033[49m"
}

#Panel collection
panels = {}

#Default background color for screen 
screenColorCode=bgColorCode['white']

def MOVE(x,y):
   str=f"\033[{round(y)};{round(x)}H"
   os.system(f"printf \"{str}\"")
   #print(f"\033[{y};{x}f")

#Hack to get control of the full screen
#Just print an empty string on the last row
def touchLastRow():
    MOVE(1,rows)
    print("",flush=True,end='\r')

def getBGColorCode(colorString):
       colorCode=""
       resetColor=bgColorCode['reset']
       if(colorString in bgColorCode):
            colorCode = bgColorCode[colorString]
       elif (colorString.isnumeric() == True):
            num = int(colorString)%255
            colorCode = f"\033[48;5;{num}m"
            resetColor = f"\033[49;49m"
       else: 
            colorCode = bgColorCode['white'] 
       return (colorCode,resetColor)

def getFGColorCode(colorString):
       colorCode=""
       resetColor=fgColorCode['reset']
       if(colorString in fgColorCode):
            colorCode = fgColorCode[colorString]
       elif (colorString.isnumeric() == True):
            num = int(colorString)%255
            colorCode = f"\033[38;5;{num}m"
            resetColor = f"\033[39;49m"
       else: 
            colorCode = fgColorCode['white'] 
       return (colorCode,resetColor)

class ColumnDef:
   def __init__(self,columnName,columnTitle,columnWidth):
       self.columnName = columnName
       self.columnTitle = columnTitle
       self.columnWidth = columnWidth

class TableDef:
   def __init__(self,tableName):
       self.tableName = tableName
       self.colMap={}
       self.columns=[]
       self.indexName=None

   def addColumn(self,columnDef,isIndex=False):
       self.colMap[columnDef.columnName]=len(self.columns)
       self.columns.append(columnDef)
       if (isIndex == True):
           self.indexName=columnDef.columnName
       return self; 
   

class PanelRect:
   def __init__(self,top,left,height,width):
       self.top = top
       self.left = left
       self.height = height
       self.width = width

class Panel:

   def fillRow(self,rowNum,bgColor):
       fill = " "*self.width
       print(f"{bgColor}",end='')
       MOVE(self.left,rowNum)
       print(f"{fill}",end='\r')

   def setConsole(self,console):
       self.console = console

   def printText(self,text,markdown=False):
       if(markdown):
           text = text.replace(f"</bg>",f"{self.bgColor}")
           text = text.replace(f"</fg>",f"{self.fgColor}")
           for i in range(1,256):
               bgColor = getBGColorCode(f"{i}")
               text = text.replace(f"<bg:{i}>",f"{bgColor[0]}")
               text = text.replace(f"</bg:{i}>",f"{self.bgColor}")
               fgColor = getFGColorCode(f"{i}")
               text = text.replace(f"<fg:{i}>",f"{fgColor[0]}")
               text = text.replace(f"</fg:{i}>",f"{self.fgColor}")
       lines=text.splitlines()
       row=1
       width=self.width-1
       for line in lines:
          for i in range(0, len(line), width):
             self.printAt(row,1,line[i:i+width])
             row += 1

   def clearRows(self,rowstart):
       for rownum in range(rowstart,self.height):
           self.fillRow(self.top+rownum,self.bgColor)

   def clearPanel(self):
       self.clearRows(1);

   def fillColor(self,startRow,bgColor):
       i=startRow
       fill = " "*self.width
       print(f"{bgColor}",end='')
       while(i<=self.bottomY):
           MOVE(self.left,i)
           print(f"{fill}",end='\r')
           i += 1


   def centerText(self,row,text,fgColor=None,bgColor=None):
       if(bgColor == None):
           bgColor = (self.bgColor,self.bgReset)
       else:
           bgColor = getBGColorCode(bgColor)

       if(fgColor == None):
           fgColor = (self.fgColor,self.fgReset)
       else:
           fgColor = getFGColorCode(fgColor)

       MOVE(self.left,row)
       fill=" " * self.width
       print(f"{bgColor[0]}{fgColor[0]}{fill}",end='\r')
       tlen=len(text)
       MOVE(self.left+round((self.width-tlen)/2),row)
       print(f"{bgColor[0]}{fgColor[0]}{text}",end='\r')
       print(f"{bgColor[1]}{fgColor[1]}",end='\r')

   def printAt(self,row,col,text,fgColor=None,bgColor=None):
       if (bgColor == None):
           bgCode = (self.bgColor,self.bgReset)
       else:
           bgCode = getBGColorCode(bgColor)
       if (fgColor == None):
           fgCode = (self.fgColor,self.bgReset)
       else:
           fgCode = getFGColorCode(fgColor)
       MOVE(self.left+col,self.top+row)
       print(f"{bgCode[0]}{fgCode[0]}{text}",end='\r')
       print(f"{bgCode[1]}{fgCode[1]}",flush=True,end='\r')
       touchLastRow()

   def append1(self,msg):
       global rows
       print(f"{self.bgReset}",end='')
       MOVE(self.left,self.top+1)
       print(DELETE_LINE,end='\r')
       MOVE(self.left,self.bottomY)
       print(f"{screenColorCode}",end='')
       print(INSERT_LINE,end='\r')
       MOVE(self.left,self.bottomY)
       print(f"{self.bgColor}{self.fgColor}",end='')
       fill = " "*self.width
       print(f"{fill}",end='\r')
       MOVE(self.left,self.bottomY)
       print(msg,flush=True,end='\r')

   def append(self,msg):
       msg = msg.replace("\n","")
       colwidth = (self.width - 4)
       data = msg[:colwidth] + '..' * (len(msg) > colwidth)
       msg = data
       fill = " "*(self.width-len(msg.encode('utf-8')))
       nmsg = msg + fill
       fill = " "*(self.width-len(nmsg)-1)
       nmsg = nmsg + fill
       self.msgs.append(nmsg)
       if(len(self.msgs) >= self.height):
           self.msgs.pop(0)
       for i in range(1, self.height):
          index=len(self.msgs)-i
          if(index>=0):
              self.printAt(self.height-i,0,self.msgs[index])
       

   def top(self):
       return self.top

   def bottom(self):
       return self.top+self.height

   def left(self):
       return self.left

   def right(self):
       return self.left + self.width

   def panel_height(self):
       return self.height

   def panel_width(self):
       return self.width

   def __init__(self,console,panelName,panelTitle,panelRect,bgcolor,fgcolor):
        self.console=console
        self.panelName=panelName
        self.panelTitle=panelTitle
        self.panelRect=panelRect
        self.top=panelRect.top
        self.left=panelRect.left
        self.width=panelRect.width
        self.height=panelRect.height
        self.bottomY = panelRect.top+panelRect.height-1
        self.bgReset = f"\033[49;49m"
        self.fgReset = f"\033[39;49m"
        self.msgs = []
        if(bgcolor in bgColorCode):
            self.bgColor = bgColorCode[bgcolor]
        elif (bgcolor.isnumeric() == True):
            num = int(bgcolor)%255
            self.bgColor = f"\033[48;5;{num}m"
        else: 
            self.bgColor = bgColorCode['white'] 
        if(fgcolor in fgColorCode):
            self.fgColor = fgColorCode[fgcolor]
        elif (fgcolor.isnumeric() == True):
            num = int(fgcolor)%255
            self.fgColor = f"\033[38;5;{num}m"
        else:
            self.fgColor = fgColorCode['black'] 
        self.fillColor(self.top,self.bgColor)
        self.centerText(self.top,panelTitle,self.console.panelFGColor,self.console.panelBGColor)

   def titleIcon(self,iconText,bgColor=None):
       if(bgColor == None):
           bgColor = self.console.panelBGColor
       self.printAt(0,0,iconText,self.console.panelFGColor,bgColor)

class TablePanel(Panel):
   rowstart=2
   def __init__(self,console,panelName,panelTitle,panelRect,tableDef,bgcolor,fgcolor):
       super().__init__(console,panelName,panelTitle,panelRect,bgcolor,fgcolor)
       self.tableDef = tableDef
       self.tabStops = []
       self.rows = []
       self.rowIndexMap={}
       self.hdrFgColor = None
       self.hdrBgColor = None

   def headerColors(self,fgColor=None,bgColor=None):
       self.hdrFgColor = fgColor
       self.hdrBgColor = bgColor
       return self

   def render(self):
       totalWidth=0
       self.tabStops.append(totalWidth)
       if(len(self.tableDef.columns) > 0):
           avgWidth = round(self.panelRect.width/len(self.tableDef.columns))
       titleRow={}
       for col in self.tableDef.columns:
           if(col.columnWidth != None):
               totalWidth += col.columnWidth
           else:
               totalWidth += avgWidth
           self.tabStops.append(totalWidth);
           titleRow[col.columnName] = col.columnTitle
       self.printTitle(titleRow)

   def clear(self):
       self.rows = []
       super().clearRows(self.rowstart);

   def column(self,columnId,columnName,width,isIndex=False):
       if(self.tableDef == None):
           self.tableDef = TableDef(self.panelName)
       self.tableDef.addColumn(ColumnDef(columnId,columnName,width),isIndex)
       return self;

   def columns(self,colArray):
       if(self.tableDef == None):
           self.tableDef = TableDef(self.panelName)
       for col in colArray:
           isIndex=None
           columnId = col[0]
           columnName = col[1]
           width= col[2]
           if(len(col) > 3):
               isIndex = col[3]
           self.tableDef.addColumn(ColumnDef(columnId,columnName,width),isIndex)
       return self;


   def printTitle(self,titleRow):
       i=0 
       print(UNDER_ON,end='\r')
       for key in titleRow:
           colIndex=self.tableDef.colMap[key]
           self.printAt(1,self.tabStops[colIndex],titleRow[key],self.hdrFgColor,self.hdrBgColor)
       print(NORMAL_VIDEO,end='\r')

   def printRow(self,rowData):
       indexValue = None
       if (self.tableDef.indexName != None):
           if(type(rowData[self.tableDef.indexName]) == dict):
               indexValue = rowData[self.tableDef.indexName]["value"]
           else:
               indexValue = str(rowData[self.tableDef.indexName])
       if (indexValue == None):
          rownum = self.rowstart+len(self.rows)
          self.rows.append(rowData)
       else:
          if (indexValue not in self.rowIndexMap):
              rownum = self.rowstart+len(self.rows)
              self.rowIndexMap[indexValue] = len(self.rows)
              self.rows.append(rowData)
          else:
              rownum = self.rowstart+self.rowIndexMap[indexValue]
       self.fillRow(self.top+rownum,self.bgColor)
       for key in rowData:
           colIndex=self.tableDef.colMap[key]
           fgColor = None
           bgColor = None
           if(type(rowData[key]) == dict):
               if("fgColor" in rowData[key]):
                   fgColor = rowData[key]["fgColor"]
               if("bgColor" in rowData[key]):
                   bgColor = rowData[key]["bgColor"]
               text = str(rowData[key]["value"]) 
           else:
               text = str(rowData[key])
           colwidth = (self.tableDef.columns[colIndex].columnWidth - 3)
           data = text[:colwidth] + '..' * (len(text) > colwidth)
           self.printAt(rownum,self.tabStops[colIndex],data,fgColor,bgColor)
           

class ConsoleUI:
    def __init__(self,bgColor=None):
        self.initscreen(bgColor)
        self.initEmoji()

    def setPanelHeaderColor(self,bgColor=None,fgColor=None):
        self.panelBGColor = bgColor
        self.panelFGColor = fgColor

    def initEmoji(self):
        self.emojiMap={}
        for e in emojilist:
           self.emojiMap[e[0]] = e[1]

    def getEmoji(self,name):
        if(name in self.emojiMap):
            return self.emojiMap[name]
        else:
            return name

    def getEmojiTuple(self,index):
        if(index >= len(emojilist)):
            index = len(emojilist)-1
        return emojilist[index]

    def setTitle(self,screenTitle,bgColor=None):
        if(screenTitle != None):
            MOVE(1,1) 
            bgColor="81"
            fgColor="88"
            if("bgColor" in screenTitle):
                bgColor=screenTitle["bgColor"]
            if("fgColor" in screenTitle):
                fgColor=screenTitle["fgColor"]
            bgColorCode=getBGColorCode(bgColor)[0]
            fgColorCode=getFGColorCode(fgColor)[0]
            fill = " "*cols
            print(f"{bgColorCode}",end='')
            print(f"{fill}",end='\r')
            tlen=len(screenTitle["title"])
            MOVE(1+round((cols-tlen)/2),1)
            print(f"{bgColorCode}{fgColorCode}{screenTitle['title']}",end='\r')

    def fillScreen(self,bgColor):
       i=1
       fill = " "*cols
       print(f"{bgColor}",end='')
       while(i<=rows):
           MOVE(1,i)
           print(f"{fill}",end='\r')
           i += 1

    def initscreen(self,bgColor=None):
       global rows,cols,screenColorCode
       self.panelBGColor = "lightgray"
       self.panelFGColor = "black"
       out = os.popen("stty -a | grep rows").read()
       arr = out.split(";")
       for line in arr:
          if (line.count("rows") > 0):
             rows=int(line.replace("rows","").replace(" ",""))
          if (line.count("columns") > 0):
             cols=int(line.replace("columns","").replace(" ",""))
       print(NORMAL_VIDEO)
       print(WIDE_SCREEN)
       print(CLEAR_SCREEN)
       print(CURSOR_OFF)
       if(bgColor != None):
           screenColorCode=getBGColorCode(bgColor)[0]
           self.fillScreen(screenColorCode)
       #print(UNDER_ON)

    def createPanel(self,panelName,panelTitle,panelRect,bgColor="white",fgColor="black"):
       panel = Panel(self,panelName,panelTitle,panelRect,bgColor,fgColor)
       panel.setConsole(self)
       panels[panelName] = panel
       return panel

    def createRollingPanel(self,panelName,panelTitle,panelRect,bgColor="white",fgColor="black"):
       return self.createPanel(panelName,panelTitle,panelRect,bgColor,fgColor)

    def createTablePanel(self,panelName,panelTitle,panelRect,bgColor="darkgray",fgColor="black",tableDef=None):
       if (tableDef == None):
           tableDef = TableDef(panelName)
       panel = TablePanel(self,panelName,panelTitle,panelRect,tableDef,bgColor,fgColor)
       panel.setConsole(self)
       panels[panelName] = panel
       return panel

    def createFGPalette(self):
       panel = self.createPanel("fgPalette","Text Color",PanelRect(1,1,rows-1,round(cols/2)),"231","black")
       i=0
       rnum=2
       cnum=5
       while (i<256):
          panel.printAt(rnum,cnum,"\033[1;4m"+str(i)+"\033[0m",str(i),"231")
          rnum += 2
          if(rnum >= rows-1):
              rnum=2
              cnum += 5
          i+=1

    def createBGPalette(self):
       panel = self.createPanel("bgPalette","Background Color",PanelRect(1,round(cols/2),rows-1,round(cols/2)),"231","black")
       i=0
       rnum=2
       cnum=5
       while (i<256):
          panel.printAt(rnum,cnum,str(i),"black","231")
          panel.printAt(rnum,cnum+4,"   ","black",str(i))
          rnum += 2
          if(rnum >= rows-1):
              rnum=2
              cnum += 10
          i+=1

    def createEmojiList(self):
       panel = self.createPanel("emoji","Emoji List",PanelRect(1,1,rows-1,cols),"white","black")
       emoji_width = 5
       total_cols = round(cols/emoji_width)-1
       total_rows = round(len(emojilist)/total_cols)
       i=0
       rstart=2
       cstart=1
       while (i<len(emojilist)):
          rnum = round(i/total_cols)
          cnum = i%total_cols
          text = emojilist[i][1].replace("U+","\\U000")
          panel.printAt(rstart+rnum,cstart+(cnum*emoji_width),text,"black","231")
          i+=1

    def rows(self):
       return rows

    def cols(self):
       return cols 


