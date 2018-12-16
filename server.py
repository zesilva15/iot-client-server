#!/usr/bin/python           # This is server.py file

import socket              
import sys
import importAPI
import time
import copy
import requests
import os
from threading import Thread
from funcoesDeEnvio import send_msg
from funcoesDeEnvio import recv_msg
from funcoesDeEnvio import recvall
from funcoesAuxiliares import num_to_key
from funcoesAuxiliares import curr_time
from funcoesAuxiliares import key_to_num
from funcoesAuxiliares import DictDiffer

subscricoes = []
data = importAPI.data
condicao = True
#Indica o numero de clientes ligados atualmente
utilizadores = 0
#Indica o ID (de 1 ate n, em que n e o numero de clientes) do cliente atual
ID_cliente = 0
tempo = 1

###Inicializar os sockets e criar as threads###
###Parametros de entrada : nenhum
###Valores de retorno : referencia do socket das notificacoes e do socket 'principal'
def startup():
	global utilizadores
	global ID_cliente
	global tempo

	while True:
		tempo = raw_input('Introduza de quanto em quanto tempo quer atualizar a API: ')
		try:
			tempo = float(tempo)
			if type(tempo) is not float:
				print 'Introduza um valor inteiro/decimal'
				continue
			else:
				break
		except:
			print 'Introduza um valor inteiro/decimal'

	print 'Ok. Esperando por uma conexao...'
	
	#Cria os sockets TCP
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
	notificaSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
	#Evita problemas como "adress already is use", escolhendo automaticamente addresses e portos diferentes se os escolhidos ja estiverem a ser usados
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	notificaSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	  
	IP_address = "127.0.0.1"
	Port1 = 9000 
	Port2 = Port1 + 1

	try:
		s.bind((IP_address, Port1))   
		notificaSocket.bind((IP_address,Port2))
	except:
		print "Error binding"
		sys.exit()

	#Escuta ate len(data) clientes, o numero total de clientes da API
	s.listen(len(data))               
	notificaSocket.listen(len(data))


	while True:
		c, addr = s.accept()     
		print curr_time(),'Socket 1 : Got connection from', addr
		c.send(str(addr))

		notSocket, address = notificaSocket.accept()
		print curr_time(),'Socket 2: Got connection from', address
		notSocket.send(str(address))

		#Cria as threads do servidor assim como associa a cada utilizador um ID unico
		#Utilizadores indica o numero de utilizadores atualmente ligados ao servidor(se for 0 entao o servidor desliga-se)
		try:
			utilizadores+=1
			ID_cliente+=1
			ID = '[%d]' % ID_cliente
			Thread(target=main, args=(c,notSocket,ID)).start()
		except:
			print "Erro ao iniciar thread"
			sys.exit()

###Cliente dar login no servidor. Tem 3 tentativas###
###Parametros de entrada : socket das notificacoes e socket 'principal'
###Valores de retorno : em caso de sucesso, o indice do utilizador no array da API
def login(c,notificaSocket,Num_cliente):
	tentativas = 2
	while tentativas >= 0:
		ID = recv_msg(c)
		i = verificaID(ID)
		if i != False:
			send_msg(c,'Success')
			return i
		else:
			str(tentativas)
			send_msg(c,str(tentativas))
		tentativas-=1

	print Num_cliente,curr_time(),'Numero maximo de tentativas excedido!'
	#Caso o cliente exceda o numero maximo de tentativas(3), entao termina a sua thread de servidor
	terminate(c,notificaSocket)

###Calcula a media de um dado###
###Parametros de entrada : dado a calcular a media(chave desse no dicionario)
###Valores de retorno : em caso de a chave ter um valor inteiro associado, retorna a media. Em caso da chave ter uma String associada, devolve a mais frequente
def media(chave):
	cont = 0
	arr = []
	#Vai buscar todos os valores associados a chave
	for i in range(len(data)):
		pessoa = data[i]
		for key, value in pessoa.items():
			if key == chave:
				#armazenar o tipo do valor
				sample = value
				arr.append(str(value))
				cont += 1
	#Se o valor for inteiro, calcula a media
	if type(sample) is int:
		arr = map(int,arr)
		avg = sum(arr)/cont
		return avg
	#Se o valor for unicode(string)
	elif type(sample) is unicode:
		maisComum = max(set(arr), key=arr.count)
		return maisComum

###Obter o valor associado a chave do utilizador com indice i do array###
###Parametros de entrada : chave e indice do utilizador no array
###Valores de retorno : em caso de sucesso, o valor. Em caso de insucesso, 'ERROR'
def search_key(chave,i):
	for key, value in data[i].items():
		if(key == chave):
			return value
	#se nao encontrar
	return 'ERROR'

