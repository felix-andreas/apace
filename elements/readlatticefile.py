import os
def readfile(filepath):
    name = os.path.basename(filepath)
    with open(filepath) as file:
        print(list(map(str.strip,file.readlines())))
        for line in file:
            # print(type(line))
            pass