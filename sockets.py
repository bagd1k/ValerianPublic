import time

import socketio
import rr
text = '''
ффффффффффффффффффффффффффффффффф
'''
sock = socketio.Client()
sock.connect('http://static.rivalregions.com:8880')
for _id in [1]:
    print(_id)
    sock.emit("rr_room", f"u1u_u{_id}u")
    sock.emit('rr_chat', '{"text":"' + text + '", "nome":"' + '0' + '", "id":"' '1' + '", "lang_id":"' + '1' + '", "hash":"' + '2' + '", "room":"' + f'u{_id}u_u1u' + '"}')
    time.sleep(1)
