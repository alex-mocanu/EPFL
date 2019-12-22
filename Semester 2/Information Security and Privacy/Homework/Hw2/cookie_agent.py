import requests


data = {
    'user': 'administrator',
    'pass': '42'
}
r = requests.post('http://127.0.0.1:5000/ex3/login', json=data)
cookie_content = r.cookies['LoginCookie']
# cookie_content = cookie_content[:-1] + '0"'
# print(cookie_content)
cookie = {'LoginCookie': cookie_content}

requests.post('http://127.0.0.1:5000/ex3/list', cookies=cookie)
