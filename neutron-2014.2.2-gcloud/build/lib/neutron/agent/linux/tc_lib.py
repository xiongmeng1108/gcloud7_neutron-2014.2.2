__author__ = 'luoyb'
import socket
from binascii import hexlify
from binascii import  unhexlify
from neutron.agent.linux import utils
import time
class TC_Operation:
    def __init__(self):
          self.root_helper="sudo  neutron-rootwrap /etc/neutron/rootwrap.conf"
    def add_root_and_class(self,nsname=None,devname=None):
        """
        add root qdisc and root class,first class 100 mbit,root class 1:1
        """

        is_exist=self.check_qdisc(nsname,devname,"htb 1:")
        #print is_exist
        cmd=[]
        nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        if is_exist == -1:
           cmd.extend(["tc","qdisc","add","dev",devname,"root","handle","1:","htb"])
           #print(cmd)
           rc=utils.execute(cmd,self.root_helper)
           #print("result:"+rc)
        #add  root class
        self.add_or_update_class(nsname,devname,"1:","1:1","100mbit","100mbit")


    def add_or_update_class(self,nsname=None,devname=None,parent_classid=None,curent_classid=None,rate=None,ceil=None ):
        """
        add or update class  qos  bandwidth
        """
        cmd=[]
        nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        is_exist=self.check_class(nsname,devname,"class htb "+curent_classid)
        #print "add_class"
        #print is_exist
        if is_exist == -1:
           cmd.extend(["tc","class","add","dev",devname,"parent",parent_classid,"classid",curent_classid,"htb","rate",rate,"ceil",ceil])
           utils.execute(cmd,self.root_helper)
           return 0
        else:
           cmd.extend(["tc","class","replace","dev",devname,"parent",parent_classid,"classid",curent_classid,"htb","rate",rate,"ceil",ceil])
           utils.execute(cmd,self.root_helper)

    def add_leaf(self,nsname=None,devname=None,curent_classid=None ):
        """
        add qdisc info ,add_leaf
        """
        cmd=[]
        nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
        cmd.extend(nscmd)
        cmd.extend(["tc","qdisc","add","dev",devname,"parent",curent_classid,"sfq","perturb","10"])
        utils.execute(cmd,self.root_helper)
    def add_flow(self,nsname=None,devname=None,parentid=None,src_ip=None,classid=None):
        #ip netns exec qrouter-b90a765b-d4ee-4ca9-aee8-79387537a3a7
        #tc filter add  dev qg-fca39d8c-1a protocol ip parent 1: u32 match ip src  20.251.36.102 flowid 1:10
        cmd=[]
        nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        check_rc= self.check_flow(nsname,devname,classid,src_ip)
        if check_rc==-1:
             #print "add new flow"
             cmd.extend(["tc","filter","add","dev",devname,"protocol","ip","parent",parentid,"u32","match","ip","src",src_ip,"flowid",classid])
             utils.execute(cmd,self.root_helper)
        elif check_rc == -2:
             #print "delete old flow"
             self.del_flow(nsname,devname,classid)
             cmd.extend(["tc","filter","add","dev",devname,"protocol","ip","parent",parentid,"u32","match","ip","src",src_ip,"flowid",classid])
             utils.execute(cmd,self.root_helper)
             #print "add new flow"

    def _get_flow_grep_src(self,src_ip):
        hexstr=hexlify(socket.inet_aton(src_ip))+"/ffffffff"

        #print hexstr
        return hexstr

    def check_qdisc(self,nsname=None,devname=None,grep_src=None):
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        cmd.extend(["tc","qdisc","show","dev",devname])
        output=utils.execute(cmd,self.root_helper)
        if output:
                return output.find(grep_src)
        return -1

    def check_class(self,nsname=None,devname=None,grep_src=None):
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        cmd.extend(["tc","class","show","dev",devname])
        output=utils.execute(cmd,self.root_helper)
        if output:
                return output.find(grep_src)
        return -1

    def check_flow(self,nsname=None,devname=None,classid=None,src_ip=None):
        """
        return 0 is the same
        return -2 is :the src_ip is not the same
        return -1:is not found
        """
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        cmd.extend(["tc","filter","show","dev",devname])
        output=utils.execute(cmd,self.root_helper)
        grep_src="flowid "+classid
        ##print output
        if output:
             if output.find(grep_src)==-1:
                return -1
        next=0
        for line in output.split('\n'):
             if next==1:
                 if line.find(self._get_flow_grep_src(src_ip))==-1:
                     return -2
                 else:
                     return  0
             if line.find("flowid "+classid) != -1:
                 next=1
        return -1

    def del_flow(self,nsname = None,devname=None, classid=None):
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        cmd.extend(["tc","filter","show","dev",devname])
        output=utils.execute(cmd,self.root_helper)
        #print output
        grep_src="flowid "+classid
        match_line=None
        for line in output.split('\n'):
             if line.find(grep_src) != -1:
                match_line=line
                break

        del_cmd=nscmd
        if match_line is not None:
            index=match_line.find("u32")+len("u32")
            rule_set=match_line[len("filter "):index].split(" ")
            del_cmd.extend(["tc","filter","del","dev",devname])
            del_cmd.extend(rule_set)
            #print rule_set
            output=utils.execute(del_cmd,self.root_helper)

    def del_class(self,nsname,devname,classid):
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        if self.check_class(nsname,devname,"class htb "+classid)==-1:
            return
        cmd.extend(["tc","class","del","dev",devname,"classid",classid])
        output=utils.execute(cmd,self.root_helper)

    def del_flow_and_class(self,nsname = None,devname=None, classid=None):
        self.del_flow(nsname,devname,classid)
        self.del_class(nsname,devname,classid)
    def add_class_and_flow(self,nsname = None,devname=None, classid=None,max_rate=None,src_ip=None):
        self.add_root_and_class(nsname,devname)
        rc=self.add_or_update_class(nsname,devname,"1:1",classid,max_rate,max_rate)
        if rc==0:
            self.add_leaf(nsname,devname,classid)
        self.add_flow(nsname,devname,"1:",src_ip,classid)
    def get_class_and_flow(self,nsname,devname,min_classid,max_classid):
        cmd=nscmd=[]
        if nsname is not None:
            nscmd=["ip","netns","exec",nsname]
            cmd.extend(nscmd)
        cmd.extend(["tc","filter","show","dev",devname])
        output=utils.execute(cmd,self.root_helper)
        ##print output
        match_line=None
        grep_flow_src="flowid 1:"
        qoss=[]
        qos={}
        class_line=ip_line=line_index=0
        for line in output.split('\n'):
             class_index= line.find(grep_flow_src)
             if class_index!= -1 and  line.find("protocol ip") !=-1 and line.find("u32 ") !=-1 :
                #get class_id
                classid_str=line[class_index+len(grep_flow_src):]
                ##print classid_str
                sub_class_id=int(classid_str)
                #print sub_class_id
                if sub_class_id>=min_classid and sub_class_id<=max_classid:
                    qos["class_id"]=sub_class_id
                    class_line=line_index
                    ##print qos
             elif line_index-class_line==1:
                #print "line"+line
                ip_index=line.find("match ")
                ip_end_index=line.find("/ffffffff")
                if ip_index!=-1 and ip_end_index>ip_index:
                    hen16_ip=line[ip_index+len("match "):ip_end_index]
                    src_ip= socket.inet_ntoa(unhexlify(hen16_ip))
                    ##print src_ip
                    qos["src_ip"]=src_ip
                    qoss.append(qos)
                qos={}
             line_index=line_index+1
        return qoss


if __name__ == '__main__':
    tc_operation=TC_Operation()
    nsname="qrouter-2c93bb39-7a0f-4539-8206-c395df034374"
    devname="qg-73023b4f-8b"
    #tc_operation.del_flow_and_class(nsname,'qg-73023b4f-8b','1:10')
   # tc_operation.check_qdisc(nsname,devname,"htb 1:")
   # tc_operation.add_root_and_class(nsname,devname)
   # tc_operation.add_or_update_class(nsname,devname,"1:1","1:10","20mbit","20mbit")
   # tc_operation.add_flow(nsname,devname,"1:","20.251.36.102","1:10")
   # #print tc_operation.check_flow(nsname,devname,"1:10","20.251.36.102")
   ##def del_flow(self,nsname = None,devname=None, classid=None):
    #qoss=tc_operation.get_class_and_flow(nsname,devname,10,20)
    #for qos in qoss:
     #   print ("%r"%(qos))
    tc_operation.del_flow_and_class(nsname,devname,"1:10")
    tc_operation.add_class_and_flow(nsname,devname,"1:10","100mbit","20.251.36.104")
