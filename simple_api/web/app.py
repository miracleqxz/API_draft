
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import bcrypt

from pymongo import MongoClient

app = Flask(__name__)
api= Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Sentence" : "",
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(retJson)
    
def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False
    
def countTokens(username):
    countTokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return countTokens

class Store(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302,
                "msg": "Invalid username or password"
            }
            return jsonify(retJson)
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301,
                "msg": "Not enough tokens"
            }
            return jsonify(retJson)
        
        
        users.update_one({
            "Username": username
        },{
            "$set":{"Sentence": sentence, 
                    "Tokens": num_tokens - 1}
        })
        retJson = {
            "status": 200,
            "msg": "Sentence successfully saved in the database"
        }

        return jsonify(retJson)
    
class Get(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302,
                "msg": "Invalid username or password"
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301,
                "msg": "Not enough tokens"
            }
            return jsonify(retJson)

        user = users.find_one({"Username": username})
        sentence = user["Sentence"]

        users.update_one(
            {"Username": username},
            {"$set": {"Tokens": num_tokens - 1}}
        )

        retJson = {
            "status": 200,
            "msg": sentence
        }

        return jsonify(retJson)

        
    
    
api.add_resource(Register, '/register')
api.add_resource(Get, '/get')
api.add_resource(Store, '/store')

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api= Api(app)

client = MongoClient("mongodb://db:27017")
db = client.aNewDB
userNum = db ["UserNum"]
userNum.insert_one({
    "num_of_users": 0
})

class Visit(Resource):
    def get(self):
        prev_num = userNum.find({})[0]["num_of_users"]
        new_num = prev_num + 1
        userNum.update_one({}, {"$set": {"num_of_users": new_num}})
        return str("Hello user" + str(new_num))

def checkpostedData(postedData, functionName):
    if (functionName == "add" or functionName == "substract" or functionName == "multiply"):
        if "x" not in postedData or "y" not in postedData:
            return 301
        else:
            return 200
    elif (functionName == "divide"):
        if "x" not in postedData or "y" not in postedData:
            return 301
        elif int(postedData["y"]) == 0:
            return 302
        else:
            return 200
        
class Add(Resource):
    def post(self):
        postedData = request.get_json()

        status_code =checkpostedData(postedData, "add")
        if (status_code != 200):
            retJson = {
                "message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retJson)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        ret = x + y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
    
        return jsonify(retMap)
    


class Substract(Resource):
    def post(self):
        postedData = request.get_json()

        status_code =checkpostedData(postedData, "substract")
        if (status_code != 200):
            retJson = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retJson)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        ret = x - y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
    
        return jsonify(retMap)

class Multiply(Resource):
    def post(self):
        postedData = request.get_json()

        status_code =checkpostedData(postedData, "multiply")
        if (status_code != 200):
            retJson = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retJson)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        ret = x * y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
    
        return jsonify(retMap)

class Divide(Resource):
    def post(self):
        postedData = request.get_json()

        status_code =checkpostedData(postedData, "divide")
        if (status_code != 200):
            retJson = {
                "Message": "An error happened",
                "Status Code": status_code
            }
            return jsonify(retJson)

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)
        ret = (x * 1.0) / y
        retMap = {
            'Message': ret,
            'Status Code': 200
        }
    
        return jsonify(retMap)

api.add_resource(Add, '/add')
api.add_resource(Substract, '/substract')
api.add_resource(Multiply, '/multiply')
api.add_resource(Divide, '/divide')
api.add_resource(Visit, '/hello')

@app.route('/')
def hello_world():
    return "Hello World!"



if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)
"""