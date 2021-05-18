import subprocess
import json
import time
from pyclap.pyclap import ConsoleUI,PanelRect
from datetime import datetime
from optparse import OptionParser

screen=None
margin=3
startRow=3
containerProcessPanel=None
containerProcessTextPanel=None
procdata={}
cntrdata={}

def initDisplay(title,icon):
   global screen
   screen = ConsoleUI(bgColor="186")
   screen.setTitle({"title":f"{title} {screen.getEmoji(icon)}"})
   screen.setPanelHeaderColor(bgColor="153")

def getProcessArguments(podName):
    global containerProcessTextPanel,cntrdata
    text=""
    for container in cntrdata:
        text += f"Container:{container}\n"
        for pid in cntrdata[container]["pids"]:
           args =  ['kubectl','exec',podName,'-c',container,'--','cat']
           args.append(f"/proc/{pid}/cmdline")
           outstr = subprocess.check_output(args)
           outstr = str(outstr).replace("b'","").replace("\\x00"," ").replace("\\n","\n").replace(" '","")
           text += f"   PID:{pid}  CMD:{outstr}\n"
           text += "\n"
        text += " \n"
    containerProcessTextPanel.printText(text)

def getProcessDetails(podName,containerName):
    global containerProcessPanel,procdata,cntrdata
    outstr = subprocess.check_output(['kubectl','exec',podName,'-c',containerName,'--','ls','-m', '/proc'])
    entries = str(outstr).replace("b'","").split(",")
    pids=[]

    for entry in entries:
        pid= entry.replace(" ","")
        if(pid.isnumeric()):
            try:
               prockey=f"{containerName}-{pid}"
               outstr = subprocess.check_output(['kubectl','exec',podName,'-c',containerName,'--','cat',f"/proc/{pid}/stat","/proc/stat"],stderr=subprocess.DEVNULL)
               outstr = str(outstr).replace("b'","").replace("\\x00"," ").replace("\\n","\n")
               lines = str(outstr).splitlines()
               outstr = lines[0].replace("b'","").replace("\\x00"," ")
               fields = outstr.split(" ")
               utime = int(fields[13])
               stime = int(fields[14])

               total_jiffies = 0
               for line in lines:
                  if(line.startswith("cpu ")):
                     entries = line.split(" ")
                     for entry in entries:
                         jiffy=entry.replace(" ","")
                         if(jiffy.isnumeric()):
                             total_jiffies += int(jiffy)
               user_util=0
               sys_util=0
               sno=len(procdata.keys())
               if(prockey in procdata):
                   user_util = round(100*(utime-procdata[prockey]["utime"])/(total_jiffies-procdata[prockey]["total_jiffies"]),2)
                   sys_util = round(100*(stime-procdata[prockey]["stime"])/(total_jiffies-procdata[prockey]["total_jiffies"]),2) 
                   sno = procdata[prockey]["sno"]

               procdata[prockey] = {"sno":sno,"program":fields[1],"ppid":fields[3],"vsize":round(int(fields[22])/(1024*1024)),"threads":fields[19],
                                    "rss":round((int(fields[23])*4096)/(1024*1024)),"state":fields[2],"utime":utime,"stime":stime,"total_jiffies":total_jiffies,
                                    "user_util":user_util,"sys_util":sys_util
                                   }
               pinfo = procdata[prockey]
               containerProcessPanel.printRow({"sno":sno,"container":containerName,"pid":pid,"ppid":pinfo["ppid"],"vsize":f"{pinfo['vsize']} MB","rss":f"{pinfo['rss']} MB",
                                                "program":pinfo["program"],"state":pinfo["state"],"threads":pinfo["threads"],
                                                "user":user_util,"sys":sys_util,"cpu":user_util+sys_util,
                                              })
               pids.append(pid)
            except:
               dummy=1
    if(containerName not in cntrdata):
        cntrdata[containerName] = {"pids":pids}

