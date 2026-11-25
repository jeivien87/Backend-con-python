
from flask import Flask, request
import requests

app = Flask(__name__)

USERS = [
    {
        "id": 1,
        "nombre": "Leo",
        "email": "Messi@gmail.com",
        "preferences": {
            "favorite_streamers": ["ibai"],
            "favorite_games": ["Minecraft"]
        }
    },
    {
        "id": 2,
        "nombre": "Cristiano",
        "email": "cr7@gmail.com",
        "preferences": {
            "favorite_streamers": ["auronplay"],
            "favorite_games": ["Just Chatting"]
        }
    }
]


TWITCH_CLIENT_ID = "tjt1tntaa6rnq3g3jp9a4s6fgflxlj"
TWITCH_CLIENT_SECRET = "0oaw1r78l6xtvklhxqzw2m0prejroe"

@app.route("/")
def hello():
    return {
        "message": "Flask Streamers API is running"
    }, 200


@app.route("/users", methods=["GET"])
def get_users():

    return {
        "users": USERS
    }, 200

@app.route("/user/<int:id>", methods=["GET"])
def get_user(id):

    for user in USERS:

        if user["id"] == id:
            return {
                "user": user
            }, 200

    return {
        "message": "User not found"
    }, 404



@app.route("/user", methods=["POST"])
def add_single_user():

    new_user = request.get_json()

    if not new_user:
        return {
            "message": "JSON data is required"
        }, 400

    if "id" not in new_user or "nombre" not in new_user or "email" not in new_user:
        return {
            "message": "id, nombre and email are required"
        }, 400

    if any(user["id"] == new_user["id"] for user in USERS):
        return {
            "message": "User ID already exists"
        }, 409

    new_user.setdefault("preferences", {
        "favorite_streamers": [],
        "favorite_games": []
    })

    USERS.append(new_user)

    return {
        "message": "User added successfully",
        "user": new_user
    }, 201


@app.route("/users", methods=["POST"])
def add_users():

    data = request.get_json()

    if not data or "users" not in data:
        return {
            "message": "The users list is required"
        }, 400

    new_users = data["users"]

    if not isinstance(new_users, list):
        return {
            "message": "users must be a list"
        }, 400

    existing_ids = [user["id"] for user in USERS]
    new_ids = []

    for new_user in new_users:

        if not isinstance(new_user, dict):
            return {
                "message": "Each user must be an object"
            }, 400

        if "id" not in new_user or "nombre" not in new_user or "email" not in new_user:
            return {
                "message": "Each user must have id, nombre and email"
            }, 400

        if new_user["id"] in existing_ids or new_user["id"] in new_ids:
            return {
                "message": f"User with ID {new_user['id']} already exists"
            }, 409

        new_ids.append(new_user["id"])

    for new_user in new_users:

        new_user.setdefault("preferences", {
            "favorite_streamers": [],
            "favorite_games": []
        })

    USERS.extend(new_users)

    return {
        "message": "Users added successfully",
        "users_names": [user["nombre"] for user in new_users]
    }, 201



@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):

    updated_user = request.get_json()

    if not updated_user:
        return {
            "message": "JSON data is required"
        }, 400

    for user in USERS:

        if user["id"] == id:

            user.update(updated_user)

            return {
                "message": "User updated successfully",
                "user": user
            }, 200

    return {
        "message": "User not found"
    }, 404


@app.route("/users-with-authorization/<int:id>", methods=["PUT"])
def update_user_with_auth(id):

    auth_header = request.headers.get("Authorization")

    if auth_header != "1234":
        return {
            "message": "Unauthorized"
        }, 401

    updated_user = request.get_json()

    if not updated_user:
        return {
            "message": "JSON data is required"
        }, 400

    for user in USERS:

        if user["id"] == id:

            user.update(updated_user)

            return {
                "message": "User updated successfully",
                "user": user
            }, 200

    return {
        "message": "User not found"
    }, 404


@app.route("/users", methods=["DELETE"])
def delete_user():

    user_id = request.args.get("id", type=int)

    if user_id is None:
        return {
            "message": "User ID is required"
        }, 400

    for user in USERS:

        if user["id"] == user_id:

            USERS.remove(user)

            return {
                "message": f'User {user["nombre"]} deleted successfully'
            }, 200

    return {
        "message": "User not found"
    }, 404


@app.route("/user/<int:id>/preferences", methods=["POST"])
def add_preferences(id):

    data = request.get_json()

    if not data:
        return {
            "message": "JSON data is required"
        }, 400

    for user in USERS:

        if user["id"] == id:

            user["preferences"].update(data)

            return {
                "message": "Preferences updated successfully",
                "preferences": user["preferences"]
            }, 200

    return {
        "message": "User not found"
    }, 404



@app.route("/user/<int:id>/preferences", methods=["GET"])
def get_preferences(id):

    for user in USERS:

        if user["id"] == id:

            return {
                "preferences": user["preferences"]
            }, 200

    return {
        "message": "User not found"
    }, 404



@app.route("/user/<int:id>/preferences", methods=["PUT"])
def update_preferences(id):

    data = request.get_json()

    if not data:
        return {
            "message": "JSON data is required"
        }, 400

    for user in USERS:

        if user["id"] == id:

            user["preferences"].update(data)

            return {
                "message": "Preferences updated successfully",
                "preferences": user["preferences"]
            }, 200

    return {
        "message": "User not found"
    }, 404



def get_twitch_token():

    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        },
        timeout=15
    )

    if response.status_code != 200:
        print("Twitch token response:", response.text)

    response.raise_for_status()

    return response.json()["access_token"]



@app.route("/twitch/search", methods=["GET"])
def search_streamers():

    query = request.args.get("q")

    if not query:
        return {
            "message": "Search query q is required"
        }, 400

    try:

        token = get_twitch_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Client-Id": TWITCH_CLIENT_ID
        }

        params = {
            "query": query,
            "first": 10
        }

        response = requests.get(
            "https://api.twitch.tv/helix/search/channels",
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            print("Twitch search response:", response.text)

        response.raise_for_status()

        data = response.json()

        streamers = []

        for streamer in data["data"]:

            streamers.append({
                "id": streamer["id"],
                "name": streamer["display_name"],
                "login": streamer["broadcaster_login"],
                "game": streamer["game_name"],
                "title": streamer["title"],
                "is_live": streamer["is_live"],
                "thumbnail": streamer["thumbnail_url"],
                "url": f"https://www.twitch.tv/{streamer['broadcaster_login']}"
            })

        return {
            "query": query,
            "streamers": streamers
        }, 200

    except requests.exceptions.HTTPError as e:

        return {
            "message": "Twitch HTTP error",
            "error": str(e)
        }, 502

    except requests.exceptions.RequestException as e:

        return {
            "message": "Twitch connection error",
            "error": str(e)
        }, 502

    except Exception as e:

        return {
            "message": "Unexpected error",
            "error": str(e)
        }, 500




if __name__ == "__main__":
    app.run(debug=True)
