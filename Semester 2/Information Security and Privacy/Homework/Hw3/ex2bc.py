import re
import sys
import hashlib


def generate_pwds(word, mappings):
    # Generate all possible passwords according to the available types of changes
    pwds = [word, word.title()]
    for m in mappings:
        pwds = pwds + [w.replace(m, mappings[m]) for w in pwds]
    return set(pwds)


if __name__ == '__main__':
    # Read encrypted passwords
    with open('data/hw3_ex2.txt', 'r') as f:
        data = f.read().split('\n')
        # Check if to read salt and hash or just hash
        if sys.argv[2] == 'b':
            enc_pwds = data[12:22]
        elif sys.argv[2] == 'c':
            enc_pwds = data[23:33]
            salts = [x.split(', ')[0] for x in enc_pwds]
            enc_pwds = [x.split(', ')[1] for x in enc_pwds]
        else:
            print('Wrong task provided as second parameter')
            sys.exit(1)

    # Read dictionary
    with open(sys.argv[1], 'r', errors='ignore') as f:
        words = f.read().split('\n')
        # Keep only words containing alphanumeric characters
        words = list(filter(lambda x: re.match('^[\w-]+$', x) is not None, words))

    pwds = {}
    mappings = {'e': '3', 'o':'0', 'i':'1'}
    for word in words:
        # Finish searching if we've retrieved all passwords
        if len(pwds) == len(enc_pwds):
            break
        # Generate possible passwords from the original word
        possible_pwds = generate_pwds(word, mappings)
        # Check if any of the passwords matches any of the ecrypted ones
        for p in possible_pwds:
            # Check if salt is needed
            if sys.argv[2] == 'b':
                enc_p = hashlib.sha256(p.encode()).hexdigest()
                if enc_p in enc_pwds:
                    print("Match", enc_p, p)
                    pwds[enc_p] = p
            else:
                for salt, enc_pwd in zip(salts, enc_pwds):
                    enc_p = hashlib.sha256((p + salt).encode()).hexdigest()
                    if enc_p == enc_pwd:
                        print("Match", enc_p, p)
                        pwds[enc_p] = p

    # Write passwords to file
    with open(f'ex2{sys.argv[2]}.txt', 'w') as f:
        res = ''
        for enc_p in enc_pwds:
            res += pwds[enc_p] + ','
        f.write(res[:-1])