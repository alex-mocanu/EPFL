import hashlib
import itertools


def crack_pwd(pwds):
    res = {}
    # Generate character set
    charset = [chr(ord('a') + i) for i in range(ord('z') - ord('a') + 1)] + \
            [chr(ord('0') + i) for i in range(ord('9') - ord('0') + 1)]
    # Find plain password
    for length in range(4, 7):
        char_lists = [charset] * length
        for p in itertools.product(*char_lists):
            # Stop after retrieving all passwords
            if len(res) == len(pwds):
                return res
            p = ''.join(p)
            # Encrypt password and check for match
            enc_p = hashlib.sha256(p.encode()).hexdigest()
            if enc_p in pwds:
                print(enc_p, p)
                res[enc_p] = p
    return res


if __name__ == '__main__':
    pass_file = 'data/hw3_ex2.txt'

    # Read hashed passwords
    with open(pass_file, 'r') as f:
        data = f.read().split('\n')
        pwds = data[1:11]

    # Crack passwords
    plain_pwds = crack_pwd(pwds)
    # Store plain passwords
    res = ''
    for pwd in pwds:
        res += plain_pwds[pwd] + ','
    with open('ex2b.txt', 'w') as f:
        f.write(res[:-1])
