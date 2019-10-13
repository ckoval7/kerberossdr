import teslajson
import json
from time import sleep

#Set up Tesla Login
tesla_c = teslajson.Connection(tokens_file="./tokens.txt")
tesla_v = tesla_c.vehicles[0]
tesla_v.wake_up()

while True:
    response = json.dumps(tesla_v.get("data_request/drive_state"))
    json_response = json.loads(response)
    json_drive_state = json.loads(json.dumps(json_response["response"]))
    latitude = json_drive_state["latitude"]
    longitude = json_drive_state["longitude"]
    heading = json_drive_state["heading"]

    f = open("/ram/TeslaLocation.txt","w+")
    f.write(str(json_drive_state["latitude"]) +
        "\n" + str(json_drive_state["longitude"]) +
        "\n" + str(json_drive_state["heading"]))
    f.close()
    #print("Location updated")
    sleep(1)
