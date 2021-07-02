
import requests
import random
import time
import json
import sys
from prettytable import PrettyTable
import numpy as np
import datetime

'''
global variables
'''

ENDPOINT = "things.ubidots.com"
DEVICE_LABEL = "reactor-nuclear"
VARIABLE_LABELS = []
for i in range(10):
    VARIABLE_LABELS.append("S%02i"%i)
vars = {}
for var in VARIABLE_LABELS:
    vars[var] = {"values": [], "timestamps": []}
TOKEN = "BBFF-U9WcLLXpk4EpdO4iSyPNHrZp8tM2Yg"
DELAY = 1  # Delay in seconds


def get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABELS[0],
            token=TOKEN):
    try:
        url = "http://{}/api/v1.6/devices/{}/{}?page_size=1".format(url,
                                                        device,
                                                        variable)

        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

        attempts = 0
        status_code = 400

        while status_code >= 400 and attempts < 5:
            #print("[INFO] Retrieving data, attempt number: {}".format(attempts))
            req = requests.get(url=url, headers=headers)
            status_code = req.status_code
            attempts += 1
            time.sleep(0.1)

        # print("[INFO] Results:")
        # print(req.text)
        return req.json()

    except Exception as e:
        print("[ERROR] Error posting, details: {}".format(e))


if __name__ == "__main__":
    go_back_n = 14
    for i in range(go_back_n):
        print("")
    while True:
        t1 = datetime.datetime.now()
        for var in VARIABLE_LABELS:
            sys.stdout.write("\033[%iA"%go_back_n) # go up n lines
            response = get_var(variable=var)

            if len(vars[var]["timestamps"]) == 0: #No hay valores registrados
                vars[var]["timestamps"].append(response["last_value"]["timestamp"])
                vars[var]["values"].append(response["last_value"]["value"])
            else:
                # Si es más nuevo que el último registrado
                if response["last_value"]["timestamp"] > vars[var]["timestamps"][-1]:
                    vars[var]["timestamps"].append(response["last_value"]["timestamp"])
                    vars[var]["values"].append(response["last_value"]["value"])

            # Crear Tabla
            t = PrettyTable(['ID', 'Mean', 'Std'])
            for var_name in VARIABLE_LABELS:
                if len(vars[var_name]['values'])==0:
                    t.add_row([var_name, '', ''])
                else:
                    t.add_row([var_name, "%.2f"%np.mean(vars[var_name]['values']), "%.2f"%np.std(vars[var_name]['values'])])

            # Imprimir Tabla
            print(t)
        t2 = datetime.datetime.now()
        d = t2-t1
        if d.seconds < 10:
            time.sleep(10-d.seconds)
