class config:
    dic = {}
    def __init__ (self,filename = "config/config.json"):
        import json
        self.filename = filename
        try:
            fp = open(filename,"r")
        except FileNotFoundError:
            self.dic={}
            return
        s = fp.read()
        fp.close()
        self.dic = json.loads(s)

    def dict(self):
        return self.dic
    def getkey(self,key):
        if key not in self.dic:
            return None
        return self.dic[key]

    def setkey(self,key,value):
        self.dic[key]=value

    def delkey(self,key):
        del self.dic[key]
    
    def save(self):
        import json
        s = json.dumps(self.dic,indent=4)
        fp = open(self.filename,"w")
        fp.write(s)
        fp.close()

    def reload(self):
        self.save()
        self.__init__(self.filename)