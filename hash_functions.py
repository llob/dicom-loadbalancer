import hashlib

def random(input: str, modulo: int):
    # Ensure that input value is not ridiculously large
    if len(input) > 100000:
        raise BaseException('Input value too large')
    # Ensure that modulo value is valid
    if modulo > 10000:
        raise BaseException('Modulo value too large')
    # Create md5 hash, but use only last 6 digits
    hash_suffix = hashlib.md5(input.encode('utf-8')).hexdigest()[-5:]
    # 6 digit decimal number as string, decode
    hash_number = int(hash_suffix, 16)
    # Modulo
    return hash_number % modulo
