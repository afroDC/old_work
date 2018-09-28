import hashlib
import os
import json

hashDict = {}
dir = os.getcwd()

def sha1checksum(inputFile):
    openedFile = open(inputFile)
    readFile = openedFile.read()
    parsedFile = inputFile.strip('{0}/scripts/extensions'.format(dir)).replace('.','',2).replace('/', ' ').split(' ')
    # print '{' + parsedFile[0] + '{' + parsedFile[1] + '/' + parsedFile[2] + '}' + '}'
    version = parsedFile[0]
    script_default = parsedFile[1] + '/' + parsedFile[2]

    # Remove white spaces, tabs, newlines and carriage returns before hashing to sanitize data
    # It might be wise to attempt to remove comments as well.
    readFile = readFile.replace('\n','').replace('\r\n','').replace('\r','').replace(' ','').replace('\t','').strip()

    sha1Hash = hashlib.sha1(readFile)
    sha1Hashed = sha1Hash.hexdigest()

    if version in hashDict:
        hashDict[version][script_default] = sha1Hashed
    else:
        hashDict.update({version: {script_default:sha1Hashed}})

for root, dirs, files in os.walk('{0}/scripts/extensions'.format(dir)):
    for file in files:
        if '.py' in file:
            inputFile = root + '/' + file
            sha1checksum(inputFile)

with open('default_script_hashes.json', 'w') as f:
    f.write(json.dumps(hashDict, indent=2))