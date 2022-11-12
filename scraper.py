from bs4 import BeautifulSoup
import requests
import json
url_to_POST = "http://test.local/do_usage/web/jsonapi/node/project"
url_to_POST_ = "http://test.local/do_usage/web/jsonapi/node/project_usage"
headers = {'Accept': 'application/vnd.api+json', 
           'Content-type': 'application/vnd.api+json', 
           'Authorization': 'Basic YWxhbmFieTAxOkV2ZXJlc3RAODg0OA=='}

date_array = ["2022-10-30", "2022-10-23", "2022-10-16", "2022-10-9", "2022-10-2", "2022-9-28"]
def parse(name_box):
    date_index = 0
    for name in name_box:
        title = name.find('a').text
        code = name.find('a').get('href').split("/")[3]
        url = "https://www.drupal.org/project/"+name.find('a').get('href').split("/")[3]
        json_ =  {
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
        json_["data"]["attributes"]["title"] = title
        json_["data"]["attributes"]["field_project_code"] = code
        json_["data"]["attributes"]["field_project_url"] = url

        #print(json_["data"]["attributes"]["title"])
        #print(json_["data"]["attributes"]["field_project_code"])
        #print(json_["data"]["attributes"]["field_project_url"])
        json_object = json.dumps(json_, indent = 4) 
        response = requests.post(url_to_POST, headers=headers, data=json_object)
        print(response)
        usage_box = name.findAll('td',{'class':'project-usage-numbers'})
        for usage in usage_box:
            print(usage.text)
            json_ = {
            "data" : {
                "type": "node--project_usage",
                "attributes": {
                    "title": "",
                    "field_number_of_sites": "",
                    "field_usage_date": ""
                    }
                }
            }
            json_["data"]["attributes"]["title"] = 1
            json_["data"]["attributes"]["field_number_of_sites"] = usage.text.replace(',',"")
            json_["data"]["attributes"]["field_usage_date"] =  date_array[date_index]
            #print(json_["data"]["attributes"]["title"] )
            #print(json_["data"]["attributes"]["field_number_of_sites"] )
            #print(json_["data"]["attributes"]["field_usage_date"])
            json_object = json.dumps(json_, indent = 4) 
            try:
                response = requests.post(url_to_POST_, headers=headers, data=json_object)
            except: 
                continue
            print(response)
            date_index = (date_index + 1) % 6
for i in range(0, 10, 1):

    page_name = "./downloads/2022-11-10/usage_page-" + str(i) + ".html"
    file = open(page_name)
    html_doc = file.read()
    file.close()
    soup = BeautifulSoup(html_doc, "html.parser")

    #usage_html_box = soup.find('thead').findAll('a')
    #for bits in usage_html_box:
    #    print(bits.text)
    name_box = soup.findAll('tr', {'class': 'odd'})
    parse(name_box)
    name_box = soup.findAll('tr', {'class': 'even'})
    parse(name_box)