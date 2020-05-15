#!/usr/bin/python3
#*************************************************************
# Citrix ITM API
# Author : Jeff Hyeongjun Kim (hyeong.jun.k@gmail.com)
# *************************************************************/

import sys
import time
import requests
import json
import re
import argparse
import urllib.parse
import pandas as pd

# Variables
credentials = {'client_id': '[client_id]', 'client_secret': '[client_secret_key]', 'grant_type': 'client_credentials'}
cedexisApiUrl = 'https://portal.cedexis.com:443/api' # Reporting Docs
docsUrl = {
    'countries': '/v2/reporting/countries.json?',
    'networks': '/v2/reporting/networks.json?',
    'radar': '/v2/reporting/radar.json?geoLocateUsing=client',
    'platforms': '/v2/reporting/platforms.json/community',
    'regions': '/v2/reporting/regions.json'
}
access_token = 'a8e787ca-8adf-464e-aab1-4c0227d85ff2' # need to update when credentials changed

""" # Parser for command-line arguments. """
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('-d', '--docs', action='store', required=True, default=False, help='(Required) Reporting Live docs such as radar, networks, regions, countries, states, platforms, ...')
parser.add_argument('--token', action='store_true', default=False, help='(optional) Generate access token by credentials')
parser.add_argument('-m', '--measurementType', action='store', default='community_radar', help='(defatult: community_radar) Measurement Type such as community_radar, private_radar, ...')
parser.add_argument('-ms', '--measurementSource', action='store', default='community', help='(default: community) Measurement Source such as community, private')
parser.add_argument('-p', '--platformIds', action='store', default=False, help='(optional) CDNW Static:25, DWA EU/US/AP:56,54,57, SSL:17653, 41683(CDN360) ; comma separated platform IDs')
parser.add_argument('-pl','--platformListType', action='store', default=False, help='(optional) Platform List such as "hidden", "simple", "simple/hidden"')
parser.add_argument('-t', '--probeTypeIds', action='store', default=0, help='(default: 0) Response Time: 0 | Availability: 1')
parser.add_argument('-c', '--countryIds', action='store', default=False, help='(optional) countryIds China = 44 ; comman sepated country IDs')
parser.add_argument('-cn', '--country', action='store', default=False, help='(optional) country name China ; comman sepated country IDs')
#parser.add_argument('-ct', '--category', action='store', default=False, help='(optional) category for platform: "Cloud Computing" | "Cloud Storage" | "Delivery Networks" (Non-SSL) | "Dynamic Content" | "Managed DNS" | "Secure Object Delivery"')
parser.add_argument('-s', '--stateIds', action='store', default=False, help='(optional) stateIds Beijing = 1140851080 ; comman sepated state IDs')
parser.add_argument('-n', '--networkIds', action='store', default=False, help='(optional) networkIds  ASN number = 4134 CT ; comman sepated state IDs')
parser.add_argument('-tr', '--timeRange', action='store', default='last_4_hours', help='(default: last_1_days) Time Range Use one of the following formats: last_N_[minutes|hours|days|months], '+
    '[minute|hour|day|month]_to_date, YYYY-MM-DDThh:mm:ssZ/YYYY-MM-DDThh:mm:ssZ, ssssssssss/ssssssssss, N_to_M_[minutes|hours|days|months]_ago, yesterday, or today. '+
    'Examples: last_60_minutes, last_4_hours, last_3_days, month_to_date, 1_to_2_hours_ago.')
parser.add_argument('-r', '--results', action='store', default='networkId[limit:10;sort:measurements desc],mean', help='(optional, default = "networkId[limit:10;sort:measurements desc],mean") results parameter: e.g results=countryId,networkId,mean, '+
    'Examples: results="networkId[limit:10;sort:measurements desc],mean"')
parser.add_argument('-q', '--quite', action='store', default=0, help='(default: 0) quite mode: no return output via print')
parser.add_argument('-qr', '--query', action='store', default=False, help='(option) query for SQL Pandas Dataframe e.g. SELECT * FROM data_df LIMIT 5')

""" # Functions """
def getCurrTime():  # Get current time: format == Tue Feb 11 22:36:07 2020
    currTime = time.gmtime()
    #return '{0}|{1}'.format(time.ctime(time.mktime(currTime)), time.mktime(currTime))
    return '{0}'.format(time.ctime(time.mktime(currTime)))

