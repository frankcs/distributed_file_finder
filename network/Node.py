__author__ = 'Jorge'

import Pyro4
import threading
import socket
from threading import Timer
import random
import time
from hashlib import md5

TIMEOUT=3.0
PORT=3200
TIMECOMMCHILD=2
TIMECHECKSYNC=2
TIMERNEXTS=5.0

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
        self.timer=None
        self.daemon=True
        self.fail=False
        self.mySocket=None
        self.timerNext=None
        self.socketNext=None
        self.timerPrevious=None
        self.socketPrevious=None
        self.failNext=False
        self.failPrevious=False
        self.nextAdrr=None
        self.previousAdrr=None
        self.failNext=False
        self.failPrevious=False
        self.manager=manager
        self.verifying=False


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
        if next is not None:
            self.next=next
            self.nextAdrr=next.GetIpAddress()
            if not self.verifying:
                self.verifying=True
                t=threading.Thread(target=self.CheckNext)
                t.daemon=True
                t.start()
        else:
            self.next=None
            self.nextAdrr=None
        if self.child is not None:
            self.child.SetNext(next)

    def SetNextAddress(self,next):
        print("SetNextAddress")
        self.nextAdrr=next

    def SetPreviousAddress(self,previous):
        print("SetPreviousAddress")
        self.previousAdrr=previous

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
        if previous is not None:
            print("SetPrevious")
            self.previous=previous
            self.previousAdrr=previous.GetIpAddress()
            if not self.verifying:
                self.verifying=True
                t=threading.Thread(target=self.CheckNext)
                t.daemon=True
                t.start()
        else:
            self.previous=None
            self.previousAdrr=None
        if self.child is not None:
            self.child.SetPrevious(previous)

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
                print("CHILD:{0}".format(self.child))
                self.child.SetNext(self.next)
                self.child.SetPrevious(self.previous)
                self.child.SetParentAddress(self.myIp)
                #data call
                print("Voy a buscar")
                self.TakeInitialData()
                print("CHILD:{0}".format(self.child))
                t1=threading.Thread(target=self.VerifyParent)
                t1.daemon=True
                t1.start()
                return "True"
            else:return "False"
        except Exception as inst:
            print(inst)
            return "False"

    def GetIpAddress(self):
        return Pyro4.socketutil.getMyIpAddress()

    def HasChild(self):
        return self.child is None

    def GetUri(self):
        return self.uri

    def ImInRing(self,dont_do=False):
        self.imInRing=True
        self.GiveEveryoneInRingMyDB(dont_do)

    def SearchInRing(self,info,path):
        """
        Make a search
        """
        nextneig=self.next
        while nextneig != None and nextneig._pyroUri != self.uri:
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
                self.nextAdrr=index.GetIpAddress()
                t=threading.Thread(target=self.CheckNext)
                t.daemon=True
                t.start()
                self.previous=index
                self.previousAdrr=index.GetIpAddress()
                #t1=threading.Thread(target=self.VerifyPrevious)
                #t1.daemon=True
                #t1.start()
                self.ImInRing()
                print("2 Nodes")
                break
            if index.GetId() < self.id and self.id < nextIndex.GetId():#Case 2: Find your position by id
                self.next=nextIndex
                self.nextAdrr=nextIndex.GetIpAddress()
                t=threading.Thread(target=self.CheckNext)
                t.daemon=True
                t.start()
                self.previous=index
                self.previousAdrr=index.GetIpAddress()
                #t1=threading.Thread(target=self.VerifyNext)
                #t1.daemon=True
                #t1.start()
                index.SetNext(self)
                nextIndex.SetPrevious(self)
                self.ImInRing()
                print("Case 2")
                break
            if index.GetId() < self.id and self.id > nextIndex.GetId():#Case 3: At the end of the ring
                self.next=nextIndex
                self.nextAdrr=nextIndex.GetIpAddress()
                t=threading.Thread(target=self.CheckNext)
                t.daemon=True
                t.start()
                self.previous=index
                self.previousAdrr=index.GetIpAddress()
                #t1=threading.Thread(target=self.VerifyNext)
                #t1.daemon=True
                #t1.start()
                index.SetNext(self)
                nextIndex.SetPrevious(self)
                self.ImInRing()
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
            nextHelper=nextHelper.GetNext()

    def IsAlive(self):
        return True

    def CallForParent(self):
        if self.parent is not None:
            try:
                if self.parent.IsAlive():
                    print("Parent is Alive.")
                    return True
            except :
                print("Parent is death.")
                self.Parent_death()
                return False

    def CallForChild(self):
        if self.child is not None:
            try:
                if self.child.IsAlive():
                    print("Son is Alive.")
                    return True
            except :
                print("Child is death.")
                self.Child_death()
                return False

    def Child_death(self):
        self.DeleteEverythingFrom(self.childAdrr)
        self.child=None
        self.childAdrr=None

    def Parent_death(self):
        #Dos casos
        #Caso 1: Mi padre se desconecta y yo veo a sus hermanos
        try:
            if self.next.IsAlive() and self.previous.IsAlive():
                self.fail=True
                print(self.next)
                self.previous.SetNext(self)
                self.next.SetPrevious(self)
                print(self.previous)
                self.next.DeleteEverythingFrom(self.parentAdrr)
                print(self.next)
                self.parent=None
                self.parentAdrr=None
                print("I claim my parent place")
                print("nexts updated.!!!")
                self.ImInRing(True)
                self.CheckNext()
        except : #caso 2 estoy solo en el mundo
            self.fail=True
            self.parent=None
            self.parentAdrr=None
            self.SetNext(None)
            self.SetPrevious(None)
            self.SayHelloOnFails()


    def CallMe(self):
        if not self.imInRing:
            self.CallForParent()
        else:
            self.CallForChild()

    def SayHelloOnFails(self):
        if self.fail:
            print("Saying Hello")
            self.SayHello()
            Timer(10.0,self.SayHelloOnFails).start()

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
        #self.print_resume()
        t=None
        while True:
            if not self.imInRing and self.parent is None:
                number= random.randint(0,3)
                print(number)
                t=Timer(TIMEOUT+number,self.ImTheOne)
                t.start()
            (msg, address) = s.recvfrom(65536)

            if t is not None:
                t.cancel()

            print("tengo info {0}".format(address))
            sms=msg.decode()

            print("MSG IMLISTEN:{0}".format(sms))

            if self.myIp == str(address[0]):
                print("evitando escuchar mis propios msg.")
                continue
            elif sms.__contains__("ALERT"):
                if str(address[0]) == str(self.parentAdrr):
                    print("evitando escuchar los msg broadcast de mi padre.")
                    continue
                list=str(sms).split('>>')
                sender=list[1]
                broke=list[2]
                if str(broke) == str(self.myIp):
                    print("continueeee")
                    continue
                if self.nextAdrr is not None and str(self.nextAdrr)== broke:
                    self.nextAdrr=None
                    self.next=None
                    user=Pyro4.Proxy(str(sender))
                    if user.SetNext(self) == "True":
                        self.SetPrevious(user)
                if self.previousAdrr is not None and str(self.previousAdrr)== broke:
                    self.previousAdrr=None
                    self.previous=None
                    user=Pyro4.Proxy(str(sender))
                    if user.SetPrevious(self) == "True":
                        self.SetNext(user)
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
                if self.parent is None:
                    print("no tengo padre")
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
                else:
                    print("ya tengo padre no atiendo este llamado.")
                print("PASO")
            #self.print_resume()

    def ImTheOne(self):
        """
        Invoke this method when no receive answer of any node.
        """
        print("Im in ring")
        if not self.imInRing:
            self.ImInRing()
            sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            msg = str(self.uri)
            sock_out.sendto(msg.encode(), ("255.255.255.255", PORT))
            sock_out.close()

    def VerifyParent(self):
        if self.fail:
            self.fail=False
        else:
            Timer(7.0,self.VerifyParent).start()
            self.CallMe()



    def SendAdvice(self,sender,broke):
        sock_out =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = "ALERT>>{}>>{}".format(sender,broke)
        sock_out.sendto(msg.encode(), ("255.255.255.255", PORT))
        sock_out.shutdown(socket.SHUT_RDWR)
        sock_out.close()

    #ver si poner o no en NONE.
    def Next_death(self):
        print("Next_death")
        #self.socketNext.close()
        self.failNext=True
        #ver si poner o no en NONE.
        self.SendAdvice(self.uri,self.nextAdrr)
        self.DeleteEverythingFrom(self.nextAdrr)
        self.next=None
        self.nextAdrr=None
        if self.child is not None:
            self.child.SetNext(None)



    def VerifyNext(self):
        print("VerifyNext")
        if self.failNext:
            self.failNext=False
            return False
        if self.next is not None:
            try:
                if self.next.IsAlive():
                    print("Next Alive")
                    return True
            except :
                self.Next_death()
                return False


    def Previous_death(self):
        print("Previous_death")
        #self.socketPrevious.close()
        self.failPrevious=True
        self.SendAdvice(self.uri,self.previousAdrr)
        self.DeleteEverythingFrom(self.previousAdrr)
        self.previous=None
        self.previousAdrr=None
        if self.child is not None:
            self.child.SetPrevious(None)


    def VerifyPrevious(self):
        print("VerifyPrevious")
        if self.failPrevious:
            self.failPrevious=False
            return False
        if self.previous is not None:
            try:
                if self.previous.IsAlive():
                    print("Previous Alive")
                    return True
            except :
                self.Previous_death()
                return False


    def CheckNext(self):
        if self.imInRing:
            self.verifying=True
            Timer(TIMERNEXTS,self.CheckNext).start()
            if self.next is not None:
                self.VerifyNext()
            if self.previous is not None:
                self.VerifyPrevious()

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
        self.print_resume()
        self.SayHello()
        self.ImListen()
        # t=threading.Thread(target=self.SayHello)
        # t.start()
        #self.pyroDaemon.requestLoop()

    def print_resume(self):
        Timer(5.0,self.print_resume).start()
        resume="############################\nRESUME:\nNEXT:{}\nNEXTAdrr:{}\nPREVIOUS:{}\nPREVIOUSAdrr:{}\nInRING:{}\nPARENT:{}\nPARENTAdrr:{}\nCHILD:{}\nCHILDAdrr:{}\n############################".format(self.next,self.nextAdrr,self.previous,self.previousAdrr,self.imInRing,self.parent,self.parentAdrr,self.child,self.childAdrr)
        print(resume)

    def RingWithoutMe(self):
        """
        Me da acceso a todas los piro objects del anillo
        """
        if not self.imInRing:
            return None
        else:
            try:
                all=[]
                elem=self.next
                if elem is None:
                    return None
                while True:
                    all.append(elem)
                    elem=elem.GetNext()
                    if elem.GetIpAddress() == self.myIp or elem is None:
                        return all
            except :
                return None

    def ChildDisposal(self,childaddr):
        self.DeleteEverythingFrom(childaddr)

    def LocalSearch(self,pattern, matchoption, block=''):
        return [x for x in self.manager.search_result(pattern, matchoption,block)]#fix this

    def Search(self, pattern, matchoption, amount= 400):
        result=[]
        child= True if not self.imInRing else False

        for item in self.LocalSearch(pattern,matchoption):
            result.append(item)
            if len(result)>=amount:
                yield result
                result=[]
        if child:
            for item in self.parent.LocalSearch(pattern,matchoption,self.myIp):
                #si te llega algo que diga localhost ponle que es de tu padre
                item[3]=self.parentAdrr if item[3]=='localhost' else item[3]
                result.append(item)
                if len(result)>=amount:
                    yield result
                    result=[]
        yield result# por si te quedo algo o nunca llegaste al amount

        #data acces
    #for children
    def GetDataToMyParent(self):
        self.StartJournal()
        senderth=threading.Thread(target=self.SenDataToMyParent)
        senderth.daemon=True
        senderth.start()
        return [x for x in self.manager.extract_database_data()]


    def SenDataToMyParent(self):
        while not self.imInRing:
            time.sleep(TIMECOMMCHILD)
            print("Looking for data to send")
            op=self.manager.get_operation_list()
            if len(op)!=0 and self.parent is not None:
                self.parent.TakeChangesFromChild(self.myIp,op)
                print("Data sent to my parent: \n{} ".format(op))
            else:
                print("nothing to send")

    #for parent nodes
    def TakeInitialData(self):
        print(self.childAdrr)
        #si tienes hermanos en algun momento ya diste la base de datos
        #y tienes que guardar los cambios que te hacen
        if self.next:
            self.StartJournal()
        obj= self.child.GetDataToMyParent()
        print("Data received from Child: \n {}".format(obj))
        self.manager.push_into_database(self.childAdrr,self.myIp,obj)


    def TakeInitialDataFromIndex(self, index_addr, data):
        self.StopJournal()
        self.manager.push_into_database(index_addr, self.myIp, data)
        self.StartJournal()
        print("Received db from {}".format(index_addr))

    #self.connect.parent.TakeChanges(list)
    def TakeChangesFromChild(self,from_who,changes):
        self.StartJournal()
        self.manager.process_changes_from(from_who,changes)
        print("Changes taken from {} index".format(from_who))

    def TakeChangesFromIndex(self,from_who,changes):
        self.manager.process_changes_from_off_the_record(from_who,changes)
        print("Changes taken from {} index".format(from_who))

    def ExposeDataBase(self):
        return [x for x in self.manager.extract_database_data()]

    def GiveEveryoneInRingMyDB(self,dont_do=False):
        """
        Dar la base de datos inicialmente a la gente en el anillo
        Recibir la base de datos de uno, supuestamente actualizada
        Iniciar el paso de datos de los cambios(SendDataToRIng)
        Recordar guardar el resultado de get_operation_list porque se resetea la lista
        """
        first=True
        everyones_db=None
        first_adress=None
        print("Got into the ring and passing my data")
        ring= self.RingWithoutMe()
        if ring:
            for index in ring:
                if first:
                    everyones_db=index.ExposeDataBase()
                    first_adress=index.GetIpAddress()
                    first=False
                    #paro la recolección del historial dado que esto se va a realizar en todos los nodos
                #actualizo la base de datos
                if not dont_do:
                    index.TakeInitialDataFromIndex(self.myIp,self.ExposeDataBase())
                #ejecuto de nuevo el historial
            self.TakeInitialDataFromIndex(first_adress,everyones_db)
        senderth= threading.Thread(target=self.SendDataToRing)
        senderth.daemon=True
        senderth.start()

    def StartJournal(self):
        self.manager.start_journal()

    def StopJournal(self):
        self.manager.stop_journal()

    def SendDataToRing(self):
        """
        Enviar periódicamente, si es necesario mis operaciones
        Cuando termine de enviar estos datos
        """
        self.StartJournal()
        while self.imInRing: #and self.next and self.previous:
            time.sleep(TIMECHECKSYNC)
            op= self.manager.get_operation_list()
            if len(op)!=0:
                print("Data sent to ring: \n {}".format(op))
                ring= self.RingWithoutMe()
                if ring:
                    for index in ring:
                        print(index)
                        index.TakeChangesFromIndex(self.myIp,op)
        self.StopJournal()

    def DeleteEverythingFrom(self, machine_id):
        print("Eliminar todos los datos de {}".format(machine_id))
        self.manager.delete_everything_from(machine_id)

    def Download(self,file,to_who):
        return self.SendFileTo(file,to_who)

    def SendFileTo(self,path,to_who):
        try:
            file=open(path,rmode) 
        except IOError as msg:
            print("Error:{} for file{}".format(msg,path))

        m = md5()
        while 1:
            data = file.read(bufsize)
            if not data:
                break
            m.update(data)
        result.append(m.hexdigest())



