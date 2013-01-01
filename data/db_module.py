import sqlite3
import os

class db_manager:
    COLUMNS="(path,base_name,is_directory)"
    def __init__(self,db_path):
        self.db_path=db_path

    def create_database(self):
        file=open(self.db_path,mode='w')
        file.close()

    def reset_database(self):
        self.create_database()
        connection=sqlite3.connect(self.db_path)
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
        print("Changes Commited")

    def insert_everything_under_path(self,path):
        connection=sqlite3.connect(self.db_path)
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

    # se usa para crear la entrada en files antes de proceder a revisar lo nuevo
    def insert_on_move(self, path):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        parent_directory, base_name =os.path.split(path)
        cursor.execute('SELECT path_id FROM paths WHERE path=?',(parent_directory,))
        path_id=cursor.fetchone()[0]
        #calcular el md5!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.db_files_insert(cursor,path_id,base_name, 1,'')
        connection.commit()
        cursor.close()
        self.insert_everything_under_path(path)


    def db_paths_insert(self,cursor,path, machine_id='localhost'):
        return cursor.execute('INSERT INTO paths (path, machine_id) VALUES (?,?)',(path,machine_id))
    def db_files_insert(self,cursor, path_id, base_name, isdir, md5):
        cursor.execute('INSERT INTO files (path,base_name,is_directory,md5) VALUES (?,?,?,?)'
            ,(path_id,base_name,isdir,md5))

    def delete_all_within_path(self, deletion_path):
        connection=sqlite3.connect(self.db_path)
        cursor=connection.cursor()
        #dividir el camino que me dan para hacer las respectivas consultas
        parent_directory, base_name =os.path.split(deletion_path)
        #preguntar por quién tiene ese camino
        result=cursor.execute('SELECT path_id, id, is_directory\
                               FROM paths\
                               INNER JOIN files\
                               ON paths.path_id = files.path\
                               WHERE paths.path=?\
                               AND files.base_name=?',(parent_directory,base_name))
        # setear lo de directorio siempre en true por el problema de que
        #las watchs no están registradas en la DB
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

    def update_paths_on_moved(self, old_path, new_path):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        #dividir el camino que me dan para hacer las respectivas consultas
        old_parent_directory, old_base_name =os.path.split(old_path)
        new_parent_directory, new_base_name =os.path.split(new_path)
        #si fue el nombre de un directorio buscar todos los que tengan el sufijo viejo y cambiarlo por el nuevo
        cursor.execute('SELECT path FROM paths WHERE path LIKE ?',(old_path+"%",))
        result=[row for row in cursor]
        for row in result:
            #copio el nombre y le aplico replace
            new_full_path=row[0][:].replace(old_path,new_path)
            cursor.execute('UPDATE paths SET path=? WHERE path = ?',
            (new_full_path,row[0]))
        #cambiar las entradas en la tabla files
        cursor.execute('UPDATE files\
                        SET base_name=?\
                        WHERE base_name=?\
                        AND path =(\
                        SELECT path_id\
                        FROM paths\
                        WHERE path =?)',(new_base_name,old_base_name,new_parent_directory))
        connection.commit()

    def insert_new_created_entries(self, path, isdir):
        connection=sqlite3.connect(self.db_path)
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

    def search_result(self, pattern, option):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        final_pattern="%"+pattern+"%"
        if option==1:
            final_pattern= pattern+"%"
        elif option==2:
            final_pattern="%"+pattern

        print(final_pattern)
        cursor.execute('SELECT paths.path, files.base_name, files.is_directory \
                        FROM files \
                        INNER JOIN paths \
                        ON files.path = paths.path_id \
                        WHERE files.base_name LIKE ?',(final_pattern,))
        stop=False
        for item in cursor:
            if not stop:
                stop=yield (item[0],item[1],item[2])

    def persist_watches(self, watches):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        cursor.execute('DELETE FROM watches')
        for watch in watches:
            cursor.execute('INSERT INTO watches (watch) VALUES (?)' ,(watch,))
        connection.commit()

    def retrieve_watches(self):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        return [x[0] for x in cursor.execute('SELECT watch FROM watches')]

    def delete_watch(self, watch):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        cursor.execute('DELETE FROM watches WHERE watch=?',(watch,))
        connection.commit()

    def delete_all_file_data(self):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        cursor.execute('DELETE FROM files')
        cursor.execute('DELETE FROM paths')
        connection.commit()

    #para dar servicio a la red
    def push_into_database(self, pusher_id, data):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        path_id= None
        for item in data:
            self.db_paths_insert(cursor,item[0],pusher_id)
            path_id=cursor.lastrowid
            for entry in item[1]:
                self.db_files_insert(cursor, path_id, entry[0], entry[1], entry[2])
        connection.commit()

    def extract_database_data(self):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        paths= [x for x in cursor.execute('SELECT path_id, path FROM paths')]
        #para poder parar
        stop=False
        for path in paths:
            files_entries=[x for x in cursor.execute('SELECT base_name, is_directory, md5 FROM files where path = ?',(path[0],))]
            if not stop:
                stop=yield (path[1], files_entries)




#my_db=db_manager('./files_db.db')
#my_db.populate_database()
#input()
##my_db.delete_all_within_path("D:\Work\SISTDIST\Sentry\Test\\3")
#my_db.update_paths_on_moved("D:\Work\SISTDIST\Sentry\Test\\3","D:")
#my_db.insert_new_created_entries("D:\Work\SISTDIST\Sentry\Test\\3\gacana.txt",0)
#print(my_db.search_result(sys.argv[1],int(sys.argv[2])))
#my_db.push_into_database('10.6.129.1',my_db.extract_database_data())
