__author__ = 'Jorge'

import Pyro4
import threading
import socket
from threading import Timer

TIMEOUT=10.0
PORT=3200

class Node(threading.Thread):
    """
    The Node Class
    """
    def __init__(self,Id,manager):
        """
        Constructor
        """
        super(Node,self).__init__()
        self.id=Id
        self.next=None
        self.previous=None
        self.pyroDaemon=Pyro4.Daemon(Pyro4.socketutil.getMyIpAddress())
        self.imInRing=False
        self.uri=None
        self.child=None
        self.childAdrr=None
        self.parent=None
        self.parentAdrr=None
        self.manager=manager
        self.timer=None
        self.daemon=True


    def GetId(self):
        """
        Get the ID of the Node.
        """
        print("GetId:{0}".format(self.id))
        return self.id

    def SetNext(self,next):
        """
        Set the Next Node in the chord.
        """
        print("SetNext")
        self.next=next

    def GetNext(self):
        """
        Get the Next Node in the chord.
        """
        print("GetNext")
        return self.next

    def SetPrevious(self,previous):
        """
        Set the Previous Node in the chord.
        """
        print("SetPrevious")
        self.previous=previous

    def GetPrevious(self):
        """
        Get the Previous Node in the chord.
        """
        print("GetPrevious")
        return self.previous

    def SetChildAddress(self,addr):
        self.childAdrr=addr

    def SetParentAddress(self,addr):
        self.parentAdrr=addr

    def SetChild(self,child):
        """
        Set the Child Node.
        """
        print("SetChild")
        if self.child is None:
            self.child=child
            self.childAdrr=self.child.GetIpAddress()
            self.child.SetNext(self.next)
            self.child.SetPrevious(self.previous)
            self.child.SetParentAddress(self.GetIpAddress())
            print("CHILD:{0}".format(self.child))
            return True
        else:return False

    def SetParent(self,parent):
        """
        Set the Parent Node.
        """
        print("SetParent")
        if self.parent is None:
            self.parent=parent
            self.parentAdrr=self.parent.GetIpAddress()
            self.next=self.parent.GetNext()
            self.previous=self.parent.GetPrevious()
            self.parent.SetChildAddress(self.GetIpAddress())
            return True
        else:return False

    def GetIpAddress(self):
        return Pyro4.socketutil.getMyIpAddress()

    def HasChild(self):
        return self.child is None

    def GetUri(self):
        return self.uri

    def ExternalSearch(self,path):
        """
        Search used for external Nodes to find something in my info.
        """
        if self.imInRing:
            return ["este","aquel","el otro"]#Ver Con Frank
        else: return []

    def LocalSearch(self,pattern, matchoption, child= False):
        return self.manager.search_result( pattern, matchoption)#fix this

    def Search(self, pattern, matchoption, amount= 400):
        result=[]
        child= True if not self.imInRing else False

        for item in self.LocalSearch(pattern,matchoption):
            result.append(item)
            if len(result)>=amount:
                yield result
                result=[]
        if child:
            for item in self.parent.LocalSearch(pattern,matchoption,child):
                result.append(item)
                if len(result)>=amount:
                    yield result
                    result=[]
        else:
            comparer= self.parent if child else self
            next= self.next
            while next is not comparer and next is not None:
                for item in next.LocalSearch(pattern,matchoption):
                    result.append(item)
                    if len(result)>=amount:
                        yield result
                        result=[]
                next=next.GetNext()
        yield result# por si te quedo algo o nunca llegaste al amount

    def SearchInRing(self,info,path):
        """
        Make a search
        """
        nextneig=self.next
        while nextneig!= None and nextneig._pyroUri != self.uri:
            info+=nextneig.ExternalSearch(path)
            nextneig=nextneig.GetNext()
        return info

    def SearchPosition(self,indexUri):
        """
        Search position in the ring of the chord.
        """
        index=Pyro4.Proxy(indexUri)
        nextIndex=index.GetNext()
        while True:
            if nextIndex == None:#Case 1: Only 2 Nodes in the ring
                index.SetNext(self)
                index.SetPrevious(self)
                self.next=index
                self.previous=index
                self.imInRing=True
                print("2 Nodes")
                break
            if index.GetId() < self.id and self.id < nextIndex.GetId():#Case 2: Find your position by id
                self.next=nextIndex
                self.previous=index
                index.SetNext(self)
                nextIndex.SetPrevious(self)
                self.imInRing=True
                print("Case 2")
                break
            if index.GetId() < self.id and self.id > nextIndex.GetId():#Case 3: At the end of the ring
                self.next=nextIndex
                self.previous=index
                index.SetNext(self)
                nextIndex.SetPrevious(self)
                self.imInRing=True
                print("Case 3")
                break

    def SearchForParent(self,uriRing):
        print("SearchForParent")
        helper=Pyro4.Proxy(uriRing)
        nextHelper=helper.GetNext()

        while True:
            if nextHelper is None:
                self.SearchPosition(uriRing)
                break
            if not nextHelper.HasChild():
                if nextHelper.SetChild(self):
                    self.parent=nextHelper
            #if nextHelper.GetId() == self.id:#mojon
            #    self.SearchPosition(uriRing)
            #    break
            nextHelper=nextHelper.GetNext()

    #self.connect.parent.TakeChanges(list)
    def TakeChanges(self,list):
        self.manager.UpdateFromChild(list)

    def GetDataToMyParent(self,data):
        if self.parent is not None:
            self.parent.TakeInitialData(data)

    def TakeInitialData(self,data):
        self.manager.TakeInitialData(data)#implementation

    def CallForParent(self):
        if self.parentAdrr is not None:
            print("CallForParent")
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg="Are you there?"
            sock_out.sendto(msg.encode(), (str(self.parentAdrr), int(input("advice port:"))))
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_out.bind((str(self.parentAdrr),int(input("listen port:"))))
            self.timer=Timer(5.0,self.print_death)
            self.timer.start()
            (msg, address) = sock_out.recvfrom(65536)
            self.timer.cancel()
            if msg.decode() == "YES":
               return True

    def CallForChild(self):
        if self.childAdrr is not None:
            print("CallForChild")
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg="Are you there?"
            sock_out.sendto(msg.encode(), (str(self.childAdrr), int(input("advice port:"))))
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_out.bind((str(self.childAdrr),int(input("listen port:"))))
            self.timer=Timer(5.0,self.print_death)
            self.timer.start()
            (msg, address) = sock_out.recvfrom(65536)
            self.timer.cancel()
            if msg.decode() == "YES":
                return True

    def CallMe(self):
        if not self.imInRing:
            self.CallForParent()
        else:
            self.CallForChild()

    def print_death(self):
        print("some death")

    def SayHello(self):
        """
        Send a broadcast message to search parent or enter in the ring and listen for messages.
        """
        sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = "hello"
        port = 3100
        sock_out.sendto(msg.encode(), ("255.255.255.255", int(input("hello port:"))))

    def ImListen(self):
        """
        Listen for Broadcast messages.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0",int(input("listen port:"))))
        #s.bind(("0.0.0.0",PORT))
        t=None
        while True:
            print("RESUME:")
            print("\nparent:{}\nchild:{}\nInRIng:{}".format(self.parent,self.child,self.imInRing))


            if not self.imInRing and self.parent == None:
                t=Timer(TIMEOUT,self.ImTheOne)
                t.start()
            (msg, address) = s.recvfrom(65536)
            #if not self.imInRing:
            if t != None:
                t.cancel()

            print("tengo info {0}".format(address))
            sms=msg.decode()

            print("MSG:{0}".format(sms))
            if sms == str(self.uri):#evitando escuchar mis propios msg.
                continue
            elif sms == "Are you there?":
                sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg="YES"
                print(msg)
                sock_out.sendto(msg.encode(), (address[0], int(input("answer port:"))))
                print("child response send!!!.")
            elif sms=="hello": #and self.imInRing:
                sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                if self.imInRing:
                    if self.child == None:
                        msg = str(self.uri)
                    else:
                        msg="Full House.{0}".format(self.uri)
                    print(msg)
                    sock_out.sendto(msg.encode(), (address[0], int(input("send port:"))))
                    print("info send!!!.")
                else:
                    if self.parent is None:
                        continue
                    msg="Full House.{0}".format(self.parent.GetUri())
                    print(msg)
                    sock_out.sendto(msg.encode(), (address[0], int(input("send port:"))))
                    print("info send!!!.")


            elif str(sms).__contains__("Full House") and not self.imInRing:
                substr=str(sms)#implementar logica de esperar mas respuestas por posibles anfitriones
                sim=str(substr[11:])
                print("URI FULL HOUSE:{0}".format(sim))
                #entrar al anillo y buscar quien no tenga hijos.
                self.SearchForParent(sim)
            elif str(sms).__contains__("PYRO") and not self.imInRing:# and  (not self.imInRing):
                if self.parent == None:
                    self.parent=Pyro4.Proxy(sms)
                    if self.parent.SetChild(self):
                        continue
                    else:self.parent=None





    def ImTheOne(self):
        """
        Invoke this method when no receive answer of any node.
        """
        print("Im in ring")
        self.imInRing=True

    def dale(self):
        """
        to make pruebas
        """
        self.run()

    def VerifyParent(self):
        self.CallMe()
        #print("Verifiying")
        Timer(3.0,self.VerifyParent).start()

    def run(self):
        """
        The run method.
        """
        print("run")
        t=threading.Thread(target=self.pyroDaemon.requestLoop)
        t.daemon=True
        t.start()
        self.uri=self.pyroDaemon.register(self,self.id)
        print(self.uri)
        Timer(3.0,self.VerifyParent).start()

        self.SayHello()
        self.ImListen()
        # t=threading.Thread(target=self.SayHello)
        # t.start()
        #self.pyroDaemon.requestLoop()


