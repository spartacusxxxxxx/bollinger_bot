import smtplib
import time
import datetime
import numpy as np
import pprint
import requests
import json as jsn
from pymongo import MongoClient



def get_json(url):
    r = requests.get(url)
    return r.text


def moving_average(x, N):
    if (len(x)<3):
        print("x<3")
        return x[0]
    else:
        print("x>3")
        #return np.convolve(x, np.ones((N,)) / N)[(N - 1):]
        return np.convolve(x, np.ones((N,)) / N, mode='valid')




def main():
    # https: // api.coinmarketcap.com / v1 / ticker /?limit = 5
    while True:
        print ("This prints once a 5 minutes.")
        #time.sleep(300)


        #getting request
        url = "https://api.coinmarketcap.com/v1/ticker/?limit=1"
        json = get_json(url)
        #print(json)
        parced_json = jsn.loads(json)
        #print(parced_json[1])


        #db init
        client = MongoClient('localhost', 27017)
        db = client.crypto_database
        cryptocurrences = db.cryptocurrences


        #db insert data
        cryptocurrences.insert_many(parced_json)


        # show all Bitcoin prices in db
        #for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}):
            #pprint.pprint(cryptocurrency)
            #pprint.pprint(float(cryptocurrency[u'price_usd']))
            #running_avg.append(float(cryptocurrency[u'price_usd']))



        # calculating moving average for last updated price in result_to_update
        running_avg = []
        for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}).sort("last_updated", -1).limit(3):
            #pprint.pprint(cryptocurrency)
            #pprint.pprint(float(cryptocurrency[u'price_usd']))
            running_avg.append(float(cryptocurrency[u'price_usd']))
        result_to_update = moving_average(running_avg, 3)
        print(result_to_update)


        #creating 'mov_avg' for last_updated point
        for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}).sort("last_updated", -1).limit(1):
            result = cryptocurrency.update({u'mov_avg': float(result_to_update)})
            print(result)
            result = cryptocurrences.save(cryptocurrency)
            print(result)



        #deleting part of collection with condition
        #result = db.cryptocurrences.remove({u'name': "Bitcoin"})
        #print(result)



        # calculating numpy std for last updated price in result_to_update
        running_avg = []
        for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}).sort("last_updated", 1).limit(10):
            # pprint.pprint(cryptocurrency)
            # pprint.pprint(float(cryptocurrency[u'price_usd']))
            running_avg.append(float(cryptocurrency[u'price_usd']))
        result_to_update = np.std(running_avg)
        print(running_avg)
        print(result_to_update)



        # creating 'upper_bb_line' and 'lower_bb_line' for last_updated point
        for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}).sort("last_updated", -1).limit(1):
            #upper line
            print(float(cryptocurrency[u'mov_avg']))
            result = cryptocurrency.update({u'upp_bbl': float(cryptocurrency[u'mov_avg']) + 2 * float(result_to_update)})
            print(result)
            result = cryptocurrences.save(cryptocurrency)
            print(result)
            #lower line
            result = cryptocurrency.update({u'low_bbl': float(cryptocurrency[u'mov_avg']) - 2 * float(result_to_update)})
            print(result)
            result = cryptocurrences.save(cryptocurrency)
            print(result)



        #sending to e-mail with condition
        for cryptocurrency in cryptocurrences.find({u'name': u'Bitcoin'}).sort("last_updated", -1).limit(1):
            if float(cryptocurrency[u'mov_avg']) < float(cryptocurrency[u'low_bbl']) + (float(cryptocurrency[u'upp_bbl'])-float(cryptocurrency[u'low_bbl'])) * 0.05 and float(cryptocurrency[u'mov_avg']) > float(cryptocurrency[u'low_bbl']):
                addressee = []
                credentials = {}
                msg = "Subject: Price Alert (BTRX " + cryptocurrency[u'symbol'] + "/USD @ " + cryptocurrency[u'price_usd'] + ")" \
                      "Body: Price for " + cryptocurrency[u'name'] + " currency is within a buying range." \
                      "https://www.coinigy.com/main/markets/BTRX/" + cryptocurrency[u'symbol'] + "/USD." \
                      "Timestamp: " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
                with open('Usernames.txt', 'r') as f:
                    for line in f:
                        user, pwd = line.strip().split(':')
                        credentials[user] = pwd
                        break
                    for line in f:
                        user, pwd = line.strip().split(':')
                        addressee.append(user)
                        break
                for username in credentials:
                    print(username)
                    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)           # connecting to gmail
                    smtpObj.starttls()                                      # TLS(Transport Layer Security) on
                    smtpObj.login(username, credentials[username])
                    smtpObj.sendmail(username, addressee, msg)
                    smtpObj.quit()
                print(addressee)
            elif float(cryptocurrency[u'mov_avg']) < float(cryptocurrency[u'low_bbl']):
                addressee = []
                credentials = {}
                msg = "Subject: Price Alert (BTRX " + cryptocurrency[u'symbol'] + "/USD @ " + cryptocurrency[u'price_usd'] + ")" \
                       "Body: Price for " + cryptocurrency[u'name'] + " currency is within a selling range." \
                       "https://www.coinigy.com/main/markets/BTRX/" + cryptocurrency[u'symbol'] + "/USD." \
                        "Timestamp: " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
                with open('Usernames.txt', 'r') as f:
                    for line in f:
                        user, pwd = line.strip().split(':')
                        credentials[user] = pwd
                        break
                    for line in f:
                        user, pwd = line.strip().split(':')
                        addressee.append(user)
                        break
                for username in credentials:
                    print(username)
                    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)           # connecting to gmail
                    smtpObj.starttls()                                      # TLS(Transport Layer Security) on
                    smtpObj.login(username, credentials[username])
                    smtpObj.sendmail(username, addressee, msg)
                    smtpObj.quit()
                print(addressee)


        # show all database
        for cryptocurrency in cryptocurrences.find():
            pass
            #pprint.pprint(cryptocurrency)

        #delay for 5 minutes
        time.sleep(3000)



if __name__ == "__main__":
    main()