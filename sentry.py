from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import DirMovedEvent
import sys
import time
import os
from threading import Thread
from db_module import db_manager
from queue import Queue

class octopus_handler(FileSystemEventHandler):
    def __init__(self,manager):
        super(FileSystemEventHandler,self).__init__()
        # se inicializa la base de datos
        self.last_deleted_path=""
        self.ev_db_manager= manager

    def on_any_event(self, event):
        pass

    def on_created(self, event):
        if event.src_path== os.path.realpath(self.ev_db_manager.db_path+"-journal"):
            return
        if event.is_directory:
            print("Created Directory: {}".format(event.src_path))
            #hubo un movimiento de ficheros en windows
            if self.last_deleted_path and os.path.basename(self.last_deleted_path)==os.path.basename(event.src_path):
                self.ev_db_manager.insert_everything_under_path(event.src_path)
            else:
                self.ev_db_manager.insert_new_created_entries(event.src_path,1)
        else:
            print("Created File: {}".format(event.src_path))
            self.ev_db_manager.insert_new_created_entries(event.src_path,0)
        self.last_deleted_path=""

    def on_deleted(self, event):
        if event.src_path== os.path.realpath(self.ev_db_manager.db_path+"-journal"):
            return
        self.ev_db_manager.delete_all_within_path(event.src_path)
        self.last_deleted_path=event.src_path
        print("Deleted all under path: {}".format(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            print("Moved Directory: \"{}\" to \"{}\"".format(event.src_path,event.dest_path))
        else:
            print("Moved File: \"{}\" to \"{}\"".format(event.src_path,event.dest_path))
        self.ev_db_manager.update_paths_on_moved(event.src_path,event.dest_path)
        print("Updates were made")
        self.last_deleted_path=""

    def on_modified(self, event):
        if event.src_path== os.path.realpath(self.ev_db_manager.db_path+"-journal"):
            return
        if event.is_directory:
            print("Modified Directory: {}".format(event.src_path))
        else:
            print("Modified File: {}".format(event.src_path))
        self.last_deleted_path=""

def main():
    manager= db_manager(sys.argv[1], [sys.argv[2]])
    manager.populate_database()
    event_handler= octopus_handler(manager)
    observer=Observer()
    observer.schedule(event_handler,sys.argv[2], recursive=True)
    observer.start()
    print("Observer started at {}".format(sys.argv[2]))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
#main()
#chequear que no me llegue nada del journal para la base de datos
#created deleted