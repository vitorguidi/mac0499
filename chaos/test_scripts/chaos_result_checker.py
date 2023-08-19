import os
import requests, json, uuid

spira_api_base_url = os.environ["SPIRA_API_BASE_URL"]
user = os.environ["SPIRA_USER"]
password = os.environ["SPIRA_PASSWORD"]
log_file = os.environ["CHAOS_LOG_FILE"]

f = open(log_file, 'r')

def main():
    (user_id, token, token_type) = get_token()
    inferences = get_all_inferences(user_id, token)
    inference_status = build_inference_map(inferences)
    failed_inference_acks = 0
    ack_and_completed_inferences = 0
    ack_and_not_completed_inferences = 0
    for inference_id in f.readlines():
        inference_id = inference_id.strip('\n') #reading from file gives us string with \n, will not hash properly on dict
        if inference_id == "connection failed" or inference_id == "internal error":
            failed_inference_acks += 1
        else:
            if inference_id not in inference_status:
                ack_and_not_completed_inferences += 1
            elif inference_status[inference_id] != "completed":
                ack_and_not_completed_inferences += 1
            else:
                ack_and_completed_inferences += 1
    result = {
        "failed_inference_acks": failed_inference_acks,
        "ack_and_completed_inferences": ack_and_completed_inferences,
        "ack_and_not_completeed_inferences": ack_and_not_completed_inferences
    }
    print(json.dumps(result))
    

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

def get_all_inferences(user_id, token):
    url = '{}/v1/users/{}/inferences'.format(spira_api_base_url, user_id)
    try:
        response = requests.get(
            url,
            headers = {
                "Authorization": "bearer {}".format(token)
            }            
        )

        if response.status_code != 200:
            response.raise_for_status()

        inferences = json.loads(response.content)

        return inferences["inferences"]

    except requests.exceptions.RequestException as e:
        raise(e)

def build_inference_map(inferences):
    result = {}
    for inference in inferences:
        result[inference["id"]] = inference["status"]
    return result

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False
    
main()