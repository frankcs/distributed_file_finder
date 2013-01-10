import sqlite3
import os
import threading

TIMEOUT=10

class db_manager:
    COLUMNS="(path,base_name,is_directory)"
    def __init__(self,db_path):
        self.db_path=db_path
        #para enterarme de los cambios que han ocurrido con mi base de datos
        #va a guardar tuplas función, parámetros
        self.operation_list=[]
        self.keep_journal=False
        #self.lock=threading.Lock()

    def create_database(self):
        file=open(self.db_path,mode='w')
        file.close()

    def reset_database(self):
        if self.keep_journal:
            self.operation_list.append(("delete_everything_from",))
        self.create_database()
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        try:
            cursor.execute('DROP TABLE "paths";')
        except : pass
        try:
            cursor.execute('DROP TABLE "files";')
        except : pass
        try:
            cursor.execute('DROP TABLE "watches";')
        except : pass
        cursor.execute('CREATE TABLE "paths" (\
                       "path_id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                       "path"  TEXT NOT NULL,\
                       "machine_id"  TEXT NOT NULL DEFAULT localhost);')
        cursor.execute('CREATE TABLE "files" (\
            "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            "path"  INTEGER NOT NULL REFERENCES "paths" ("path_id") ON DELETE CASCADE ON UPDATE CASCADE,\
            "base_name"  TEXT NOT NULL,\
            "is_directory"  INTEGER NOT NULL,\
            "md5"  TEXT );')
        cursor.execute('CREATE TABLE "watches" ( \
            "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            "watch"  TEXT NOT NULL\
            );')
        connection.commit()
        connection.close()

    def insert_everything_under_path(self,path):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            for directory in os.walk(path,topdown=True):
                self.db_paths_insert(cursor,directory[0])
                #cursor.execute('SELECT path_id FROM paths WHERE path=?',(directory[0],))
                path_id=cursor.lastrowid
                for dirs in directory[1]:
                    self.db_files_insert(cursor,path_id,dirs,1,"")
                for file in directory[2]:
                    self.db_files_insert(cursor,path_id,file,0,"")
            connection.commit()
            connection.close()

    # se usa para crear la entrada en files antes de proceder a revisar lo nuevo
    def insert_on_move(self, path):
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        parent_directory, base_name =os.path.split(path)
        cursor.execute('SELECT path_id FROM paths WHERE path=?',(parent_directory,))
        path_id=cursor.fetchone()[0]
        #calcular el md5!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.db_files_insert(cursor,path_id,base_name, 1,'')
        connection.commit()
        cursor.close()
        self.insert_everything_under_path(path)
        connection.close()


    def db_paths_insert(self,cursor,path, machine_id='localhost'):
        if self.keep_journal:
            self.operation_list.append(("db_paths_insert", machine_id, path))
        return cursor.execute('INSERT INTO paths (path, machine_id) VALUES (?,?)',(path,machine_id))
    def db_files_insert(self,cursor, path_id, base_name, isdir, md5, machine_id='localhost'):
        if self.keep_journal:
            path= cursor.execute('SELECT path FROM paths WHERE path_id=?',(path_id,)).fetchone()[0]
            self.operation_list.append(("db_files_insert", machine_id,path, base_name,isdir,md5))
        cursor.execute('INSERT INTO files (path,base_name,is_directory,md5) VALUES (?,?,?,?)'
            ,(path_id,base_name,isdir,md5))

    def delete_all_within_path(self, deletion_path,machine_id='localhost'):
        #with self.lock:
            if self.keep_journal:
                self.operation_list.append(("delete_all_within_path",machine_id,deletion_path))
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor=connection.cursor()
            #dividir el camino que me dan para hacer las respectivas consultas
            parent_directory, base_name =os.path.split(deletion_path)
            #preguntar por quién tiene ese camino
            result=cursor.execute('SELECT path_id, id, is_directory\
                                   FROM paths\
                                   INNER JOIN files\
                                   ON paths.path_id = files.path\
                                   WHERE paths.path=?\
                                   AND files.base_name=?\
                                   AND paths.machine_id=?',(parent_directory,base_name,machine_id))
            is_directory=True

            tmp=result.fetchone()
            if tmp:
                file_id=tmp[1]
                is_directory=tmp[2]

                #siempre vas eliminar la entrada de la tabla files
                cursor.execute('DELETE FROM files WHERE id=?',(file_id,))

            #si es un directorio has de eliminar todos los caminos que lo tengan de sufijo y todas las entradas
            #en la tabla files que tuvieran a estos caminos....
            if is_directory :
                #tengo que copiar la lista porque el cursor se va a actualizar
                result=[row for row in cursor.execute('SELECT path_id FROM paths WHERE path LIKE ?',(deletion_path+'%',))]
                #por cada camino eliminado eliminar las entradas que los tienen en la tabla files
                for row in result:
                    path_id=row[0]
                    cursor.execute('DELETE FROM files WHERE path = ?',(path_id,))
                #eliminar todos los caminos que tengan com prefijo el elimnado
                cursor.execute('DELETE FROM paths WHERE path LIKE ?',(deletion_path+'%',))
            connection.commit()
            connection.close()

    def update_paths_on_moved(self, old_path, new_path, machine_id='localhost'):
        #with self.lock:
            if self.keep_journal:
                self.operation_list.append(("update_paths_on_moved",machine_id,old_path,new_path))
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            #dividir el camino que me dan para hacer las respectivas consultas
            old_parent_directory, old_base_name =os.path.split(old_path)
            new_parent_directory, new_base_name =os.path.split(new_path)
            #si fue el nombre de un directorio buscar todos los que tengan el sufijo viejo y cambiarlo por el nuevo
            cursor.execute('SELECT path FROM paths WHERE path LIKE ? AND machine_id=?',(old_path+"%",machine_id))
            result=[row for row in cursor]
            for row in result:
                #copio el nombre y le aplico replace
                new_full_path=row[0][:].replace(old_path,new_path)
                cursor.execute('UPDATE paths SET path=? WHERE path = ? AND machine_id=?',
                (new_full_path,row[0],machine_id))
            #cambiar las entradas en la tabla files
            cursor.execute('UPDATE files\
                            SET base_name=?\
                            WHERE base_name=?\
                            AND path =(\
                            SELECT path_id\
                            FROM paths\
                            WHERE path =?\
                            AND machine_id=?)',(new_base_name,old_base_name,new_parent_directory,machine_id))
            connection.commit()
            connection.close()

    def insert_new_created_entries(self, path, isdir):
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        #Si es directorio va generar un nuevo camino
        if isdir:
            self.db_paths_insert(cursor,path)

        parent_directory, base_name =os.path.split(path)
        cursor.execute('SELECT path_id FROM paths WHERE path=?',(parent_directory,))
        path_id=cursor.fetchone()[0]
        #calcular el md5!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.db_files_insert(cursor,path_id,base_name, isdir,'')
        connection.commit()
        connection.close()

    def search_result(self, pattern, option, block=''):
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        final_pattern="%"+pattern+"%"
        if option==1:
            final_pattern= pattern+"%"
        elif option==2:
            final_pattern="%"+pattern

        print(final_pattern)
        cursor.execute('SELECT paths.path, files.base_name, files.is_directory, paths.machine_id \
                        FROM files \
                        INNER JOIN paths \
                        ON files.path = paths.path_id \
                        WHERE files.base_name LIKE ? \
                        AND NOT (paths.machine_id= ?)',(final_pattern,block))
        stop=False
        for item in cursor:
            if not stop:
                stop=yield [item[0],item[1],item[2], item[3]]
        connection.close()

    def persist_watches(self, watches):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            cursor.execute('DELETE FROM watches')
            for watch in watches:
                cursor.execute('INSERT INTO watches (watch) VALUES (?)' ,(watch,))
            connection.commit()
            connection.close()

    def retrieve_watches(self):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            result= [x[0] for x in cursor.execute('SELECT watch FROM watches')]
            connection.close()
            return result


    def delete_watch(self, watch):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            cursor.execute('DELETE FROM watches WHERE watch=?',(watch,))
            connection.commit()
            connection.close()

    def delete_all_file_data(self):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            cursor.execute('DELETE FROM files')
            cursor.execute('DELETE FROM paths')
            connection.commit()
            connection.close()

    #de aquí en adelante son para dar servicio a la red

    def start_journal(self):
        self.keep_journal=True

    def stop_journal(self):
        self.keep_journal=False


    def push_into_database(self, machine_id, local_id, data):
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        path_id= None
        for item in data:
            if item[1]==local_id:
                continue
            m_id=machine_id if item[1]=='localhost' else item[1]
            self.db_paths_insert(cursor,item[0],m_id)
            path_id=cursor.lastrowid
            for entry in item[2]:
                self.db_files_insert(cursor, path_id, entry[0], entry[1], entry[2])
        connection.commit()
        connection.close()

    def delete_everything_from(self, machine_id):
        #with self.lock:
            if self.keep_journal:
                self.operation_list.append(("delete_everything_from",machine_id))
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            paths= [x for x in cursor.execute('SELECT path_id, path FROM paths WHERE machine_id=?',(machine_id,))]
            for path in paths:
               cursor.execute('DELETE FROM files WHERE path=?',(path[0],))
            cursor.execute('DELETE FROM paths WHERE machine_id=?',(machine_id,))
            connection.commit()
            connection.close()

    def extract_database_data(self):
        #with self.lock:
            connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
            cursor= connection.cursor()
            paths= [x for x in cursor.execute('SELECT path_id, path, machine_id FROM paths')]
            #para poder parar
            stop=False
            for path in paths:
                files_entries=[x for x in cursor.execute('SELECT base_name, is_directory, md5 FROM files where path = ?',(path[0],))]
                if not stop:
                    stop=yield (path[1],path[2], files_entries)
            connection.close()

    def process_changes_from(self,machine_id,changes):
        connection=sqlite3.connect(self.db_path,timeout=TIMEOUT)
        cursor= connection.cursor()
        for change in changes:
            print(change)
            id=machine_id if change[1]=='localhost' else change[1]
            if change[0]=="delete_everything_from":
                self.delete_everything_from(id)
            elif change[0]=="db_paths_insert":
                self.db_paths_insert(cursor,change[2],id)
            elif change[0]=="db_files_insert":
                pathid= cursor.execute('SELECT path_id FROM paths WHERE path=? AND machine_id=?',
                    (change[2],id)).fetchone()[0]
                self.db_files_insert(cursor,pathid,change[3],change[4],change[5],id)
            elif change[0]== "delete_all_within_path":
                self.delete_all_within_path(change[2],id)
            elif change[0]== "update_paths_on_moved":
                self.update_paths_on_moved(change[2],change[3],id)
        print("about to commit")
        connection.commit()
        connection.close()

    def process_changes_from_off_the_record(self,machine_id,changes):
        self.stop_journal()
        self.process_changes_from(machine_id,changes)
        self.start_journal()


    def get_operation_list(self):
        result= self.operation_list[:]# esto tambien copia
        self.operation_list=[]
        return result

#my_db=db_manager('./files_db.db')
#my_db.populate_database()
#input()
##my_db.delete_all_within_path("D:\Work\SISTDIST\Sentry\Test\\3")
#my_db.update_paths_on_moved("D:\Work\SISTDIST\Sentry\Test\\3","D:")
#my_db.insert_new_created_entries("D:\Work\SISTDIST\Sentry\Test\\3\gacana.txt",0)
#print(my_db.search_result(sys.argv[1],int(sys.argv[2])))
#my_db.start_journal()
#my_db.push_into_database('10.6.129.1',my_db.extract_database_data())
#my_db.stop_journal()
#my_db.delete_everything_from('10.6.129.1')
#my_db.process_changes_from('10.6.129.1',my_db.operation_list)
#my_db.delete_everything_from('10.6.129.1')
#for x in my_db.search_result('estopa', 0):
    #print(x)
#for x in my_db.search_result('estopa', 0, block="10.6.129.1"):
    #print(x)
