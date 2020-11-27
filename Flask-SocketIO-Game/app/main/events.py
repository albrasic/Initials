import random
from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
people = {}
people_names = []
control_id = 0
rounds_count = 0
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] 

@socketio.on('joined', namespace='/chat')
def joined(message):
    global people, people_names, rounds_count, control_id
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    join_room(room)
    name = session.get('name')    
    while name in people:
        name = name + '1'
    if name not in people_names:
        people_names.append(name)
    people[name] = 0
    ids = people_names.index(name)
    print(rounds_count, len(people))
    emit('status', {'msg': name + ' with id ' + str(ids) + ' has entered the room.', 'id': ids, 'control_id': control_id}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    global people_names, people, control_id
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    name = people_names[message['a0']]
    people[name] = message['a4']
    emit('reply', {'name': name, 'msg1': message['a1'], 'msg2': message['a2'], 'msg3': message['a3'], 'msg4': message['a4']}, room=room)
    if message['a5']:
        emit('status', {'msg': name + ' has made a correction of ' + message['a5'] + ' points.', 'control_id': control_id}, room=room)

@socketio.on('test', namespace='/chat')
def test():
    global rounds_count, people_names, people, letters, control_id
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    rounds_count += 1
    ids = rounds_count % len(people_names)
    while people_names[ids] not in people:
        rounds_count += 1
        ids = rounds_count % len(people_names)
    control_id = ids
    index = random.randint(0,25)
    tip = letters[index]
    print(people_names[ids])
    leader = max(people, key=people.get)
    lead_id = people_names.index(leader)
    emit('question', {'Q1': tip, 'control_id': ids}, room=room)
    emit('status', {'msg': leader + ' with id ' + str(lead_id) + ' is the leader with ' + str(people[leader]) + ' points.', 'id': lead_id, 'control_id': control_id}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    global people, people_names, control_id
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    ids = message['id']
    name = people_names[ids]
    score = people[name]
    people.pop(name)
    emit('status', {'msg': name + ' and id' + str(ids) + ' has left the room with a score of' + str(score), 'id': ids, 'control_id': control_id}, room=room)

