__author__ = 'Frank'
import threading
import time
import Pyro4

TIMECOMMCHILD=2
TIMECHECKSYNC=2

class network_data_manager():
    def __init__(self, node,manager):
        self.node=node
        self.manager=manager

    def LocalSearch(self,pattern, matchoption, block=''):
        return [x for x in self.manager.search_result(pattern, matchoption,block)]#fix this

    def Search(self, pattern, matchoption, amount= 400):
        result=[]
        child= True if not self.node.imInRing else False

        for item in self.LocalSearch(pattern,matchoption):
            result.append(item)
            if len(result)>=amount:
                yield result
                result=[]
        if child:
            for item in self.node.parent.LocalSearch(pattern,matchoption,self.node.myIp):
                #si te llega algo que diga localhost ponle que es de tu padre
                item[3]=self.node.parentAdrr if item[3]=='localhost' else item[3]
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
        while not self.node.imInRing:
            time.sleep(TIMECOMMCHILD)
            print("Looking for data to send")
            op=self.manager.get_operation_list()
            if len(op)!=0:
                self.node.parent.network_data_manager.TakeChangesFromChild(self.node.myIp,op)
                print("data sent")
            else:
                print("nothing to send")

    #for parent nodes
    def TakeInitialData(self):
        self.manager.push_into_database(self.node.childAdrr, self.node.child.GetNetworkManager().GetDataToMyParent())

    def TakeInitialDataFromIndex(self, index_addr, data):
        self.manager.push_into_database(index_addr,data)
        print("Data inserted from {} index".format(index_addr))

    #self.connect.parent.TakeChanges(list)
    def TakeChangesFromChild(self,from_who,changes):
        self.manager.process_changes_from(from_who,changes)
        print("Changes taken from {} index".format(from_who))

    def TakeChangesFromIndex(self,from_who,changes):
        self.manager.process_changes_from_off_the_record(from_who,changes)

    def ExposeDataBase(self):
        return [x for x in self.manager.extract_database_data()]

    def GiveEveryoneInRingMyDB(self):
        """
        Dar la base de datos inicialmente a la gente en el anillo
        Recibir la base de datos de uno, supuestamente actualizada
        Iniciar el paso de datos de los cambios(SendDataToRIng)
        Recordar guardar el resultado de get_operation_list porque se resetea la lista
        """
        first=True
        everyones_db=None
        first_adress=None
        lock= threading.Lock()
        with lock:
            ring= self.node.RingWithoutMe()
            if ring:
                for index in ring:
                    if first:
                        everyones_db=index.ExposeDataBase()
                        first_adress=index.GetIpAddress()
                        first=False
                        #paro la recolección del historial dado que esto se va a realizar en todos los nodos
                    index.StopJournal()
                    #actualizo la base de datos
                    index.TakeInitialDataFromIndex(self.node.myIp,self.ExposeDataBase())
                    #ejecuto de nuevo el historial
                    index.StartJournal()
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
        while self.node.imInRing and self.node.next and self.node.previous:
            time.sleep(TIMECHECKSYNC)
            op= self.manager.get_operation_list()
            if len(op)!=0:
                lock= threading.Lock()
                with lock:
                    ring= self.node.RingWithoutMe()
                    if ring:
                        for index in ring:
                            index.TakeChangesFromIndex(self.node.myIp,op)
        self.StopJournal()

    def DeleteEverythingFrom(self, machine_id):
        self.manager.delete_everything_from(machine_id)
