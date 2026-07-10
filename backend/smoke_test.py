import urllib.request, json

# Health check
r = urllib.request.urlopen('http://127.0.0.1:8000/health')
print('HEALTH:', json.loads(r.read()))

# SOS trigger
req = urllib.request.Request(
    'http://127.0.0.1:8000/sos',
    data=json.dumps({'user_id': 'demo_user', 'lat': 19.076, 'lng': 72.877, 'contact_ids': ['friend_1']}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
r2 = urllib.request.urlopen(req)
sos = json.loads(r2.read())
print('SOS session_id:', sos['session_id'])
print('alert_time    :', sos['alert_time'])
print('message       :', sos['message'])

# Session status
sid = sos['session_id']
r3 = urllib.request.urlopen('http://127.0.0.1:8000/session/' + sid + '/status')
print('STATUS:', json.loads(r3.read()))

# Safety score for a Mumbai coordinate
r4 = urllib.request.urlopen('http://127.0.0.1:8000/safety/score?lat=19.076&lng=72.877')
score = json.loads(r4.read())
print('SAFETY SCORE :', score['safety_score'], '|', score['safety_label'])
print('hex_id       :', score['hex_id'])
print('crime_count  :', score['crime_count'])
print('nearest_police_m:', score['nearest_police_m'])

print('\nAll smoke tests passed!')