def writeLog(joblogfile, jobtype, jobstep, jobdetail):
    """ Write job logs
    @joblogfile: path & name of logfile == logs/api_cedexis_{workyear}-{workmonth}.log
    @jobtype: 'start' / 'finish' / 'retry' / 'execute' / 'alert' / 'error'
    @jobstep: descriptiove name
    @jobdetail: number of objects, etc.
    """
    logfp = open (joblogfile, 'a')
    logmessage = '{0}|{1}|{2}|{3}\n'.format(getCurrTime(), jobstep, jobtype, jobdetail)
    logfp.write(logmessage)
    logfp.close()

def apiQuery(query):  # Generate API URL from params
    """ @query: (list) params for each API call """
    addUrl = docsUrl[query[0]]
    if query[0] == 'platforms': 
        if query[1] == True:
            addUrl = addUrl+'/'+query[1]
    else:
        if len(query) > 1:
            for q in query[1:]:
                if q.count("False") == 0:
                    addUrl = addUrl+'&'+q
                    
    return '{0}{1}'.format(cedexisApiUrl,addUrl)

""" # Script Start """
def main(argv):
    flags = parser.parse_args(argv[1:])
    trycount = 0
    workyear = time.gmtime().tm_year
    workmonth = time.gmtime().tm_mon
    joblogfile = '/usr/local/performance/scripts/logs/api_cedexis_{0}-{1}.log'.format(workyear, workmonth)
    writeLog(joblogfile, '[Info]', '[API:Cedexis]', 'API Start {0}'.format('='*40))
    data = ''

    if flags.token:
        requestToken = requests.post('https://api.cedexis.com/api/oauth/token', data=credentials)
        tokenInfo = json.loads(requestToken.content)
        print('Here is the access_token: {0}'.format(tokenInfo['access_token']))
        sys.exit()

    if flags.docs:
        if flags.docs == 'radar':
            query = [ flags.docs, 'measurementSource='+str(flags.measurementSource), 'platformIds='+str(flags.platformIds), 'probeTypeIds='+str(flags.probeTypeIds), 
            'countryIds='+str(flags.countryIds), 'timeRange='+str(flags.timeRange), 'results='+str(urllib.parse.quote_plus(flags.results)) ]
        elif flags.docs == 'networks' or flags.docs == 'regions':
            query = [ flags.docs, 'measurementType='+str(flags.measurementType), 'countryIds='+str(flags.countryIds) ]
        elif flags.docs == 'platforms':
            query = [ flags.docs, str(flags.platformListType) ]
        elif flags.docs == 'countries':
            query = [ flags.docs, 'measurementType='+str(flags.measurementType) ]
        else:
            query = [ flags.docs ]

        url = apiQuery(query)

        while True:
            try:
                data = requests.get(url, headers={'Authorization': 'Bearer' + access_token})
                writeLog(joblogfile, '[Info]', '[API:Cedexis]', 'Request API URL: {0}, Status Code: {1}'.format(url,data.status_code))
                data.raise_for_status()  # 200 = None, not 200 = exceptions.HTTPError => move to except
                data = json.loads(data.content)
                break
            except requests.exceptions.HTTPError as err:
                print(err)
                writeLog(joblogfile, '[Error]', '[API:Cedexis]', err)
                break
            except:
                trycount = trycount + 1
                requestToken = requests.post('https://api.cedexis.com/api/oauth/token', data=credentials)
                tokenInfo = json.loads(requestToken.content)
                access_token = tokenInfo['access_token']
                if not access_token:
                    writeLog(joblogfile, '[Warn]', '[API:Cedexis]', 'Failed to get access token: try count => {0}'.format(trycount))
                    time.sleep(5)  # seconds
                else:
                    writeLog(joblogfile, '[Info]', '[API:Cedexis]', 'Generated Access Token successfully with credentials [{0}]'.format(trycount))
                
    else:
        parser.print_help()

    """ Processing data 
        Steps
            - Top ASN by country with tiem period that given by options
            - Response time / Availability by country with time period that given by options
        @options
            Top ASN count: --count [number]
            time period: --start --end or --time 6h, 12h, 24h, 48h, ... (last xx hours)
            states level: --states
        @param
            Networks: Networks(ASN by ratio): https://portal.cedexis.com:443/api/v2/reporting/networks.json?countryIds=44&measurementType=community_radar
                countyIds: (optional) country id (44 = China)
                measurementType: community_radar
            States:
                countryIds: country id (44 = China): https://portal.cedexis.com:443/api/v2/reporting/states.json?countryIds=44&measurementType=community_radar
                measurementType: community_radar
            Radar: https://portal.cedexis.com:443/api/v2/reporting/radar.json?platformIds=....
                platformIds: platform id (25 = CDNW static)
                probeTypeIds: 0 (0=Http Response Time, 1=Http Connect Time, etc.)
                stateIds: Comma separated state IDs when added option --states + countryIds
                networkIds: comma separated network IDs, maximum of 50
                measurementSource: community
                geoLocateUsing: client (default) or resolver
                timeRange: eg. last_60_minutes
                    Use one of the following formats: last_N_[minutes|hours|days|months], [minute|hour|day|month]_to_date, 
                    YYYY-MM-DDThh:mm:ssZ/YYYY-MM-DDThh:mm:ssZ, ssssssssss/ssssssssss, 
                    N_to_M_[minutes|hours|days|months]_ago, yesterday, or today. Examples: last_60_minutes, last_4_hours, last_3_days, month_to_date, 1_to_2_hours_ago.
                results: e.g. 
                    response time: results=countryId,networkId,mean
                    availability: probeTypeIds should be 1. results=countryId,networkId,availability
                    https://github.com/cedexis/webservices/wiki/v2-Reporting-Endpoints#adhoc-results
                    Main data => read json from "facts"
                    NetworkId limit 5 per countryId => networkId[limit:5;sort:measurements desc] measurements = sample count
    """
    if data:  # data processing JOIN country, network(ASN) for analysis
        """ Data format type == JSON
        {'columns': ['networkId', 'mean'], 'meta': {'columns': [{'dimensions': ['networkId'], 'facts': ['mean']}], 'counts': {}, 'uri': '/api/result/002feb2b-88dc-45da-b1dc-238ce036de0e', 'id': '002feb2b-88dc-45da-b1dc-238ce036de0e',
        'overall': {}, 'version': '0.0.0', 'com.cedexis.aggapiclient.restfulClient': {'executionTimeMS': 68}, 'com.cedexis.aggapiclient.cache': {'cacheHit': False}, 'com.cedexis.aggapiclient.nameMappingClient': {'executionTimeMS': 0},
        'com.cedexis.aggapiclient.timeRangeAdjust': {'requestedTimeRanges': ['2020-02-11T18:00:00.000Z/2020-02-11T22:00:00.000Z'], 'effectiveTimeRanges': ['2020-02-11T18:00:00.000Z/2020-02-11T22:00:00.000Z'], 'now': '2020-02-11T22:36:07.420Z', 
        'timeScales': ['hour'], 'timeRangeAdjust': 'both'}, 'com.cedexis.aggapiclient.timeRangeTruncate': {'requestedTimeRanges': ['2020-02-11T18:36:00.000Z/2020-02-11T22:36:00.000Z'], 'truncatedTimeRanges': ['2020-02-11T18:00:00.000Z/2020-02-11T22:00:00.000Z']}, 
        'com.cedexis.aggapiclient.main': {'executionTimeMS': 71, 'factCount': 10}}, 'facts': [[4134, 25], [4837, 34], [9808, 64], [56044, 31], [132525, 31], [4812, 9], [56047, 21], [56041, 128], [56040, 26], [24547, 15]]}
        : requestedTimeRanges: '2020-02-11T18:36:00.000Z/2020-02-11T22:36:00.000Z' (default: 4 hours if no options)
        : columns
        : factCount: rawcount of facts
        : facts: data by columns
        """

        import pandas as pd
        from sqlalchemy import create_engine # SQL Engine to do in-memory SQL
        engine = create_engine('sqlite://', echo=False)  # Create an in-memory SQLite database.
        if flags.docs == 'platforms':
            temp = []
            for item in data:
                #temp.append([ {'id': item['id']}, {'name': item['name']}, {'category': item['category']['name']}, {'visibility': item['visibility']}, {'openmixEnabled': item['openmixEnabled']}])
                temp.append([item['id'], item['name'], item['category']['name'], item['publicChartEnabled']])
            data_df = pd.DataFrame(temp, columns=['id','name','category','is_public'])
            data_df.to_sql('data_df', engine) # Create SQL Table for each data : % Data should be type Dataframe
            query = flags.query if flags.query else """ SELECT * FROM data_df """
            result = pd.DataFrame(engine.execute(query).fetchall())
            if flags.quite:
                return result
            else: 
                print(result.to_csv(index=False))
        elif flags.docs == 'countries':
            temp = []
            for item in data:
                temp.append([item['id'], item['isoCode'], item['name'], item['overallPercent']])
            data_df = pd.DataFrame(temp, columns=['id','iso','name','ratio'])
            data_df.to_sql('data_df', engine) # Create SQL Table for each data : % Data should be type Dataframe
            query = flags.query if flags.query else """ SELECT * FROM data_df """
            result = pd.DataFrame(engine.execute(query).fetchall())
            if flags.quite:
                return result
            else: 
                print(result.to_csv(index=False))
        else:
            if flags.quite:
                return data
            else:
                print(data)

        """ move to ML
            4 hours data check .. if it has error per country by inspection model, add +4 hours or more and re-analysis by inspection model ...
            If hypothesis is true by t-test, determine this is error case.
            Purpose increasing accuracy by ML and modeling for continous data. Automatic error detection with less false positive case(false alarm). 
        """

