from fastapi import FastAPI
import db
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import api
from typing import Optional

app = FastAPI()

fetchedEvents = []


class Group(BaseModel):
    group_id: int
    token: str
    response: str


class Event(BaseModel):
    group_id: int
    type: str
    event_id: str
    v: str
    object: Optional[dict] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get('/add_form', response_class=HTMLResponse)
def sendForm():
    html = '''
<html>
 <head>
  <meta charset="utf-8">
  <title>julia API</title>
 </head>
 <body>
<script>

async function send() {
const group_id = parseInt(document.getElementById('group_id').value, 10)
const token = document.getElementById('token').value
const responseCode = document.getElementById('response').value

const response = await fetch('/add', {
method: "post",
body: JSON.stringify({group_id: group_id, token: token, response: responseCode}),
headers: {
      'Content-Type': 'application/json'
    }
})
alert("Done!")
}
</script>
 <form action="/add" method="post" id="form">
  <input type="text" id="group_id" placeholder="group_id"><br><br>
  <input type="text" id="token" placeholder="token"><br><br>
  <input type="text" id="response" placeholder="response"><br>
  <input type="button" onclick="send()" id="submit" value="Send!">
 </form>
 </body>
</html>'''
    return HTMLResponse(content=html, status_code=200)


@app.post("/add")
def read_smth(group: Group):
    if db.isGroupExists(group.group_id):
        db.updateGroup(group.group_id, group.token, group.response)
        return {'response': 'Ok'}
    db.addGroup(group.group_id, group.token, group.response)
    return {'response': 'Ok'}


@app.post('/callback/{group_id}')
def read_root(group_id: int, event: Event):
    if db.isGroupExists(group_id) and not db.isGroupVerified(group_id):
        db.verifyGroup(group_id)
        return db.getResponseCode(group_id)
    elif db.isGroupExists(group_id):
        if event.event_id not in fetchedEvents:
            fetchedEvents.append(event.event_id)
            api.fetcher(api.formObject('vk', event, db.getToken(group_id)))
        return 'ok'
