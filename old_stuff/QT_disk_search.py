__author__ = 'Frank'
class Searcher():
    def __init__(self,pattern, directory_name, match_option):
        self.dir=QDir(directory_name)
        self.match_option= match_option
        self.query_string=pattern
        self.result_list=[]
        self.done=True
        self.childs=[]
        self.cancel=False

    def search(self):
        self.done=False
        self.childs.append(self.dir)
        self.queue_search()
        self.done=True

    def queue_search(self):
        while self.childs and not self.cancel:
            self.current = self.childs.pop(0)
            for x in self.current.entryInfoList():
                if self.cancel:
                    break
                if x.isFile():
                    if x.fileName().find(self.query_string)!= -1:
                        self.result_list.append([x.fileName(),x.canonicalPath()])
                elif x.isDir():
                    childir=QDir(x.filePath())
                    name=childir.dirName()
                    if name !='.' and name!='..': #no me cojas de nuevo las ref
                        self.childs.append(childir)