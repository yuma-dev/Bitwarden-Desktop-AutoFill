
def printDebug(*objects,args:list):
    debugArgs = ["--debug","debug","-debug","-d"]
    if any(word in args for word in debugArgs):
        print(objects)