import hashlib

def compute_md5(n):
    with open(n) as f:
        data = f.read()
        md5hash = hashlib.md5(data).hexidigest()
        return md5hash

compute_md5()
