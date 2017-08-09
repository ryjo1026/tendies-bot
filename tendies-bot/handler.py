import datetime
import json
import logging
import os
import urllib
import urllib2

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def callGroupMe(message):
    """For each bot, use urllib to open a post request to the API"""
    ids = os.environ['botIDs'].split()

    for bot in ids:
        url = 'https://api.groupme.com/v3/bots/post'
        values = {'text': message, 'bot_id': bot}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        urllib2.urlopen(req)

def checkDiningHall(hall, itemInfo, nickname):
    """
    Recieves itemInfo for a specific dining hall and checks for being served tomorrow. Constructs message
    and calls GroupMe if Found
    """

    # Get time for tomorrow
    tomorrow = datetime.datetime.today()+datetime.timedelta(days=1)
    tomorrow = str(tomorrow)[:-16]
    logger.info('Tomorrow logged as: %s', tomorrow)

    # If hall found, try to find times
    if hall in itemInfo["diningHallMatches"]:
        times = itemInfo["diningHallMatches"][hall]["mealTimes"]
        logger.info('Found times in %s: %s', hall, times)
        for key in times.keys():
            # Compare truncated time to tommoroe
            if str(key[:-10]) == tomorrow:
                meal = times[key]["mealNames"]
                # If there are multiple meals, comma separate. Otherwise just convert to lower
                if len(meal) > 1:
                    meal = ', '.join(meal)
                    meal = meal.lower()
                else:
                    meal = meal.lower()
                # Make hall name friendly and create message string
                hallNickname = hall.replace(' Dining Hall', '')
                message = '{} for {} in {} tomorrow'.format(nickname, meal, hallNickname)
                logger.info('Sending the following message to GroupMe: %s', message)
                callGroupMe(message)

def main(event, context):
    diningHalls = ['Bursley Dining Hall', 'Mosher Jordan Dining Hall']

    # Items to alert for "formal name":"nickname"
    watchedItems = {"chicken tenders":"Tendies"}

    # Get full meal data from proxied API
    url = 'http://michigantendies.herokuapp.com/'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)

    mealData = json.loads(response.read())

    # Search for watched items in API one by one
    for item, nickname in watchedItems.items():
        logger.info('----------Checking for %s----------', item)
        if item in mealData["items"]:
            itemInfo = mealData["items"][item]
            logger.info('Found entry; checking dining halls/times')
            # If matching dining hall, continue checks
            for diningHall in diningHalls:
                checkDiningHall(diningHall, itemInfo, nickname)

if __name__ == '__main__':
    main(0, 0)