###Verificar se o ID dado existe na API###
###Parametros de entrada : um ID
###Valores de retorno : em caso de sucesso, o indice do utilizador com ID = ID. Em caso de insucesso, False
def verificaID(ID):
	for i in range(len(data)):
		pessoa = data[i]
		for key, value in pessoa.items():
			if(key == 'id' and value == ID):
				return i

	return False

###Funcao executada pela Thread para atualizar a API###
###Parametros de entrada : o socket das notificacoes e o indice do utilizador no array da API
###Valores de retorno : nenhum
def atulizaAPI(notificaSocket,index_ID):
	global data
	while condicao == True:
		if not subscricoes:
			send_msg(notificaSocket,'Empty')
			continue

		#Recebe a API
		#url = "http://10.3.4.75:9014/v2/entities?options=keyValues&type=student&attrs=activity,calls_duration,calls_made,calls_missed,calls_received,department,location,sms_received,sms_sent"
		url = "http://socialiteorion2.dei.uc.pt:9014/v2/entities?options=keyValues&type=student&attrs=activity,calls_duration,calls_made,calls_missed,calls_received,department,location,sms_received,sms_sent&limit=100"
		headers = {'cache-control':"no-cache","fiware-servicepath":"/", "fiware-service":"socialite"}
		r = requests.get(url, headers=headers)
		newData = r.json()

		lista = []
		#Notificacoes individuais
		if data[index_ID] != newData[index_ID]:
			#Obtemos as keys dos paramentros alterados
			diferenca = DictDiffer(newData[index_ID], data[index_ID])
			for e in diferenca:
				#Transformar a key em valor
				num = key_to_num(str(e))
				#Formatar para a nossa lista de notificacoes e adicionar o elemento
				notificao = "1.%d" % num
				lista.append(notificao)

		#Notificacoes de grupo
		for i in range(len(data)):
			#Obtemos as keys dos paramentros alterados
			diferenca = DictDiffer(newData[i],data[i])
			for e in diferenca:
				num = key_to_num(str(e))
				#Formatar para a nossa lista de notificacoes e adicionar o elemento
				notificao = "2.%d" % num
				lista.append(notificao)
		#Deepcopy para alterar o valor
		data = copy.deepcopy(newData)

		#Ver quais os elementos em comum da lista das subscricoes e notificacoes
		comuns = list(set(lista) & set(subscricoes))
		comuns_enviar = ' '.join(comuns)

		#Enviar para o cliente a lista das notificacoes
		if comuns_enviar == '':
			send_msg(notificaSocket,'Nothing changed')
		#se tiver alguma coisa
		else:
			send_msg(notificaSocket,comuns_enviar)
		
		control = recv_msg(notificaSocket)
		if control == 'Stop':
			notificaSocket.close()
			sys.exit()
		#else(Keep) continua a executar

		#Indica de quanto em quanto tempo a API vai ser alterada
		time.sleep(tempo)
	return

###Funcao para terminar a execucao###
###Parametros de entrada : o socket das notificacoes e o socket 'normal'
###Valores de retorno : nenhum
def terminate(c,notificaSocket):
	global condicao
	global utilizadores
	condicao = False
	c.close                    
	notificaSocket.close
	utilizadores-=1
	#Se nao houver mais nenhum utilizador conectado termina o server
	if utilizadores == 0:
		print curr_time(),'Mais nenhum utilizador conectado. A desligar servidor...'
		os._exit(1)
	else:
		sys.exit()

