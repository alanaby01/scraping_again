from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool
import requests
import json
import os

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

def get_uuid(project_code):

    # The function is called after a project entity has been created. This function 
    # returns the internal uuid of the corresponding project entity referenced by the
    # project code. GET request URL is constructed by using a filtered request as given
    # in the documentation. 
    # https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/filtering

    GET_PROJECT = "http://dousage.local/jsonapi/node/project?filter[field_project_code]="
    GET_PROJECT = GET_PROJECT + project_code

    # Preparing for GET..
    response = requests.get(GET_PROJECT, headers=GET_HEADERS)

    # Parsing the response body to extract the required UUID of the entity.
    response_content = response.content.decode('utf8').replace("'", '"')
    json_content = json.loads(response_content)
    return json_content["data"][0]["id"]

def fill_and_post_project_payload(project_code, project_url):

    # Project payload template is contained in payload_project.json file. Loading 
    # the above JSON object

    payload_open = open("payload_project.json")
    payload_project_json = json.load(payload_open)

    # Populating JSON object with data for all the fields..
    payload_project_json["data"]["attributes"]["title"] = project_code
    payload_project_json["data"]["attributes"]["field_project_code"] = project_code
    payload_project_json["data"]["attributes"]["field_project_url"] = project_url

    #Preparing to POST...
    payload_project_txt = json.dumps(payload_project_json, indent=4) 
    response = requests.post(POST_PROJECT, headers=POST_HEADERS, data=payload_project_txt)
    print(response)

def fill_and_post_project_usage_payload(project_usage_title, number_of_sites, uuid, date):

    # Project usage payload template is contained in payload_project_usage.json file. Loading 
    # the above JSON object

    payload_open = open("payload_project_usage.json")   
    payload_project_usage_json = json.load(payload_open)

    # Populating JSON object with data for all the fields..
    # Here the entity reference to project entity is given using the field_usage_project_code.
    # It is given in the ["data"]["relationships"]["field_usage_project_code"]["data"]["id"]
    # as specified in the JSON API documentation 
    # https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/creating-new-resources-post

    payload_project_usage_json["data"]["attributes"]["title"] = project_usage_title
    payload_project_usage_json["data"]["attributes"]["field_number_of_sites"] = number_of_sites
    payload_project_usage_json["data"]["attributes"]["field_usage_date"] =  date
    payload_project_usage_json["data"]["relationships"]["field_usage_project_code"]["data"]["id"] = uuid

    # Preparing to POST...
    payload_project_usage_txt = json.dumps(payload_project_usage_json, indent=4) 
    response = requests.post(POST_PROJECT_USAGE, headers=POST_HEADERS, data=payload_project_usage_txt)
    print(response)

def parse_each_row(html_rows, date_array):
    date_index = 0
    for html_row in html_rows:

        # title = name.find('a').text
        # Extracting project data from each row: Here we assume that the first <a> tag in the HTML 
        # document contains the project code. Please change this if a change happens in the
        # HTML document

        project_code = html_row.find('a').get('href').split("/")[3]
        project_url = "https://www.drupal.org/project/" + project_code
        fill_and_post_project_payload(project_code, project_url)

        # Extracting project usage data from each row. To POST project usage data with an entity
        # reference field, the UUID of the project entity is required. We acheive this using the
        # get_uuid() function.

        html_usage_row = html_row.findAll('td', {'class':'project-usage-numbers'})
        uuid = get_uuid(project_code)
        for html_usage in html_usage_row:

            # Extracting data from each column of the row. Seperate usage entities are created
            # for each date columns. i,e each row will result in the creation of 6 usage entities
            # corresponding to each row.

            number_of_sites = html_usage.text.replace(',', "")
            project_usage_title = project_code + "-" + date_array[date_index]
            fill_and_post_project_usage_payload(project_usage_title, number_of_sites, uuid, date_array[date_index])

            # As a programming optimization, we don't seek to extract date headers every time. We 
            # extract date once in the main() function and seek to rotate over the array for 
            # each usage entry. Hence, line 83.
            date_index = (date_index + 1) % 6

def main(filename):
    #Opening file to read.
    path_of_html_file = os.path.join(DIRECTORY, filename)
    file = open(path_of_html_file)
    html_document = file.read()
    file.close()
    
    soup = BeautifulSoup(html_document, "html.parser")
    html_rows = soup.find('table').find('tbody').findAll('tr')

    date_array = []
    html_dates = soup.find('table').find('thead').findAll('th', {'class': 'project-usage-numbers'})
    for html_date in html_dates:
        date_array.append(str(datetime.strptime(html_date.text, "%b %d, %Y").strftime("%Y-%m-%d")))
    
    parse_each_row(html_rows, date_array)

if __name__ == '__main__':
    # Getting HTML filenames and loading them to an array.
    array_filename = []
    for filename in sorted(os.listdir(DIRECTORY)):
        array_filename.append(filename)
    
    # 10 processes are created and each are assigned a seperate file from arrat_filename
    with Pool(processes=10) as pool:
        pool.map(main, array_filename)