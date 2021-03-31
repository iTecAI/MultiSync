import hashlib, os

def get_sync_hash(kwargs={'tld':None}):
    if not os.path.exists('sync'):
        os.mkdir('sync')
        return {'result':'failure','reason':'No TLDs available.'}
    if kwargs['tld'] == None:
        if len(os.listdir('sync')) == 0:
            return {'result':'failure','reason':'No TLDs available.'}
        tld = os.listdir('sync')[0]
    else:
        tld = kwargs['tld']
    try:
        dirs = os.walk(os.path.join('sync',tld))
    except:
        return {'result':'failure','reason':'TLD not found.'}
    paths = []
    for d in dirs:
        paths.extend([os.path.join(d[0],f) for f in d[2]])
    snhash = []
    for path in paths:
        with open(path,'rb') as f:
            snhash.append(hashlib.sha256(f.read().decode('utf-8')).hexdigest())
    return {'result':'success','hash':hashlib.sha256('||'.join(snhash)).hexdigest()}