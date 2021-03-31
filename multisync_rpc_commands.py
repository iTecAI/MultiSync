import hashlib, os

def get_sync_hash(kwargs={'network':None,'tld':None}):
    if not os.path.exists('sync'):
        os.mkdir('sync')
        return {'result':'failure','reason':'no tlds available'}
    if kwargs['network'] == None:
        return {'result':'failure','reason':'specify network'}
    if not os.path.exists(os.path.join('sync',kwargs['network'])):
        return {'result':'failure','reason':'network does not exist'}
    if kwargs['tld'] == None:
        if len(os.listdir(os.path.join('sync',kwargs['network']))) == 0:
            return {'result':'failure','reason':'no tlds available'}
        tld = os.listdir(os.path.join('sync',kwargs['network']))[0]
    else:
        tld = kwargs['tld']
    try:
        dirs = os.walk(os.path.join('sync',kwargs['network'],tld))
    except:
        return {'result':'failure','reason':'tld not found'}
    paths = []
    for d in dirs:
        paths.extend([os.path.join(d[0],f) for f in d[2]])
    snhash = []
    for path in paths:
        with open(path,'rb') as f:
            snhash.append(hashlib.sha256(f.read().decode('utf-8')).hexdigest())
    return {'result':'success','hash':hashlib.sha256('||'.join(snhash)).hexdigest()}

def certify_network(kwargs={'network':None,'tlds':[]}):
    if kwargs['network'] == None:
        return {'result':'failure','reason':'specify network'}
    if not os.path.exists('sync'):
        os.mkdir('sync')
    if not os.path.exists(os.path.join('sync',kwargs['network'])):
        os.mkdir(os.path.join('sync',kwargs['network']))
    for i in kwargs['tlds']:
        if not os.path.exists(os.path.join('sync',kwargs['network'],i)):
            os.mkdir(os.path.join('sync',kwargs['network'],i))
    return {'result':'success'}
    