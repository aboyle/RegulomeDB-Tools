import urllib, urllib2, time


# HttpBot
# -------
# This class opens a handler and can GET and POST to a url.
#
class HttpBot:
    """an HttpBot represents one browser session, with cookies."""
    def __init__(self):
        cookie_handler= urllib2.HTTPCookieProcessor()
        redirect_handler= urllib2.HTTPRedirectHandler()
        http_handler= urllib2.HTTPHandler()
        error_handler=urllib2.HTTPErrorProcessor()
        self._opener = urllib2.build_opener(cookie_handler,redirect_handler, http_handler,error_handler)
        #urllib2.install_opener(self._opener)

    def GET(self, url):
        return self._opener.open(url).read()

    def POST(self, url, parameters):     
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        return self._opener.open(url, urllib.urlencode(parameters))
    
# getRegulomeDBData
# -----------------
# This function takes a string of 'chr_:pos-pos\nchr_:pos-pos...' and returns a string with
# regulatory information for each site.
#
def getRegulomeDBDataWithText(coordText):
    #coords = 'chrX:55041618-55041619'
    #print coordText
    print "next"
    if coordText == "": return ""
    bot = HttpBot()
    # submit coordinates to regulome db
    trials=0
    # not sure why but sometimes will get error and resubmitting fixes, so have a counter to try again and again
    while trials<100:
        try:
            x = bot.POST('http://regulome.stanford.edu/results', {'data': coordText})
            # get regulome db sid--this seems to be an id associated with the output results file
            # its needed to directly get results in text format
            pageData = x.read();
            pageData = pageData.split("<input type=\"hidden\" name=\"sid\" value=\"")
            sid = pageData[1].split("\" />")[0]
            #print sid
            # get output results file from regulome db using the sid
            x = bot.POST("http://regulome.stanford.edu/download", {'format':'full', 'sid':sid})
            #print x.getcode()
            pageData = x.read()
            # remove header
            pageData = pageData.split("\n", 1)
            pageData = pageData[1]
            return pageData
        except:
            # for whatever reason, errors are common so I iterate until a particular set of positions is successful or 
            # I've reached the max number of iterations
            print "error! trial", trials
            time.sleep(0.25)
            # print coordText
            # print coordText
        trials+=1
    print "error can't be fixed by trying again..."
    return ""

# get a list of sites that didn't get annotated
def getUnannotatedSites(input, output): 
    inputSites={}
    inputLines=input.split("\n")
    for line in inputLines:
        vals = line.split("\t")
        if len(vals)>1:
            site = vals[0]+"\t"+vals[1]
            inputSites[site]=""
    
    badSites=[]
    outputLines=output.split("\t")
    for line in outputLines:
        vals = line.split("\t")
        if len(vals)>1:
            site = vals[0].strip("chr")+"\t"+vals[1]
            if site not in inputSites:
                badSites.append(site)
        
    return badSites

# getRegulomeDBData
# -----------------
# This function takes a list of 'chr_:pos-pos' and returns a string
# with the information from the regulomeDB site.
#
def getRegulomeDBDataWithList(coordList, outfile, numPerRequest):

    #total=min(total, 13000)
    sitesToAnnotate=coordList
    counter = 0
    while True:
        currentSubset=""
        total=len(coordList)
        unannotatedSites=[]
        sofar=0
        while sofar<total:
            i=0
            while i<numPerRequest:
                if sofar>=total: break
                # regulome db does not like MT (mitochondria)
                if "MT" not in coordList[sofar]:
                    currentSubset+="\n"+coordList[sofar]
                sofar+=1
                i+=1
            currentAnnotations = getRegulomeDBDataWithText(currentSubset)
            unannotatedSites += getUnannotatedSites(currentSubset, currentAnnotations)
            outfile.write(getRegulomeDBDataWithText(currentSubset)+"\n")
            currentSubset=""
        counter+=1
        sitesToAnnotate=unannotatedSites
        if len(sitesToAnnotate)==0: break
        # will continue to try to annotate unannotated sites if up until counter greater some number
        if counter > 1: 
            print "sites won't annotate..."
            print sitesToAnnotate
            break
    

#print getRegulomeDBData('chrX:55041618-55041619')
