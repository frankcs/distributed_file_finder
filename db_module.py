import sqlite3
import os
import sys

class db_manager:
    COLUMNS="(path,base_name,is_directory)"
    def __init__(self,db_path, watches):
        self.db_path=db_path
        self.watches=watches

    def populate_database(self):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        cursor.execute('DROP TABLE "files";')
        cursor.execute('CREATE TABLE "files" (\
                       "id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                        "path"  TEXT NOT NULL,\
                        "base_name"  TEXT NOT NULL,\
                        "is_directory"  TEXT NOT NULL,\
                        CONSTRAINT "id" UNIQUE ("id" ASC)\
        );')
        connection.commit()
        for watch in self.watches:
            self.insert_everything_under_path(watch)
        print("Changes Commited")

    def insert_everything_under_path(self,path):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        for directory in os.walk(path,topdown=True):
            self.db_insert(cursor,directory[0],os.path.basename(directory[0]),1)
            for file in directory[2]:
                self.db_insert(cursor,os.path.join(directory[0],file),file,0)
        connection.commit()

    def db_insert(self,cursor, path, base_name, isdir):
        cursor.execute("INSERT INTO files {} VALUES (?,?,?)".format(self.COLUMNS),(path,base_name,isdir))

    def delete_all_within_path(self, deletion_path):
        connection=sqlite3.connect(self.db_path)
        cursor=connection.cursor()
        cursor.execute("DELETE FROM files WHERE path LIKE ?",(deletion_path+"%",))
        connection.commit()

    def update_paths_on_moved(self, old_path, new_path):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        cursor.execute("SELECT * FROM files WHERE path LIKE ?",(old_path+"%",))
        result=[row for row in cursor]
        for row in result:
            new_full_path=row[1][:].replace(old_path,new_path)
            new_base_name=os.path.basename(new_full_path)
            cursor.execute("UPDATE files SET path=?, base_name=?\
            WHERE path = ?",
            (new_full_path,new_base_name,row[1]))
        connection.commit()

    def insert_new_created_entries(self, path, isdir):
        connection=sqlite3.connect(self.db_path)
        cursor= connection.cursor()
        base_name= os.path.basename(path);
        self.db_insert(cursor,path,base_name, isdir)
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
        cursor.execute("SELECT * FROM files WHERE base_name LIKE ?",(final_pattern,))
        stop=False
        for item in cursor:
            if not stop:
                stop=yield (item[1],item[2],item[3])

#my_db=db_manager('D:/Work/SISTDIST/DB/files_db.db',["D:\Work\SISTDIST\Sentry\Test"])
#my_db.populate_database()
#input()
#my_db.delete_all_within_path("D:\Work\SISTDIST\Sentry\Test\\3")
#my_db.update_paths_on_moved("D:\Work\SISTDIST\Sentry\Test\\3","D:")
#my_db.insert_new_created_entries("D:\Work\SISTDIST\Sentry\Test\\3\gacana.txt",0)
#print(my_db.search_result(sys.argv[1],int(sys.argv[2])))