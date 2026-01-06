import sys
import requests
from pprint import pprint
from credentials import orgID, tokenCC, client_id, client_secret, refresh_token  # Import the credentials from credentials.py
import time
from tabulate import tabulate
import json
import csv #test

# **********************************
# Retrieves the token from Webex CC
# **********************************

class WebexServiceAppTokenRetriever:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    def retrieve_token(self):
        # Make a POST request to the Webex API to obtain an access token.
        url = "https://webexapis.com/v1/access_token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        response = requests.post(url, headers=headers, data=payload)
        pprint(response)

        # If the request is successful, parse the response and return the access token.
        if response.status_code == 200:
            json_response = response.json()
            pprint(json_response)
            access_token = json_response["access_token"]
            refresh_token = json_response["refresh_token"]
            tokens = [access_token, refresh_token]
            return tokens  
            #return access_token
        else:
            raise Exception("Failed to retrieve access token: {}".format(response.status_code))



retriever = WebexServiceAppTokenRetriever(client_id, client_secret)
tokens = retriever.retrieve_token()
tokenCC = tokens[0]
refresh_token = tokens[1]


print("*"*122)
print("Success, New Webex Token generated")
print("")
print(f"Access token: {tokenCC}")
print("")
print(f"Refresh token: {refresh_token}")
print("")
print("*"*122)
print("")
print("Writing the new token to the credentials.py file in the same directory")
with open('credentials.py', 'r') as file:
    lines = file.readlines()

# Update the token line
new_lines = []
for line in lines:
    if line.startswith('tokenCC = '):
        new_lines.append(f"tokenCC = '{tokenCC}'\n")
        print("Token has been successfully updated in the credentials.py file!")
    else:
        new_lines.append(line)

# Write the updated contents back to credentials.py
with open('credentials.py', 'w') as file:
    file.writelines(new_lines)


# ***************************************************
# Webex CC API Calls in the following Sections!
# ***************************************************
def set_pod_number():
    # Prompt the user to enter a 3-digit number
    number = input("Enter your 2 digit pod identifier XX: ")

    # Check if the input is a 2-digit number
    if number.isdigit() and len(number) == 2:
        podNumber = int(number)
        print(f"Pod Number set to: {podNumber}")
        return podNumber
    else:
        print("Invalid input. Please enter a 2-digit number.")
        return None
def list_skill():
    url = f"https://api.wxcc-us1.cisco.com/organization/{orgID}/skill"

    payload = {}
    headers = { "Accept": "application/json", 
               "Content-Type": "application/json",
               "Authorization": "Bearer " + tokenCC}

    response = requests.request("GET", url, headers=headers, data=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        response_num = len(response_data)
        #pprint(response_data)
        if response.text:
            try:
                extracted_data = []
                for item in response_data:
                    response_info = {
                        "Name": item.get("name", "N/A"),
                        "Description": item.get("description", "N/A"),
                        "Skill Type": item.get("skillType", "N/A"),
                        "ID": item.get("id", "N/A")
                     }
                    extracted_data.append(response_info)

                # Create and print the table
                print("Table of all Skill Definitions")
                print(tabulate(extracted_data, headers="keys", tablefmt="grid"))
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from response: {response_data.text}")
        else:
            print("Received an empty response.")
    else:
        print(f"Received unexpected status code {response.status_code}: {response.text}")

    print("-" * 50)
    print("-" * 50)
    print("Number of Skills : " + str(response_num))
    print("-" * 50)
    print("-" * 50)

def write_to_csv(name, id, other, outputFile):  #write the created id, name and skillType to a csv file 
    with open( outputFile, "a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([name, id, other])

def read_csv(file_name):
    with open(file_name, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return list(reader)

def create_skill():
    # Read each line from a csv text file called "skills.csv"
    url = f"https://api.wxcc-us1.cisco.com/organization/{orgID}/skill"
    headers = { "Accept": "application/json", 
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenCC}
    with open("skills.csv", "r") as file: # open the file in read mode
        csvreader = csv.reader(file) # create a csv reader object
        next(csvreader) # skip the header row
        for line in csvreader: # loop through each line
             #Assign the values from the line to the corresponding variables
            active = line[0]
            name = line[1]
            serviceLevelThreshold = line[2]
            skillType = line[3]
            description = line[4]

            # Put the values in the body
            payload = {
                "active": True,
                "name": name,
                "serviceLevelThreshold": serviceLevelThreshold,
                "skillType": skillType,
                "description": description
            }
            payload = json.dumps(payload)
            # pprint(payload)
            # print(url)

            # Make a POST request to the API to create a new skill
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 201: # check if the request was successful
                print(f"Created skill:{name}")
                response_data = response.json()
                skill_id = response_data.get("id")
                skill_type = response_data.get("skillType")
                outputFile = "skillsCreated.csv"
                write_to_csv(name, skill_id, skill_type, outputFile)
            else: # handle errors
                print(f"Failed to create skill: {name}")
                print(f"Received unexpected status code {response.status_code}: {response.text}")

list_skill()
podNumber = str(set_pod_number())
create_skill()
list_skill
print("WxCCA Script Completed!")