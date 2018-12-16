import requests
#url = "http://10.3.4.75:9014/v2/entities?options=keyValues&type=student&attrs=activity,calls_duration,calls_made,calls_missed,calls_received,department,location,sms_received,sms_sent"
url = "http://socialiteorion2.dei.uc.pt:9014/v2/entities?options=keyValues&type=student&attrs=activity,calls_duration,calls_made,calls_missed,calls_received,department,location,sms_received,sms_sent&limit=100"
headers = {'cache-control':"no-cache","fiware-servicepath":"/", "fiware-service":"socialite"}
r = requests.get(url, headers=headers)
#array em que cada indice e um dicionario com os dados de cada aluno
data = r.json()