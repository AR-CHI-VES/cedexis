# *************************************************************
# Citrix ITM API
# Author : Jeff Hyeongjun Kim (hyeong.jun.k@gmail.com)
# *************************************************************/

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