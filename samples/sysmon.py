import time
import psutil
from pyclap.pyclap import ConsoleUI,PanelRect
from datetime import datetime

topProcessCount=20
cpuUsagePanel=None
memUsagePanel=None
cpuStatsPanel=None
memStatsPanel=None
netStatsPanel=None
diskStatsPanel=None
rollingLogPanel=None

def getListOfProcessSortedByCpuMemory():
    '''
    Get list of running process sorted by Memory Usage
    '''
    listOfProcObjects = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           # Fetch process details as dict
           pinfo = proc.as_dict(attrs=['pid', 'name', 'username','cpu_percent','status'])
           pinfo['threads'] = proc.num_threads()
           pinfo['fds'] = proc.num_fds()
           pinfo['ppid'] = proc.ppid()
           pinfo['mem'] = proc.memory_percent()
           pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
           pinfo['rss'] = proc.memory_info().rss / (1024 * 1024)
           # Append dict to list
           listOfProcObjects.append(pinfo);
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
    # Sort list of dict by key vms i.e. memory usage
    memListSorted = sorted(listOfProcObjects, key=lambda procObj: procObj['mem'], reverse=True)
    memList = memListSorted[:topProcessCount]
    cpuListSorted = sorted(listOfProcObjects, key=lambda procObj: procObj['cpu_percent'], reverse=True)
    cpuList = cpuListSorted[:topProcessCount]

    return {"mem":memList,"cpu":cpuList}

def initDisplay():
   global cpuUsagePanel,memUsagePanel,cpuStatsPanel,memStatsPanel,netStatsPanel,diskStatsPanel,rollingLogPanel
   screen = ConsoleUI(bgColor="green")
   screen.setTitle({"title":f"System Monitor {screen.getEmoji('smiling face with smiling eyes')}"})
   screen.setPanelHeaderColor(bgColor="153",fgColor="black")
   margin=3
   startRow=3
   halfScreenWidth = int((screen.cols() - 3*margin)/2)
   quarterScreenWidth = int((screen.cols() - 5*margin)/4)

   cpuUsagePanelPos = PanelRect(startRow,margin,3+topProcessCount,halfScreenWidth)
   cpuUsagePanel = screen.createTablePanel("cpuUsagePanel",f"CPU Usage (Top {topProcessCount} processes)",cpuUsagePanelPos,"38","white")
   cpuUsagePanel.column("pid","PID",10) \
           .column("cpu","CPU %",10) \
           .column("threads","Threads",10)\
           .column("ppid","PPID",8)\
           .column("fds","Open Handles",15)\
           .column("name","Process",40)\
           .headerColors("red")\
           .render()
   cpuUsagePanel.titleIcon(f"{screen.getEmoji('chart decreasing')}")

   memUsagePanelPos = PanelRect(startRow,2*margin+halfScreenWidth,3+topProcessCount,halfScreenWidth)
   memUsagePanel = screen.createTablePanel("memUsagePanel",f"Memory Usage (Top {topProcessCount} processes)",memUsagePanelPos,"38","white")
   memUsagePanel.columns([
                           ["pid","PID",10],
                           ["mem","MEM %",10],
                           ["vms","Virtual Memory",20],
                           ["rss","RSS(Resident Set Size)",30],
                           ["name","Process",40],
                       ]).headerColors("blue").render()
   memUsagePanel.titleIcon(f"{screen.getEmoji('chart decreasing')}")

   memStatsPanelPos = PanelRect(cpuUsagePanel.bottom()+1,margin,10,quarterScreenWidth)
   memStatsPanel = screen.createTablePanel("memStatsPanel","Memory Stats",memStatsPanelPos,"white","black")
   memStatsPanel.columns([
                      ["type","Type",20,True],["value","Value",20]
                  ]).render()
   memStatsPanel.titleIcon(f"{screen.getEmoji('open book')}",bgColor="yellow")

   adjustedWidth = cpuUsagePanel.right()-(2*margin+quarterScreenWidth)
   cpuStatsPanelPos = PanelRect(cpuUsagePanel.bottom()+1,2*margin+quarterScreenWidth,10,adjustedWidth)
   cpuStatsPanel = screen.createTablePanel("cpuStatsPanel","CPU Stats",cpuStatsPanelPos,"white","black")
   cpuStatsPanel.columns([
                      ["stat","Stat",20,True],["value","Value",20]
                  ]).render()
   cpuStatsPanel.render()
   cpuStatsPanel.titleIcon(f"{screen.getEmoji('blue book')}")

   netStatsPanelPos = PanelRect(cpuStatsPanel.bottom()+1,margin,10,quarterScreenWidth)
   netStatsPanel = screen.createTablePanel("netStatsPanel","Network Stats",netStatsPanelPos,"yellow","blue")
   netStatsPanel.columns([
                      ["stat","Stat",30,True],["value","Value",20]
                  ]).render()
   netStatsPanel.render()
   netStatsPanel.titleIcon(f"{screen.getEmoji('closed book')}")

   diskStatsPanelPos = PanelRect(cpuStatsPanel.bottom()+1,2*margin+quarterScreenWidth,10,adjustedWidth)
   diskStatsPanel = screen.createTablePanel("diskStatsPanel","Disk Stats",diskStatsPanelPos,"yellow","blue")
   diskStatsPanel.columns([
                      ["folder","Folder",35,True],["size","Capacity",10],["usage","Used",10]
                  ]).render()
   diskStatsPanel.render()
   diskStatsPanel.titleIcon(f"{screen.getEmoji('orange book')}")

   adjustedHeight = diskStatsPanel.bottom()-(memUsagePanel.bottom()+1)
   rollingLogPanelPos = PanelRect(memUsagePanel.bottom()+1,2*margin+halfScreenWidth,adjustedHeight,halfScreenWidth)
   rollingLogPanel= screen.createRollingPanel("logPanel","Log",rollingLogPanelPos,"128","white")
   rollingLogPanel.titleIcon(f"{screen.getEmoji('scroll')}")

