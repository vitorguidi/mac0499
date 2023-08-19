import os
import requests, json
import uuid
import signal
import sys
import time


spira_api_base_url = os.environ["SPIRA_API_BASE_URL"]
user = os.environ["SPIRA_USER"]
password = os.environ["SPIRA_PASSWORD"]

f = open('test_run_{}.txt'.format(str(uuid.uuid4())), 'a')

def signal_handler(sig, frame):
    print('Gracefully exiting {}'.format(sig))
    f.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    flood_and_log()

def flood_and_log():
    while True:
        try:
            (user_id, token, token_type) = get_token()
            inf_id = register_inference(user_id, token)
            f.write(inf_id + "\n")
        except(requests.ConnectionError):
            f.write("connection failed\n")
        except(requests.HTTPError) as e:
            f.write(e.errno)

def get_token():
    
    url = '{}/v1/users/auth'.format(spira_api_base_url)
    
    try:
        response = requests.post(
            url, 
            data = {
                "username": user,
                "password": password
            },
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }            
        )

        json_response = json.loads(response.content)

        if response.status_code != 200:
            response.raise_for_status()

        return (json_response["id"], json_response["access_token"], json_response["token_type"])


    except requests.exceptions.RequestException as e:
        raise(e)

def register_inference(user_id, token):
    url = '{}/v1/users/{}/inferences'.format(spira_api_base_url, user_id)
    try:
        response = requests.post(
            url, 
            data = create_inference_data(user_id),
            files = create_inference_files(),
            headers = {
                "Authorization": "bearer {}".format(token)
            }            
        )

        if response.status_code != 200:
            response.raise_for_status()

        inf_id = json.loads(response.content)['inference_id']

        return inf_id

    except requests.exceptions.RequestException as e:
        raise(e)



def create_inference_data(user_id):
    return {
        "gender": "M",
        "age": 23,
        "rgh": "fake_rgh",
        "covid_status": "Sim",
        "mask_type": "None",
        "user_id": "64ded714897b146391ac40c9",
        "model_id": "64ded756a5c219a0b2c6b660",
        "status": "processing",
        "local": "hospital_1",
        "cid": "fake_cid",
        "bpm": "fake_bpm",
        "created_in": "2022-07-18 17:07:16.954632",
        "respiratory_frequency": "123",
        "respiratory_insufficiency_status": "Sim",
        "location": "h1",
        "last_positive_diagnose_date": "",
        "hospitalized": "TRUE",
        "hospitalization_start": "2022-07-18 17:07:16.954632",
        "hospitalization_end": "2022-07-18 17:07:16.954632",
        "spo2": "123"
    }

def create_inference_files():
    return {
        "aceite": open("./mock_data_1.txt", "rb"),
        "sustentada": open("./mock_data_2.txt", "rb"),
        "parlenda": open("./mock_data_3.txt", "rb"),
        "frase": open("./mock_data_4.txt", "rb"),
    }

main()