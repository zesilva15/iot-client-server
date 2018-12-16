import datetime

###Funcao para transformar numero em key###
###Parametros de entrada : numero
###Valores de retorno : key
def num_to_key(num):
	if num == 1:
		return 'calls_missed'
	elif num == 2:
		return 'calls_received'
	elif num == 3:
		return 'calls_made'
	elif num == 4:
		return 'calls_duration'
	elif num == 5:
		return 'sms_sent'
	elif num == 6:
		return 'sms_received'
	elif num == 7:
		return 'location'
	elif num == 8:
		return 'activity'
	elif num == 9:
		return 'department'
	elif num == 10:
		return 'id'

###Funcao para transformar key em numero###
###Parametros de entrada : key
###Valores de retorno : numero
def key_to_num(key):
	if key == 'calls_missed':
		return 1
	elif key == 'calls_received':
		return 2
	elif key == 'calls_made':
		return 3
	elif key == 'calls_duration':
		return 4
	elif key == 'sms_sent':
		return 5
	elif key == 'sms_received':
		return 6
	elif key == 'location':
		return 7
	elif key == 'activity':
		return 8
	elif key == 'department':
		return 9
	elif key == 'id':
		return 10

###Funcao para dar as horas, minutos e segundos atuais###
###Parametros de entrada : nenhum
###Valores de retorno : [horas:minutos:segundos]
def curr_time():
	h = datetime.datetime.now().hour
	m = datetime.datetime.now().minute
	s = datetime.datetime.now().second
	tempo = '[%02.d:%02.d:%02.d]' % (h,m,s)
	return tempo

###Funcao para obter as keys que tem valores diferentes em dois dicionarios###
###Parametros de entrada : dicionario1 e dicionario2
###Valores de retorno : array com os as keys cujos valores foram alterados
def DictDiffer(current_dict,past_dict):
	set_current = set(current_dict.keys())
	set_past = set(past_dict.keys())
	intersect = set_current.intersection(set_past)

	returnSet = set()

	for elem in intersect:
		if past_dict[elem] != current_dict[elem]:
			returnSet.add(elem)

	return returnSet