def updateStats():
       global cpuUsagePanel,memUsagePanel,cpuStatsPanel,memStatsPanel,netStatsPanel,diskStatsPanel
       metrics = getListOfProcessSortedByCpuMemory()
       vmMetrics = psutil.virtual_memory()
       cpuCount = psutil.cpu_count()
       cpuUsagePanel.clear();
       memUsagePanel.clear();
       for cpu in metrics["cpu"]:
           cpuUsagePanel.printRow({
               "name":f"{cpu['name']}",
               "pid" :f"{cpu['pid']}",
               "threads":f"{cpu['threads']}",
               "ppid":f"{cpu['ppid']}",
               "fds":f"{cpu['fds']}",
               "cpu":f"{cpu['cpu_percent']}"
           })
       for mem in metrics["mem"]:
           memUsagePanel.printRow({
               "name":f"{mem['name']}",
               "pid":f"{mem['pid']}",
               "vms":f"{round(mem['vms'])} MB",
               "mem":f"{round(mem['mem'],2)}",
               "rss":f"{round(mem['rss'],2)} MB",
           })
       memStatsPanel.printRow({"type":f"Total",
           "value":{"value":f"{round(vmMetrics.total/(1024*1024))} MB","fgColor":"blue","bgColor":"white"}
       })
       memStatsPanel.printRow({"type":"Available","value":f"{round(vmMetrics.available/(1024*1024))} MB"})
       memStatsPanel.printRow({"type":"Used","value":f"{round(vmMetrics.used/(1024*1024))} MB"})
       memStatsPanel.printRow({"type":"Free","value":f"{round(vmMetrics.free/(1024*1024))} MB"})
       if(vmMetrics.wired != None):
           memStatsPanel.printRow({"type":"Wired","value":f"{round(vmMetrics.wired/(1024*1024))} MB"})

       cpuUsage = psutil.cpu_percent()
       loadAvg = psutil.getloadavg()
       pcount = len(psutil.pids())
       cpuStatsPanel.printRow({"stat":"CPU Usage","value":f"{round(cpuUsage,2)} %"})
       cpuStatsPanel.printRow({"stat":"Idle ","value":f"{100-round(cpuUsage,2)} %"})
       cpuStatsPanel.printRow({"stat":"CPU Count","value":f"{cpuCount}"})
       cpuStatsPanel.printRow({"stat":"Load Average","value":f"{round(loadAvg[0],2)},{round(loadAvg[1],2)},{round(loadAvg[2],2)}"})
       cpuStatsPanel.printRow({"stat":"Processes","value":f"{pcount}"})
       netMetrics = psutil.net_io_counters()
       netStatsPanel.printRow({"stat":"Bytes Sent","value":f"{round(netMetrics.bytes_sent/(1024*1024),2)} MB"})
       netStatsPanel.printRow({"stat":"Bytes Received","value":f"{round(netMetrics.bytes_recv/(1024*1024),2)} MB"})
       netStatsPanel.printRow({"stat":"Packets Sent","value":f"{netMetrics.packets_sent}"})
       netStatsPanel.printRow({"stat":"Packets Received","value":f"{netMetrics.packets_recv}"})
       netStatsPanel.printRow({"stat":"Errors Outgoing","value":f"{netMetrics.errout}"})
       netStatsPanel.printRow({"stat":"Errors Incoming","value":f"{netMetrics.errin}"})
       netStatsPanel.printRow({"stat":"Dropped Packets Out","value":f"{netMetrics.dropout}"})
       netStatsPanel.printRow({"stat":"Dropped Packets In","value":f"{netMetrics.dropin}"})
       diskStats = psutil.disk_partitions()
       for d in diskStats:
           diskUsage = psutil.disk_usage(d.mountpoint)
           diskStatsPanel.printRow({"folder":f"{d.mountpoint}","size":f"{round(diskUsage.total/(1024*1024*1024))} GB","usage":f"{round(diskUsage.percent,2)} %"})
       now = datetime.now()
       rollingLogPanel.append(f"{now.strftime('%H:%M:%S')} cpu:{round(cpuUsage,2)} % available mem:{round(vmMetrics.available/(1024*1024))} MB processes:{pcount}")

def main():
   initDisplay()
   getListOfProcessSortedByCpuMemory()
   psutil.cpu_percent()
   while(True):
       time.sleep(5)
       updateStats()

main()
