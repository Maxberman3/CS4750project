import json, requests
from django.conf import settings
from django import forms

SONGKICK_KEY=settings.SONGKICK_KEY

def has_name_chars(form_data):
    for character in form_data:
        if character in "!@#$%^&*()~,./?;:1234567890}{<>-+=":
            print('{field} contains {character}')
            raise forms.ValidationError('You included a number or special character in a name or city field')
def songkickcall(artist_iterable):
    festivals={}
    api_key=SONGKICK_KEY
    for artist in artist_iterable:
        request_url="https://api.songkick.com/api/3.0/search/artists.json?apikey={}&query={}".format(api_key,artist)
        songkickrequest=requests.get(request_url)
        artist_data=json.loads(songkickrequest.text)
        if artist_data["resultsPage"]["status"]=="ok" and artist_data["resultsPage"]["totalEntries"]>0:
            artist_id=artist_data["resultsPage"]["results"]['artist'][0]['id']
            request_url="https://api.songkick.com/api/3.0/artists/{}/calendar.json?apikey={}&page=1".format(artist_id,api_key)
            songkickrequest=requests.get(request_url)
            tour_data=json.loads(songkickrequest.text)
            if tour_data["resultsPage"]["status"]=="ok" and tour_data["resultsPage"]["totalEntries"]>0:
                #print(tour_data)
                if tour_data["resultsPage"]["totalEntries"]<50:
                    for event in tour_data["resultsPage"]["results"]["event"]:
                        #print(event)
                        if event["type"] == "Festival":
                            festivalname=event["displayName"]
                            if festivalname not in festivals:
                                festivals[festivalname]={"score":1,"bands":[artist]}
                            else:
                                if artist not in festivals[festivalname]["bands"]:
                                    festivals[festivalname]["score"]+=1
                                    festivals[festivalname]["bands"].append(artist)
                else:
                    page=2;
                    while(tour_data["resultsPage"]["status"]=="ok" and tour_data["resultsPage"]["results"]):
                        #print(tour_data)
                        for event in tour_data["resultsPage"]["results"]["event"]:
                            if event["type"] == "Festival":
                                festivalname=event["displayName"]
                                if festivalname not in festivals:
                                    festivals[festivalname]={"score":1,"bands":[artist]}
                                else:
                                    if artist not in festivals[festivalname]["bands"]:
                                        festivals[festivalname]["score"]+=1
                                        festivals[festivalname]["bands"].append(artist)
                        request_url="https://api.songkick.com/api/3.0/artists/{}/calendar.json?apikey={}&page={}".format(artist_id,api_key,page)
                        songkickrequest=requests.get(request_url)
                        tour_data=json.loads(songkickrequest.text)
                        page+=1
    return festivals
