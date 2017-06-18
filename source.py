import vk
import cognitive_face as FaceAPI
import json
import http.client, urllib.request, urllib.parse, urllib.error
import ast
from datetime import datetime, date

# keys for vk and cog service
token = 'here you vk token'
faceapi_key = 'here you faceapi key'

# init vk
session = vk.Session(access_token=token)
vk_api = vk.API(session)

# load friends
friends = vk_api.friends.get(user_id=62552420, fields='domain, sex, bdate, photo_200_orig')

# collecting data from friends and write it in json

#get sex info
def sex(person):
    if person['sex'] == 1:
        return 'female'
    elif person['sex'] == 2:
        return 'male'
    else:
        return 'N\A'

# get age info
def age(person):
    if 'bdate' in person:
        s = person['bdate']
        if s.count('.') > 1:
            today = date.today()
            dt = datetime.strptime(s, "%d.%m.%Y").date()
            person_age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
            return person_age
        else:
            return 0
    else:
        return 0

# analyze image with microsoft cognitive api
def get_photos_url(id):
    return vk_api.photos.getAll(owner_id=id, photo_sizes=0)


def run_analyzer(url):
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'cbfb0d1b4cd84f03ae1a4a839b169fbf',
    }

    params = urllib.parse.urlencode(
        {
            'visualFeatures': 'tags',
            'language': 'en',
        }
    )
    body = "{'url':'" + url + "'}"
    conn = http.client.HTTPSConnection('westeurope.api.cognitive.microsoft.com')
    conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    conn.close()
    data = ast.literal_eval(data)
    #fp = open("analyze.json", "w")
    #json.dump(data, fp, indent=4)
    #fp.close()
    return data


def find_cat(data, url):
    for i in range(len(data['tags'])):
        if (data['tags'][i]['name'] == 'outdoor' ) and data['tags'][i]['confidence'] > 0.5 :
            return True
    return False

def analyze_image(id):
    photos = get_photos_url(id)
    n = len(photos) - 1
    word_counter = 0
    for i in range(1, n):
        data = run_analyzer(photos[i]['src_big'])
        if 'tags' in data and find_cat(data, photos[i]['src_big']) :
            word_counter += 1
    return word_counter

data = {
    'persons' :
    [

    ]
}
person = {
    'id': '',
    'photo_id': '',
    'age': '',
    'sex': '',
    'friends_count': 0,
}

for f in friends:
    if f['photo_200_orig'] != 'https://vk.com/images/deactivated_200.png':
        person['id'] = f['uid']
        person['photo_id'] = f['photo_200_orig']
        person['sex'] = sex(f)
        person['age'] = age(f)
        data['persons'].append(person.copy())
fp = open('base.json', 'w')
json.dump(data, fp, indent=4)
fp.close()


age_data = {}
gen_data = {}
count = 0
print(data['persons'])
for i in range(100):
    n = data['persons'][i]['age']
    m = data['persons'][i]['sex']
    if n not in age_data:
        age_data[n] = analyze_image(data['persons'][i]['id'])
    else :
        age_data[n] += analyze_image(data['persons'][i]['id'])
    if m not in gen_data:
        gen_data[m] = analyze_image(data['persons'][i]['id'])
    else:
        gen_data[m] += analyze_image(data['persons'][i]['id'])
    count += 1
    print("Processing : ",  count ,  "%")

age_fp = open('age.json', 'w')
gen_fp = open('gen.json', 'w')
json.dump(age_data, age_fp, indent=4)
json.dump(gen_data, gen_fp, indent=4)
age_fp.close()
gen_fp.close()





# init face api
#FaceAPI.Key.set(faceapi_key)
#img_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
#result = FaceAPI.face.detect(friends[1]["photo_200_orig"])
#print(result)
