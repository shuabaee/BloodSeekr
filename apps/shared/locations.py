"""Geographic UI and coordinates, encoded in existing ERD text columns."""
import json
import math
import re
from functools import lru_cache
from pathlib import Path
PREFIX = 'BS1:'
@lru_cache(maxsize=1)
def catalog():
    return json.loads((Path(__file__).parent/'data'/'places.json').read_text(encoding='utf-8'))
@lru_cache(maxsize=1)
def city_index():
    return {c['id']:{**c,'country':country,'province_name':data['regions'].get(c['region'],'')} for country,data in catalog().items() for c in data['cities']}

def valid_point(lat,lng):
    try:
        lat,lng=float(lat),float(lng)
        if math.isfinite(lat) and math.isfinite(lng) and -90<=lat<=90 and -180<=lng<=180:
            return (lat,lng)
    except (TypeError,ValueError):
        pass
    return None

def unpack(value):
    value = str(value or '')
    blank={'country':'','province':'','city':'','address':'','point':None,'precision':'legacy','legacy':value}
    if value.startswith(PREFIX):
        try:
            row=json.loads(value[len(PREFIX):])
            if not isinstance(row,list) or len(row)!=7:
                return blank
            country,province,city,lat,lng,address,precision=row
            if not all(isinstance(x,str) for x in [country,province,city,address,precision]):return blank
            if (lat is not None or lng is not None) and not valid_point(lat,lng):return blank
            return {'country':country,'province':province,'city':city,'address':address,'point':valid_point(lat,lng),'precision':precision,'legacy':''}
        except (TypeError,ValueError):
            return blank
    coords=value.split(',')
    if len(coords)==2:
        blank['point']=valid_point(*coords)
        if blank['point']:blank['precision']='pin'
    return blank

def pack(country,province,city,lat,lng,address='',precision='pin'):
    point=valid_point(lat,lng)
    return PREFIX+json.dumps([country,province,city,round(point[0],5) if point else None,round(point[1],5) if point else None,address,precision],ensure_ascii=False,separators=(',',':'))

def city_name(value):
    item=unpack(value)
    city=item['city']
    if city.startswith('~'):return city[1:]
    return city_index().get(city,{}).get('name','') or item['legacy']

def display_location(value):
    item=unpack(value)
    if item['legacy']:return item['legacy']
    region=catalog().get(item['country'],{}).get('regions',{}).get(item['province'],item['province'].removeprefix('~'))
    country=catalog().get(item['country'],{}).get('name',item['country'])
    return ', '.join(dict.fromkeys(x for x in [item['address'],city_name(value),region,country] if x))

def coordinates(value):
    return unpack(value)['point']

def distance_km(first,second):
    a,b=coordinates(first),coordinates(second)
    if not a or not b:return None
    lat1,lon1,lat2,lon2=map(math.radians,(*a,*b))
    h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371*2*math.asin(math.sqrt(min(1,max(0,h))))

def normalize(value):
    return ' '.join(re.sub(r'[^\w\s]',' ',str(value).casefold()).split())

def location_matches(first,second,radius):
    distance=distance_km(first,second)
    if distance is not None:return distance<=radius
    a,b=unpack(first),unpack(second)
    if a['country'] and b['country'] and a['country']!=b['country']:return False
    if a['city'] and b['city']:return a['country']==b['country'] and a['city']==b['city']
    # Legacy records keep their original same-locality matching behavior.
    one,two=normalize(city_name(first)),normalize(city_name(second))
    return bool(one) and one==two

def locate_legacy(value):
    item=unpack(value)
    if item['country'] or not item['legacy']:return item
    name=normalize(item['legacy'])
    found=[c for c in catalog()['PH']['cities'] if normalize(c['name'])==name]
    if len(found)==1:
        c=found[0];return {**item,'country':'PH','province':c['region'],'city':c['id']}
    return item

def directions_url(value):
    from urllib.parse import urlencode
    point=coordinates(value)
    destination=','.join(str(x) for x in point) if point else display_location(value)
    return 'https://www.google.com/maps/dir/?'+urlencode({'api':1,'destination':destination})
