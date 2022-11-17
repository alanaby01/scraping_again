import requests
import json
URL = "http://dousage.local/jsonapi/node/project?filter[field_project_code]=schema"
HEADERS = {'Accept': 'application/vnd.api+json',
           'Authorization': 'Basic YWxhbmFieTAxOkV2ZXJlc3RAODg0OA=='}

GET_projects = requests.get(URL, headers = HEADERS)
my_json = GET_projects.content.decode('utf8').replace("'", '"')
data = json.loads(my_json)
s = json.dumps(data, indent=4, sort_keys=True)
print(data["data"][0]["id"])
# 825e294b-c9c6-4506-bed7-bf55c39574c6
# 290bf3e7-276d-49d6-b889-2ac9825b067b
# 1d32b76f-4919-4b1b-bc67-ffaa6985d24a
# 841a5847-0d49-44e0-a27b-b5a43118cf23
# 9f205344-5144-41a3-a941-5f3d7c1a64c4
# 1ad5438b-9344-4482-9d0c-1fabd985bab5
# 6a4f06a4-1c67-4b8d-9c4f-dd5d505626ab
# 3418eb6a-2793-49de-aec6-3792563fcb7f
# 9b170e28-af54-4ae7-a827-e4e2bdae26d7
# 65a3104f-b032-400d-8ab6-b67102d36bd6