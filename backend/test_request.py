import time
import urllib.parse
import urllib.request

url = 'http://127.0.0.1:5000/predict'
data = {
    'age': '50',
    'trestbps': '120',
    'chol': '240',
    'thalach': '150',
    'oldpeak': '1.0'
}
enc = urllib.parse.urlencode(data).encode()
req = urllib.request.Request(url, data=enc)

for i in range(10):
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode(errors='replace')
            print('STATUS', resp.status)
            print(body[:1000])
            break
    except Exception as e:
        print('retry', i, e)
        time.sleep(1)
else:
    print('failed to reach app')