###Funcao principal do programa###
###Parametros de entrada : socket das notificacoes, socket 'normal' e numero do cliente
###Valores de retorno : nenhum
def main(c,notificaSocket,Num_cliente):
	global utilizadores
	global subscricoes

	#Este e o indice do ID no array
	index_ID = login(c,notificaSocket,Num_cliente)

	print Num_cliente,curr_time(),'Login bem sucedido!'

	#Cria a Thread que atualiza a API
	try:
		Thread(target=atulizaAPI, args=(notificaSocket,index_ID)).start()
	except:
		print "Erro ao iniciar a thread para atualizar!"
		sys.exit()

	while True:
		#Arranjar o array das subscricoes e enviar para o cliente
		auxSet = set(subscricoes)
		subscricoes = list(auxSet)
		subscricoes.sort()
		enviaSubs = ' '.join(subscricoes)
		send_msg(c,enviaSubs)

		#Obter a opcao selecionada pelo cliente
		mensagem = recv_msg(c)
		mensagem = int(mensagem)

		if mensagem == 1:
			print Num_cliente,curr_time(),'Opcao 1. (ver uma das minhas informacoes) selecionada'
			#Receber a opcao do outro menu
			mensagem = recv_msg(c)
			mensagem = int(mensagem)
			if mensagem == 11:
				print Num_cliente,curr_time(),'Opcao 1.11. (voltar) selecionada'
				continue
			#else
			print Num_cliente,curr_time(),'Opcao 1.%d selecionada' % mensagem
			key = num_to_key(mensagem)
			result = search_key(key,index_ID)
			if result == 'ERROR':
				print Num_cliente,'Ocorreu um ERRO!'
				c.close                     # Close connection
				sys.exit(0)
			
			#Enviar os dados	
			send_msg(c,str(result))

		elif mensagem == 2:
			print Num_cliente,curr_time(),'Opcao 2. (ver todas as minhas informacoes) selecionada'
			for key, value in data[index_ID].items():
				mensagem = '%s = %s' % (key,value)
				send_msg(c,mensagem)
				#Para nao haver conflito de envio de dados
				time.sleep(0.001)

		elif mensagem == 3:
			print Num_cliente,curr_time(),'Opcao 3. (ver a media de uma das informacoes do grupo) selecionada'
			#Receber a opcao do outro menu
			mensagem = recv_msg(c)
			mensagem = int(mensagem)
			if mensagem == 10:
				print Num_cliente,curr_time(),'Opcao 3.11. (voltar) selecionada'
				continue
			#else
			print Num_cliente,curr_time(),'Opcao 3.%d.. selecionada' % mensagem
			key = num_to_key(mensagem)
			#Temos o parametro que queremos a media, agora calcular a media
			med = media(key)
			#Enviar a media para o cliente
			send_msg(c,str(med))

		elif mensagem == 4:
			print Num_cliente,curr_time(),'Opcao 4. (ver a media de todas das informacoes do grupo) selecionada'
			#Pegar num id qualquer qualquer(porque todos tem todos os parametros)
			for key, value in data[index_ID].items():
				if key == 'id':
					break
				med = media(key)
				mensagem = '%s = %s' % (key,med)
				send_msg(c,mensagem)
				#Para nao haver conflito de envio de dados
				time.sleep(0.001)

		elif mensagem == 5:
			print Num_cliente,curr_time(),'Opcao 5. (subscricoes) selecionada'
			#Recebe a opcao do menu das subscricoes
			sub = recv_msg(c)
			sub = int(sub[0])
			if sub == 7:
				print Num_cliente,curr_time(),'Opcao 5.7. (voltar) selecionada'
				continue
			elif sub == 1:
				print Num_cliente,curr_time(),'Opcao 5.1. (criar subscricao individual) selecionada'
				#Recebe qual a subscricao individual a fazer
				sub2 = recv_msg(c)
				sub2 = int(sub2)

				if sub2 == 10:
					print Num_cliente,curr_time(),'Opcao 5.1.10. (voltar) selecionada'
					continue
				#else
				#Formata para colocar no array
				subNo = "1.%d" % sub2
				subscricoes.append(subNo)
				print Num_cliente,curr_time(),'Subscricao individual criada para',num_to_key(sub2)
			elif sub == 2:
				print Num_cliente,curr_time(),'Opcao 5.2. (criar subscricao de grupo) selecionada'
				#Recebe qual a subscricao de grupo a fazer
				sub2 = recv_msg(c)
				sub2 = int(sub2)
				if sub2 == 10:
					print Num_cliente,curr_time(),'Opcao 5.2.10. (voltar) selecionada'
					continue
				#Formata para colocar no array
				subNo = "2.%d" % sub2
				if subNo not in subscricoes:
					subscricoes.append(subNo)
					print Num_cliente,curr_time(),'Subscricao de grupo criada para',num_to_key(sub2)
			elif sub == 3:
				print Num_cliente,curr_time(),'Opcao 5.3. (remover subscricao) selecionada'
				if not subscricoes:
					continue
				#Recebe o elemento a remover
				elementoRemover = recv_msg(c)
				if elementoRemover == 'Voltar':
					print Num_cliente,curr_time(),'Opcao 5.3.4. (voltar) selecionada)'
					continue
				
				elementoRemover = int(elementoRemover)
				#Remove o elemento escolhido
				del subscricoes[elementoRemover]
			elif sub == 4:
				print Num_cliente,curr_time(),'Opcao 5.4. (subscrever todos os parametros individuais) selecionada'
				subsIndividuais = ['1.1','1.2','1.3','1.4','1.5','1.6','1.7','1.8','1.9']
				subscricoes.extend(subsIndividuais)
			elif sub == 5:
				print Num_cliente,curr_time(),'Opcao 5.5. (subscrever todos os parametros de grupo) selecionada'
				subsGrupo = ['2.1','2.2','2.3','2.4','2.5','2.6','2.7','2.8','2.9']
				subscricoes.extend(subsGrupo)
			elif sub == 6:
				print Num_cliente,curr_time(),'Opcao 5.6. (remover todas as subscricoes) selecionada'
				del subscricoes[:]
		elif mensagem == 6:
			print Num_cliente,curr_time(),'Opcao 6. (limpar notificacoes) selecionada'
			continue
		elif mensagem == 7:
			print Num_cliente,curr_time(),'Cliente saiu'
			terminate(c,notificaSocket)

if __name__ == '__main__':
	startup()