def showPodInfo(pod,podName):
    global containerProcessPanel,containerProcessTextPanel
    initDisplay("Pod Viewer","magnifying glass tilted left")
    halfScreenWidth = int((screen.cols() - 3*margin)/2)
    triadScreenWidth = int((screen.cols() - 4*margin)/3)
    halfScreenHeight = int((screen.rows() - 3*margin)/2)
    podInfoPanelPos = PanelRect(startRow,margin,12,triadScreenWidth)
    podInfoPanel = screen.createTablePanel("podInfoPanel",f"Pod Info",podInfoPanelPos,"194","black")
    podInfoPanel.columns([
                           ["param","Parameter",20],
                           ["value","Value",50],
                       ]).render()
    podInfoPanel.titleIcon(f"{screen.getEmoji('light bulb')}")
    podInfoPanel.printRow({"param":f"Pod Name","value":pod["metadata"]["name"]});
    podInfoPanel.printRow({"param":f"Namespace","value":pod["metadata"]["namespace"]});
    podInfoPanel.printRow({"param":f"UID","value":pod["metadata"]["uid"]});
    podInfoPanel.printRow({"param":f"Node Name","value":pod["spec"]["nodeName"]});
    podInfoPanel.printRow({"param":f"Restart Policy","value":pod["spec"]["restartPolicy"]});
    podInfoPanel.printRow({"param":f"DNS Policy","value":pod["spec"]["dnsPolicy"]});
    podInfoPanel.printRow({"param":f"Containers","value":len(pod["spec"]["containers"])});
    podInfoPanel.printRow({"param":f"Init Containers","value":len(pod["spec"]["initContainers"])});
    podInfoPanel.printRow({"param":f"Phase","value":pod["status"]["phase"]});
    podInfoPanel.printRow({"param":f"Pod IP","value":pod["status"]["podIP"]});

    containerInfoPanelPos = PanelRect(startRow,podInfoPanel.right()+margin,5,2*triadScreenWidth+margin)
    containerInfoPanel = screen.createTablePanel("containerInfoPanel",f"Containers",containerInfoPanelPos,"194","black")
    containerInfoPanel.columns([
                           ["name","Name",20],
                           ["id","ID",15],
                           ["started","Started?",9],
                           ["ready","Ready?",9],
                           ["state","State",12],
                           ["restarts","Restarts",10],
                           ["image","Image",35],
                           ["imagepolicy","Pull Policy",15],
                       ]).render()
    containerInfoPanel.titleIcon(f"{screen.getEmoji('whale')}",bgColor="229")
    for cntr in pod["spec"]["containers"]:
        imagename=cntr['name']
        cntrstatus=None
        for cstatus in pod["status"]["containerStatuses"]:
            if(cstatus["name"] == imagename):
                cntrstatus=cstatus
        imagearr=cntr['image'].split("/")
        cid=""
        started="?"
        ready="?"
        state="?"
        restarts=0
        if(cntrstatus != None):
            cid = cntrstatus["containerID"].replace("containerd://","").replace("docker://","")[:12]
            started=cntrstatus["started"]
            ready=cntrstatus["ready"]
            for s in cntrstatus["state"]:
                state=s
            restarts=cntrstatus["restartCount"]

        containerInfoPanel.printRow({"name":f"{cntr['name']}","id":cid,"started":started,"ready":ready,"state":state,"restarts":restarts,
                                     "image":f"{imagearr[len(imagearr)-1]}","imagepolicy":f"{cntr['imagePullPolicy']}"});

    initContainerInfoPanelPos = PanelRect(containerInfoPanel.bottom()+1,podInfoPanel.right()+margin,5,2*triadScreenWidth+margin)
    initContainerInfoPanel = screen.createTablePanel("initContainerInfoPanel",f"Init Containers",initContainerInfoPanelPos,"194","black")
    initContainerInfoPanel.columns([
                           ["name","Name",20],
                           ["image","Image",35],
                           ["imagepolicy","Pull Policy",15],
                       ]).render()
    initContainerInfoPanel.titleIcon(f"{screen.getEmoji('spouting whale')}",bgColor="229")
    for cntr in pod["spec"]["initContainers"]:
        imagearr=cntr['image'].split("/")
        initContainerInfoPanel.printRow({"name":f"{cntr['name']}","image":f"{imagearr[len(imagearr)-1]}","imagepolicy":f"{cntr['imagePullPolicy']}"});

    #containerProcessPanelPos = PanelRect(initContainerInfoPanel.bottom()+1,podInfoPanel.right()+margin,screen.rows()-initContainerInfoPanel.bottom()-margin,2*triadScreenWidth+margin)
    containerProcessPanelPos = PanelRect(initContainerInfoPanel.bottom()+1,podInfoPanel.right()+margin,10,2*triadScreenWidth+margin)
    containerProcessPanel = screen.createTablePanel("Container Processes",f"Container Processes",containerProcessPanelPos ,"194","black")
    containerProcessPanel.columns([
                           ["sno","S.No",5,True],
                           ["container","Container",20],
                           ["pid","PID",10],
                           ["ppid","PPID",10],
                           ["program","Program Name",20],
                           ["state","State",7],
                           ["threads","Threads",8],
                           ["vsize","VSize",12],
                           ["rss","RSS",12],
                           ["cpu","CPU %",8],
                           ["user","USER %",8],
                           ["sys","SYS %",8],
                       ]).render()
    containerProcessPanel.titleIcon(f"{screen.getEmoji('rocket')}")

    containerProcessTextPanelPos = PanelRect(containerProcessPanel.bottom()+1,podInfoPanel.right()+margin,screen.rows()-containerProcessPanel.bottom()-margin,2*triadScreenWidth+margin)
    containerProcessTextPanel = screen.createPanel("processArgs",f"Process Args",containerProcessTextPanelPos,"194","black")
    containerProcessTextPanel.titleIcon(f"{screen.getEmoji('red circle')}")

    status_length = len(pod["status"]["conditions"])
    podStatusPanelPos = PanelRect(podInfoPanel.bottom()+1,margin,status_length+2,triadScreenWidth)
    podStatusPanel = screen.createTablePanel("podStatusPanel",f"Pod Events",podStatusPanelPos,"194","black")
    podStatusPanel.columns([
                           ["type","Type",20],
                           ["status","Status",10],
                           ["time","Time",25],
                       ]).render()
    podStatusPanel.titleIcon(f"{screen.getEmoji('spiral calendar')}")
    for cond in pod["status"]["conditions"]:
        cond["dtime"] = datetime.strptime(cond["lastTransitionTime"],"%Y-%m-%dT%H:%M:%SZ")
    pod["status"]["conditions"].sort(key=lambda cond:(cond["dtime"],cond["type"]))
    for cond in pod["status"]["conditions"]:
        podStatusPanel.printRow({"type":cond["type"],"status":cond["status"],"time":cond["dtime"]});

    volume_count = len(pod["spec"]["volumes"])
    volumePanelPos = PanelRect(podStatusPanel.bottom()+1,margin,volume_count+2,triadScreenWidth)
    volumePanel = screen.createTablePanel("volumePanel",f"Volumes",volumePanelPos,"194","black")
    volumePanel.columns([
                           ["name","Volume Name",40],
                       ]).render()
    volumePanel.titleIcon(f"{screen.getEmoji('optical disk')}")
    for volume in pod["spec"]["volumes"]:
        volumePanel.printRow({"name":volume["name"]})

    label_count= len(pod["metadata"]["labels"].keys())
    labelPanelPos = PanelRect(volumePanel.bottom()+1,margin,label_count+2,triadScreenWidth)
    labelPanel = screen.createTablePanel("labelPanel",f"Labels",labelPanelPos,"194","black")
    labelPanel.columns([
                           ["label","Label",40],
                           ["value","Value",30],
                       ]).render()
    labelPanel.titleIcon(f"{screen.getEmoji('label')}")
    for label in pod["metadata"]["labels"]:
        labelPanel.printRow({"label":label,"value":pod["metadata"]["labels"][label]})

    for cntr in pod["spec"]["containers"]:
        getProcessDetails(podName,cntr['name'])
    getProcessArguments(podName)
    while(True):
        time.sleep(5)
        for cntr in pod["spec"]["containers"]:
            getProcessDetails(podName,cntr['name'])
       

def handleGet(options,args):
    if(args[1] == "pod" and len(args) == 3):
        pod_name = args[2]
        obj = json.loads(subprocess.check_output(['kubectl','get','-o','json','pod',pod_name]))
        showPodInfo(obj,pod_name)
        #print(json.dumps(obj["spec"]["containers"],indent=4))

def handleDescribe(options,args):
    print(options)

def handleExplain(options,args):
    print(options)
    
def main():
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output_file", default="test.csv",help="output file")
    parser.add_option("-s", "--settings", dest="settings_file", default="settings.json",help="settings file")
    (options, args) = parser.parse_args()
    if(args[0] == "get"): 
        handleGet(options, args)
    elif(args[0] == "describe"):
        handleDescribe(options, args)
    elif(args[0] == "explain"):
        handleExplain(options, args)


main()
