from hashlib import md5
import os.path

bufsize = 8096
rmode = 'rb'
bytes= 8096

def get_md5_for_files(paths):
    result=[]
    file=None
    for path in paths:
        if not os.path.isdir(path):
            try:
                file=open(path,rmode)
            except IOError as msg:
                print("Error:{} for file{}".format(msg,path))
            m = md5()
            count=0
            while count < bytes:
                data = file.read(bufsize)
                count=count+len(data)
                if not data:
                    break
                m.update(data)
            result.append(m.hexdigest())
        else:
            result.append('')
    return result

#print(get_md5_for_files(["D:\Software\Programming and learning\VS 12\VS2012 RTM\en_visual_studio_ultimate_2012_RTM_x86_dvd.rar"]))
