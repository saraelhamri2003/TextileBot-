import urllib.request, urllib.parse, json, sys

try:
    login_data = urllib.parse.urlencode({'username':'demo','password':'demo123'}).encode()
    req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=login_data, headers={'Content-Type':'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req, timeout=10) as res:
        login = json.load(res)
    print('LOGIN:', json.dumps(login))
    token = login.get('access_token')
    body = {'product_name':'Demo Shirt','fiber_composition':'80% coton, 20% polyester','intended_market':'France','label_text':'80% coton, 20% polyester'}
    req2 = urllib.request.Request('http://localhost:8000/api/v1/compliance/check', data=json.dumps(body).encode(), headers={'Content-Type':'application/json','Authorization':f'Bearer {token}'})
    with urllib.request.urlopen(req2, timeout=10) as res2:
        resp = json.load(res2)
    print('RESPONSE_STATUS:', resp.get('status'))
    print('RESPONSE_CONFIDENCE:', resp.get('analysis_result')[:200])
except Exception as e:
    print('ERROR:', str(e))
    import traceback; traceback.print_exc()
    sys.exit(1)
