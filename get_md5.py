from hashlib import md5

bufsize = 8096
rmode = 'rb'

def get_md5_for_files(paths):
    result=[]
    for path in paths:
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
    return result

print(get_md5_for_files(["D:\Software\Programming and learning\VS 12\VS2012 RTM\en_visual_studio_ultimate_2012_RTM_x86_dvd.rar"]))
