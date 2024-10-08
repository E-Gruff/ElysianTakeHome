from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)


## setup the database if it doesn't exist

#this is obviously not the best way to create this, and in development a more robust library should be used
#such as a postgreSQL server

with sqlite3.connect('UserKnowledge.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            uuid TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''') #uuid is not primary key due to sort order. Having seperate ID allows for an old-new order, and quicker searches due to the smaller index. 
    conn.commit()


@app.route('/')
def home():
    return render_template('index.html') #serve the frontend from flask as well

@app.route('/accept_webhook', methods=['POST'])
def accept_webhook_post():
    payload = request.json
    payload_type = payload.get('payload_type')
    payload_content = payload.get('payload_content')
    print("payload_type:" + payload_type)
    print("name:", payload_content.get("name"))

    if payload_type =='PersonAdded':
        addPerson(payload_content)
    if payload_type =='PersonRenamed':
        renamePerson(payload_content)
    if payload_type =='PersonRemoved':
        removePerson(payload_content)



    return jsonify({"message": "Webhook processed successfully"}), 200 #Return a 200 code


@app.route('/get_name', methods = ['GET'])
def get_name_get():
    userID = request.args.get('uuid')  #Shouldn't use request.json with get requests
    
    if not userID:
        return jsonify({"error": "UUID is required"}), 400  #empty field
    name = getName(userID) 
    if name:
        return jsonify({"name": name}), 200  # Send the name in the response
    else:
        return None
    




#Function Handlers




def addPerson(content):
    with sqlite3.connect('UserKnowledge.db') as conn:
        cursor = conn.cursor()
    
        name = content.get("name")
        userID = content.get("person_id")
        timestamp = content.get("timestamp")

        cursor.execute('''
            INSERT INTO users (name, uuid, timestamp)
            VALUES (?, ?, ?)
        ''', (name, userID, timestamp))
        conn.commit()




def renamePerson(content):
    with sqlite3.connect('UserKnowledge.db') as conn:
        cursor = conn.cursor()
        newName = content.get("name")
        userID = content.get("person_id")
        timestamp = content.get("timestamp")
        cursor.execute('''
            UPDATE users
            SET name = ?, timestamp = ?
            WHERE uuid = ?
        ''', (newName, timestamp, userID))
        conn.commit()


def removePerson(content):
    with sqlite3.connect('UserKnowledge.db') as conn:
        cursor = conn.cursor()
        name = content.get("name")
        userID = content.get("person_id")
        #timestamp = content.get("timestamp")
        cursor.execute('''
            DELETE FROM users
            WHERE uuid = ?
                    ''',(userID,))
        conn.commit()

def getName(userID):
    with sqlite3.connect('UserKnowledge.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM users
            WHERE uuid = ?
        ''', (userID,))
        result = cursor.fetchone()
        if result:
            print(result)
            return result[0] 
        return None


# Run the app
if __name__ == '__main__':
    app.run()