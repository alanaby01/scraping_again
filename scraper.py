from bs4 import BeautifulSoup
from datetime import datetime
import multiprocessing
import requests
import json
import os
import time
# POST_PROJECT : URL to which POST is made to create the Project Content.
# POST_PROJECT_USAGE : URL to which POST is made to create the Project Usage Content.
# GET_PROJECT : URL to which GET request is made to get UUID's of project entities.
# HEADERS: 'Accept' and 'Content-type' keys have standard values. 'Authorization' key is local to the system.

POST_PROJECT = "http://dousage.local/jsonapi/node/project"
POST_PROJECT_USAGE = "http://dousage.local/jsonapi/node/project_usage"

GET_HEADERS = { 'Accept': 'application/vnd.api+json',
                'Authorization': 'Basic YWxhbmFieTAxOkV2ZXJlc3RAODg0OA==' }

POST_HEADERS = { 'Accept': 'application/vnd.api+json', 
                 'Content-type': 'application/vnd.api+json', 
                 'Authorization': 'Basic YWxhbmFieTAxOkV2ZXJlc3RAODg0OA==' }

DIRECTORY = "./downloads/2022-11-10/"

def get_uuid(code):
    GET_PROJECT = "http://dousage.local/jsonapi/node/project?filter[field_project_code]="
    GET_PROJECT = GET_PROJECT + code
    get = requests.get(GET_PROJECT, headers = GET_HEADERS)
    content = get.content.decode('utf8').replace("'", '"')
    json_content = json.loads(content)
    return json_content["data"][0]["id"]

def parse(name_box, date_array):
    date_index = 0
    for name in name_box:
        # title = name.find('a').text
        code = name.find('a').get('href').split("/")[3]
        url = "https://www.drupal.org/project/" + name.find('a').get('href').split("/")[3]
        payload_project =  {
        "data": {
            "type": "node--project",
            "attributes": {
                "title":  "",
                "field_project_code": "",
                "field_project_name": "",
                "field_project_url": ""
                }
            }
        }
        payload_project["data"]["attributes"]["title"] = code
        payload_project["data"]["attributes"]["field_project_code"] = code
        payload_project["data"]["attributes"]["field_project_url"] = url

        # print(json_["data"]["attributes"]["title"])
        # print(json_["data"]["attributes"]["field_project_code"])
        # print(json_["data"]["attributes"]["field_project_url"])
        json_object = json.dumps(payload_project, indent = 4) 
        response = requests.post(POST_PROJECT, headers=POST_HEADERS, data=json_object)
        print(response)
        usage_box = name.findAll('td',{'class':'project-usage-numbers'})
        uuid = get_uuid(code)
        for usage in usage_box:
            number_of_sites = usage.text.replace(',',"")
            payload_project_usage = {
            "data" : {
                "type": "node--project_usage",
                "attributes": {
                    "title": "",
                    "field_number_of_sites": "",
                    "field_usage_date": "",
                },
                "relationships": {
                    "field_usage_project_code": {
                        "data": {
                            "type": "node--project",
                            "id": ""
                            }
                        }
                    }
                }
            }
            title_project_usage = code + "-" + date_array[date_index]
            payload_project_usage["data"]["attributes"]["title"] = title_project_usage
            payload_project_usage["data"]["attributes"]["field_number_of_sites"] = number_of_sites
            payload_project_usage["data"]["attributes"]["field_usage_date"] =  date_array[date_index]
            #payload_project_usage["data"]["attributes"]["field_project_code"] = code
            payload_project_usage["data"]["relationships"]["field_usage_project_code"]["data"]["id"] = uuid

            # print(json_["data"]["attributes"]["title"] )
            # print(json_["data"]["attributes"]["field_number_of_sites"] )
            # print(json_["data"]["attributes"]["field_usage_date"])
            json_object = json.dumps(payload_project_usage, indent = 4) 
            response = requests.post(POST_PROJECT_USAGE, headers=POST_HEADERS, data=json_object)
            print(response)
            date_index = (date_index + 1) % 6

for filename in sorted(os.listdir(DIRECTORY)):
    date_array = []
    pathname = os.path.join(DIRECTORY, filename)
    file = open(pathname)
    html_doc = file.read()
    file.close()
    soup = BeautifulSoup(html_doc, "html.parser")
    date_box = soup.findAll('th', {'class': 'project-usage-numbers'})
    for date in date_box:
        date_array.append(str(datetime.strptime(date.text, "%b %d, %Y").strftime("%Y-%m-%d")))
    name_box = soup.findAll('tr', {'class': 'odd'})
    parse(name_box, date_array)
    name_box = soup.findAll('tr', {'class': 'even'})
    parse(name_box, date_array)