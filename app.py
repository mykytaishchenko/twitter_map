"""The module, receiving the username of a Twitter user,
generates a map that shows the followers of a given user.
"""


from flask import Flask, render_template, request, redirect, url_for
import folium
from geopy.geocoders import Nominatim
import json
import requests


nickname = ''
token = ''
test = False

app = Flask(__name__)


def user_request():
    """The function makes a request to the twitter
    API and returns the json file with information about
    user followers.
    """
    if test:
        file = json.load(open('static/friends_list_AdamMGrant.json', 'r', encoding='utf-8'))
        users = [(user_block['name'], user_block['location']) for user_block in file['users']
                 if user_block['location'] != '']
        return users
    else:
        base_url = "https://api.twitter.com/"

        search_url = f'{base_url}1.1/friends/list.json'

        search_headers = {
            'Authorization': f'Bearer {token}'
        }

        search_params = {
            'screen_name': nickname,
            'count': 15
        }

        response = requests.get(search_url, headers=search_headers, params=search_params)
        if response.status_code == 200:
            file = response.json()
            users = [(user_block['name'], user_block['location']) for user_block in file['users']
                     if user_block['location'] != '']
            return users
        else:
            return [[]]


def find_location(users):
    """The function looks for the coordinates of followers.
    """
    users_locations = []
    geo_loc = Nominatim(user_agent="map_generator_with_twitter")
    for user in users:
        try:
            loc = geo_loc.geocode(user[1])
            users_locations.append((user[0], (loc.latitude, loc.longitude)))
        except:
            print('No location')
    return users_locations


def map_generate():
    """The function generates a map, marking followers.
    """
    earth_map = folium.Map(zoom_start=30)
    users = find_location(user_request())

    fg = folium.FeatureGroup(name="Friends.")
    for user in users:
        fg.add_child(folium.Marker(location=user[1],
                                   popup=user[0], icon=folium.Icon()))
    earth_map.add_child(fg)
    earth_map.save('templates/map.html')


@app.route('/', methods=['POST', 'GET'])
def get_parameters():
    """The function renders the main page,
    and accepts the username and key.
    """
    global nickname, token
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        token = request.form.get('key-1')
        return redirect(url_for('show_map'))

    return render_template('home.html')


@app.route('/map')
def show_map():
    """The function starts the generation
    of the map and renders it.
    """
    map_generate()
    return render_template('map.html')


if __name__ == '__main__':
    app.run()
