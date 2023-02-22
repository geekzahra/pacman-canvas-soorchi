import json
import time

# Manage core logic by this class
class Settlement :
    @staticmethod
    def default_key(d):
        result = 0
        for key, _ in d.items():
           	# Check key is integer and key is not less than result
            if(type(key) is int and key >= result) :
                # Get new key
                result = key + 1
        d[result] = OrderedDict()
        return result
    
#---------------------------------
# These methods have not been changed yet:
# header
# getHighscore
# addHighscore
# getVersionInfo
# file_get_contents
# json_decode
# createDataBase
# htmlspecialchars
# date
# preg_match
#----------------------------

header('Content-Type: application/json')
# IMPORTANT:
# * change this to the main url of where you host the application, otherwise, every entry will be marked as a cheater
# :

hostdomain = 'pacman.platzh1rsch.ch'
if (isset(_POST['action'])) :
    if (_POST['action'] == 'get') :
        if (isset(_POST['page'])) :
            print(getHighscore(_POST['page']),end="")
        else : 
            print(getHighscore(),end="")
        
    elif (_POST['action'] == 'add') :
        if (isset(_POST['name']) or isset(_POST['score']) or isset(_POST['level'])) :
            print(addHighscore(_POST['name'], _POST['score'], _POST['level']),end="")
        
else : 
    if (isset(_GET['action'])) :
        if (_GET['action'] == 'get') :
            if (isset(_GET['page'])) :
                print(getHighscore(_GET['page']),end="")
            else : 
                print(getHighscore(),end="")
            
        else : 
            if (_GET['action'] == 'version') :
                print(getVersionInfo(),end="")
            
        
    else : 
        print("define action to call",end="")
    

def getVersionInfo() :

    strJsonFileContents = file_get_contents("../package.json")
    # Convert to array
    array = json_decode(strJsonFileContents, True)
    response["version"] = array["version"]
    if (not isset(response) or (response == None)) :
        return "[]"
    else : 
        return json.dumps(response)
    

def getHighscore(page = 1) :

    db =  SQLite3('pacman.db')
    createDataBase(db)
    results = db.query('SELECT name, score FROM highscore WHERE cheater = 0 AND name != "" ORDER BY score DESC LIMIT 10 OFFSET ' + str((page - 1) * 10))
    while (row == results.fetchArray()) :
        tmp["name"] = htmlspecialchars(row['name'])
        tmp["score"] = str(row['score'])
        k__1 = Settlement.default_key(response)
        response[k__1] = tmp
    
    if (not isset(response) or (response == None)) :
        return "[]"
    else : 
        return json.dumps(response)
    

def addHighscore(name, score, level) :

    global hostdomain
    db =  SQLite3('pacman.db')
    date = date('Y-m-d h:i:s', int(time.time()))
    createDataBase(db)
    ref =  _SERVER['HTTP_REFERER'] if isset(_SERVER['HTTP_REFERER']) else ""
    ua =  _SERVER['HTTP_USER_AGENT'] if isset(_SERVER['HTTP_USER_AGENT']) else ""
    remA =  _SERVER['REMOTE_ADDR'] if isset(_SERVER['REMOTE_ADDR']) else ""
    remH =  _SERVER['REMOTE_HOST'] if isset(_SERVER['REMOTE_HOST']) else ""
    # some simple checks to avoid cheaters
    ref_assert = preg_match(str('/http(s)?:\\/\\/.*' + str(hostdomain)) + '/', ref) > 0
    ua_assert = ua != ""
    cheater = 0
    if (not ref_assert or not ua_assert) :
        cheater = 1
    
    maxlvlpoints_pills = 104 * 10
    maxlvlpoints_powerpills = 4 * 50
    maxlvlpoints_ghosts = 4 * 4 * 100
    maxlvlpoints = maxlvlpoints_pills + maxlvlpoints_powerpills + maxlvlpoints_ghosts
    # check if score is even possible
    if (level < 1 or level > 10) :
        cheater = 1
    else : 
        if (score / level > maxlvlpoints) :
            cheater = 1
        
    
    name_clean = htmlspecialchars(name)
    score_clean = htmlspecialchars(score)
    db.exec('INSERT INTO highscore (name, score, level, date, log_referer, log_user_agent, log_remote_addr, log_remote_host, cheater)VALUES(?,?,?,?,?,?,?,?,?)', name_clean, score_clean, level, date, ref, ua, remA, remH, cheater)
    response['status'] = "success"
    response['level'] = level
    response['name'] = name
    response['score'] = score
    response['cheater'] = cheater
    return json.dumps(response)

def createDataBase(db) :

    db.exec('CREATE TABLE IF NOT EXISTS highscore(name VARCHAR(60),score INT, level INT, date DATETIME, log_referer VARCHAR(200), log_user_agent VARCHAR(200), log_remote_addr VARCHAR(200), log_remote_host VARCHAR(200), cheater BOOLEAN)')