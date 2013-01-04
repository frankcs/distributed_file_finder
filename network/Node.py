__author__ = 'Jorge'

import Pyro4
import threading
import socket
from threading import Timer
import random
import time

TIMEOUT=5.0
PORT=3200
ANSWERPORT=3201

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
        self.myIp=Pyro4.socketutil.getMyIpAddress()
        self.pyroDaemon=Pyro4.Daemon(self.myIp)
        self.imInRing=False
        self.uri=None
        self.child=None
        self.childAdrr=None
        self.parent=None
        self.parentAdrr=None
        self.manager=manager
        self.timer=None
        self.daemon=True
        self.fail=False
        self.mySocket=None


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
        print("SetChildAddress")
        self.childAdrr=addr

    def SetParentAddress(self,addr):
        print("SetParentAddress")
        self.parentAdrr=addr

    def SetChild(self,child):
        """
        Set the Child Node.
        """
        print("SetChild")
        try:
            if self.child is None:
                self.child=child
                self.childAdrr=self.child.GetIpAddress()
                self.child.SetNext(self.next)
                self.child.SetPrevious(self.previous)
                self.child.SetParentAddress(self.myIp)
                #data call
                self.TakeInitialData()
                print("CHILD:{0}".format(self.child))
                t1=threading.Thread(target=self.VerifyParent)
                t1.daemon=True
                t1.start()
                return "True"
            else:return "False"
        except :
            return "False"

    def SetParent(self,parent):
        """
        Set the Parent Node.
        """
        print("SetParent")
        try:
            if self.parent is None:
                self.parent=parent
                self.parentAdrr=self.parent.GetIpAddress()
                self.next=self.parent.GetNext()
                self.previous=self.parent.GetPrevious()
                self.parent.SetChildAddress(self.GetIpAddress())
                print("PARENT:{0}".format(self.parent))
                t1=threading.Thread(target=self.VerifyParent)
                t1.daemon=True
                t1.start()
                return True
            else:return False
        except :
            return False

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
        return [x for x in self.manager.search_result(pattern, matchoption)]#fix this

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
                item[3]=self.parentAdrr
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


    def IsAlive(self):
        return True

    def CallForParent(self):
        if self.parentAdrr is not None:
            print("CallForParent")
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg="Are you there?"
            sock_out.sendto(msg.encode(), (str(self.parentAdrr), PORT))
            self.mySocket =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.mySocket.bind((str(self.myIp),ANSWERPORT))
            self.timer=Timer(3.0,self.print_death)
            self.timer.start()
            (msg, address) = self.mySocket.recvfrom(65536)
            self.timer.cancel()
            self.mySocket.close()
            if msg.decode() == "YES":
               return True

    def CallForChild(self):
        if self.childAdrr is not None:
            print("CallForChild")
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg="Are you there?"
            sock_out.sendto(msg.encode(), (str(self.childAdrr), PORT))
            self.mySocket =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.mySocket.bind((str(self.myIp),ANSWERPORT))
            self.timer=Timer(3.0,self.print_death)
            self.timer.start()
            (msg, address) = self.mySocket.recvfrom(65536)
            self.timer.cancel()
            self.mySocket.close()
            if msg.decode() == "YES":
                return True

    def CallMe(self):
        if not self.imInRing:
            self.CallForParent()
        else:
            self.CallForChild()

    def print_death(self):
        #self.mySocket.close()
        print("some death")
        if self.imInRing:
            try:
                if self.next is not None and self.previous is not None:
                    if self.next.IsAlive() and self.previous.IsAlive():
                        self.child=None
                        self.childAdrr=None
                        print("my son is dead and my nexts alive")
                else:
                    self.child=None
                    self.childAdrr=None
                    print("My son is dead")
            except:
                self.imInRing=False
                self.childAdrr=None
                self.next=None
                self.previous=None
                self.parent=None
                self.parentAdrr=None
                self.SayHello()
                print("im a dead father")
        else:
            try:
                if self.next is not None and self.previous is not None:
                    if self.next.IsAlive() and self.previous.IsAlive():
                        self.parent=None
                        self.parentAdrr=None
                        self.next.SetPrevious(self)
                        self.previous.SetNext(self)
                        print("nexts updated.!!!")
                        self.imInRing=True
                        self.child=None
                        self.childAdrr=None
                else:
                    self.parent=None
                    self.parentAdrr=None
                    self.child=None
                    self.childAdrr=None
                    self.imInRing=True
                    #self.fail=True
                    #Timer(1.0,self.SendUriOnFails).start()
                print("my father is dead and im in ring")
            except:
                self.parent=None
                self.parentAdrr=None
                self.next=None
                self.previous=None
                self.fail=True
                Timer(1.0,self.SayHelloOnFails).start()
                print("im a dead son")

    def SayHelloOnFails(self):
        if self.fail:
            print("Saying Hello")
            self.SayHello()
            Timer(10.0,self.SayHelloOnFails).start()

    def SendUriOnFails(self):
        if self.fail:
            print("Sendind Uri")
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            msg = str(self.uri)
            sock_out.sendto(msg.encode(), ("255.255.255.255", PORT))
            sock_out.close()
            Timer(10.0,self.SendUriOnFails).start()

    def SayHello(self):
        """
        Send a broadcast message to search parent or enter in the ring and listen for messages.
        """
        sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = "hello"
        sock_out.sendto(msg.encode(), ("255.255.255.255", PORT))
        sock_out.close()

    def ImListen(self):
        """
        Listen for Broadcast messages.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0",PORT))
        self.print_resume()
        t=None
        while True:

            if not self.imInRing and self.parent is None:
                number= random.randint(0,7)
                print(number)
                t=Timer(TIMEOUT+number,self.ImTheOne)
                t.start()
            (msg, address) = s.recvfrom(65536)

            if t is not None:
                t.cancel()

            print("tengo info {0}".format(address))
            sms=msg.decode()

            print("MSG:{0}".format(sms))

            if self.myIp == str(address[0]):
                print("evitando escuchar mis propios msg.")
                continue

            elif sms == "Are you there?":
                if self.imInRing:
                    print("se recibe un mensaje de vida de su hijo.")
                else:
                    print("se recibe un mensaje de vida de su padre.")

                sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg="YES"
                print(msg)
                sock_out.sendto(msg.encode(), (address[0], ANSWERPORT))

                if self.imInRing:
                    print("child response send!!!.")
                else:
                    print("parent response send!!!.")
                sock_out.close()

            elif sms=="hello": #and self.imInRing:
                print("se recibe un mensaje hello de algun nodo que busca padre")
                sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                if self.imInRing:
                    if self.child == None:
                        msg = str(self.uri)
                    else:
                        msg="Full House.{0}".format(self.uri)
                    print(msg)
                    sock_out.sendto(msg.encode(), (address[0], PORT))
                    sock_out.close()
                    print("info send!!!.")
                else:
                    if self.parent is None:
                        sock_out.close()
                        print("se ignora ya que no tengo padre y no estoy en el anillo.")
                        continue
                    msg="Full House.{0}".format(self.parent.GetUri())
                    print(msg)
                    sock_out.sendto(msg.encode(), (address[0], PORT))
                    sock_out.close()
                    print("info send!!!.")


            elif str(sms).__contains__("Full House") and not self.imInRing:
                print("respondio algun nodo que ya tenia hijo y le permite entonces entrar al anillo mediante el.")
                if self.fail:
                    self.fail=False
                    Timer(3.0,self.VerifyParent).start()
                substr=str(sms)#implementar logica de esperar mas respuestas por posibles anfitriones
                sim=str(substr[11:])
                print("URI FULL HOUSE:{}".format(sim))
                #entrar al anillo y buscar quien no tenga hijos.
                self.SearchForParent(sim)
                if self.fail:
                    self.fail=False
                if self.parent is not None:
                    self.VerifyParent()
            #respondio un nodo que no tiene hijo y se tratara de poner como hijo de el.
            elif str(sms).__contains__("PYRO") and not self.imInRing:# and  (not self.imInRing):
                print("respondio un nodo que no tiene hijo y se tratara de poner como hijo de el.")
                if self.parent == None:
                    par=Pyro4.Proxy(sms)
                    try:
                        res=par.SetChild(self)
                        print(res)
                        if res == "True":
                            print("ya tengo padre")
                            self.parent=par
                            #self.parent.VerifyParent()
                            if self.fail:
                                self.fail=False
                            #self.VerifyParent()
                            continue
                        else:self.parent=None
                    except :
                        self.parent=None
                        self.parentAdrr=None
                print("PASO")
            self.print_resume()

    def ImTheOne(self):
        """
        Invoke this method when no receive answer of any node.
        """
        print("Im in ring")
        if not self.imInRing:
            self.imInRing=True
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            msg = str(self.uri)
            sock_out.sendto(msg.encode(), ("255.255.255.255", PORT))
            sock_out.close()

    def VerifyParent(self):
        self.CallMe()
        #print("Verifiying")
        Timer(7.0,self.VerifyParent).start()

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
        t1=threading.Thread(target=self.VerifyParent)
        t1.daemon=True
        t1.start()

        self.SayHello()
        self.ImListen()
        # t=threading.Thread(target=self.SayHello)
        # t.start()
        #self.pyroDaemon.requestLoop()

    def print_resume(self):
        resume="############################\nRESUME:\nNEXT:{}\nPREVIOUS:{}\nInRING:{}\nPARENT:{}\nPARENTAdrr:{}\nCHILD:{}\nCHILDAdrr:{}\n############################".format(self.next,self.previous,self.imInRing,self.parent,self.parentAdrr,self.child,self.childAdrr)
        print(resume)

    #data acces
    #for children
    def GetDataToMyParent(self):
        self.manager.start_journal()
        senderth=threading.Thread(target=self.SenDataWhenNeeded)
        senderth.daemon=True
        senderth.start()
        return [x for x in self.manager.extract_database_data()]


    def SenDataWhenNeeded(self):
        while True:
            time.sleep(1)
            print("Trying to send data")
            if len(self.manager.operation_list)!=0:
                self.parent.TakeChanges(self.manager.operation_list)
                self.manager.operation_list=[]
                print("data sent")

    #for parent nodes
    def TakeInitialData(self):
        self.manager.push_into_database(self.childAdrr, self.child.GetDataToMyParent())


    #self.connect.parent.TakeChanges(list)
    def TakeChanges(self,changes):
        self.manager.process_changes_from(self.childAdrr,changes)
