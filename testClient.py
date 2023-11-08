import requests

# Define the API endpoint
url = "http://ec2-16-170-142-250.eu-north-1.compute.amazonaws.com//postImage"

pathBack = '1__canada-1-cent-1882.jpg'
pathFront = '18__canada-1-cent-1891.jpg'


with open(pathFront, 'rb') as fileFront, open(pathBack, 'rb') as fileBack:

    files = {'front': (pathFront, fileFront, 'image/jpg'),
             'back': (pathBack, fileBack, 'image/jpg')}
    headers = {'key': 'password'}
    response = requests.post(url, files=files, headers=headers)

print(response.text)