if __name__ == '__main__':
    main(sys.argv)

""" 
### Usage for platforms: Get platform code
python citrix_itm_api.py -d platforms
{
    'id': 17653, 
    'name': 'CDNetworks SSL', 
    'openmixAlias': None, 
    'openmixEnabled': True, 
    'aliasedPlatform': None, 
    'indexId': 20483, 
    'visibility': 'community', 
    'category': {'id': 7, 'name': 'Secure Object Delivery'}, 
    'intendedUse': None, 
    'publicChartEnabled': True, 
    'sonarConfig': None, 
    'radarConfig': {'probeTypes': [{'id': 15}, {'id': 10}, {'id': 11}, {'id': 13}]}, 
    'geoConfig': None
},

### Usage for countries: Get country code
python citrix_itm_api.py -d countries
Result:
  {
    "id": 223,
    "isoCode": "US",
    "name": "United States",
    "overallPercent": 40.18,
    "subcontinent": {
      "id": 10,
      "isoCode": "021",
      "name": "Northern America",
      "continent": {
        "id": 3,
        "isoCode": "019",
        "name": "Americas"
      }
    },
    "market": {
      "id": 1,
      "isoCode": "NA",
      "name": "North America"
    }
  }, ...

### Usage for radar
# China, Top 10 ASN by smaple for MEAN
python citrix_itm_api.py -d radar -r "networkId[limit:10;sort:measurements desc],mean" -c 44 
Result:
{
    u'facts': [[4134, 31], [4837, 42], [9808, 56], [56040, 49], [4808, 13], [4812, 17], [23724, 61], [4816, 40], [24445, 31], [24444, 23]], 
    u'meta': {
        u'com.cedexis.aggapiclient.main': {u'executionTimeMS': 0, u'factCount': 10}, 
        u'com.cedexis.aggapiclient.nameMappingClient': {u'executionTimeMS': 0}, 
        u'com.cedexis.aggapiclient.cache': {u'cacheProvider': u'RedisCache', u'cacheHit': True}, 
        u'overall': {}, 
        u'uri': u'/api/result/9b0989e4-5e89-4097-abec-ef644095b48e', 
        u'com.cedexis.aggapiclient.timeRangeTruncate': {
            u'truncatedTimeRanges': [u'2019-03-25T18:00:00.000Z/2019-03-25T22:00:00.000Z'], 
            u'requestedTimeRanges': [u'2019-03-25T18:37:00.000Z/2019-03-25T22:37:00.000Z']
        }, 
        u'version': u'0.0.0', 
        u'com.cedexis.aggapiclient.restfulClient': {u'executionTimeMS': 80}, 
        u'com.cedexis.aggapiclient.timeRangeAdjust': {
            u'timeRangeAdjust': u'both', 
            u'effectiveTimeRanges': [u'2019-03-25T18:00:00.000Z/2019-03-25T22:00:00.000Z'], 
            u'now': u'2019-03-25T22:37:22.385Z', 
            u'timeScales': [u'hour'], 
            u'requestedTimeRanges': [u'2019-03-25T18:00:00.000Z/2019-03-25T22:00:00.000Z']
        }, 
        u'counts': {}, 
        u'id': u'9b0989e4-5e89-4097-abec-ef644095b48e', 
        u'columns': [{u'facts': [u'mean'], u'dimensions': [u'networkId']}]
    }, 
    u'columns': [u'networkId', u'mean']
}
Field: 
 - data = ['facts']
 - column = ['columns']

# Top 10 country for Top 10 ASN by sample for MEAN
python citrix_itm_api.py -d radar -r "countryId[limit:10;sort:measurements desc],networkId[limit:10;sort:measurements desc],mean" 
"""