import requests
import base64
import json
import pandas as pd
from datetime import date

def scrape_playlist(playlistId, clientId, clientSecret):
    """Use Spotify API to get the basic information of all the songs contained in 
    a playlist. 

    This website helps a lot to develope the code presented here:
        https://dev.to/mxdws/using-python-with-the-spotify-api-1d02 
        
    Parameters
    ----------
    playlistId : str
        The Spotify ID for the playlist.
    clientId : str
        Is the unique identifier of your application. To create an application you 
        must have a Spotify's developer account. More information can be found here:
        https://developer.spotify.com/documentation/general/guides/app-settings/
    clientSecret: str
        Is the key that you pass in secure calls to the Spotify Accounts and Web API 
        services. Always store the client secret key securely; never reveal it publicly! 
        If you suspect that the secret key has been compromised, regenerate it 
        immediately by clicking the link on the edit settings view.


    Returns
    -------
    df : DataFrame
        a Pandas DataFrame with this information about each song in the playlist:
        position in the playlist, song name, song id, artists names, artists ids, 
        album name, album id, duration in ms, date in which each song is added, 
        popularity score, name of the playlist, playlist id
    """

    # Step 1 - Authorization 
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{clientId}:{clientSecret}" 
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"

    r = requests.post(url, headers = headers, data = data)

    token = r.json()['access_token']

    # Step 2 - Use Access Token to call playlist endpoint
    playlistUrl = f"https://api.spotify.com/v1/playlists/{playlistId}"
    headers = {
        "Authorization": "Bearer " + token
    }

    res = requests.get(url = playlistUrl, headers = headers)

    # Step 3 - Read the response
    data = json.loads(res.content)

    # Step 4 - Consolidate the results in a dataframe
    # Number of songs in the playlist
    n = len(data['tracks']["items"])
    # Column names
    names = ["position", "song", "song_id", "artists", "artists_id", "album", "album_id", "duration",
        "added_at", "popularity", "playlist", "playlistid"]
    df = pd.DataFrame(columns = names)
    playlist = data["name"]

    for i in range(0, n):  
        added_at = data['tracks']["items"][i]['added_at']
        try: 
            album = data['tracks']["items"][i]['track']['album']["name"]
        except:
            continue
        album_id = data['tracks']["items"][i]['track']['album']["id"]
        artists = [j["name"] for j in data['tracks']["items"][i]['track']['artists']]
        artists = ", ".join(artists)
        artists_id = [j["id"] for j in data['tracks']["items"][i]['track']['artists']]
        artists_id = ", ".join(artists_id)
        duration = data['tracks']["items"][i]['track']['duration_ms'] # Duration in ms
        song_id = data['tracks']["items"][i]['track']['id']
        song = data['tracks']["items"][i]['track']['name']
        popularity = data['tracks']["items"][i]['track']['popularity']
        position = i + 1

        row = pd.DataFrame([[position, song, song_id, artists, artists_id, album, album_id, duration,
            added_at, popularity, playlist, playlistId]], columns = names)
        df = df.append(row, ignore_index = True)

    return df
