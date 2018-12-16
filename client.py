#!/usr/bin/python           # This is client.py file

import socket
import sys
import os
import time
from threading import Thread
from funcoesDeEnvio import send_msg
from funcoesDeEnvio import recv_msg
from funcoesDeEnvio import recvall
from funcoesAuxiliares import num_to_key

condicao = True
notificacoes = []

###Inicializar os sockets e criar as threads###
###Parametros de entrada : nenhum
###Valores de retorno : referencia do socket das notificacoes e do socket 'principal'
def startup():
	#SOCK_STREAM->TCP
	#AF_INET-> usar IPV4
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	IP_address = "127.0.0.1"
	Port1 = 9000

	try:
		s.connect((IP_address, Port1))
	except:
		print "Socket1 : Connection error"
		sys.exit()

	conection = s.recv(1024)
	print 'Socket1 : Got connection from', conection

	#socket para as notificacoes
	notificaSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#selecionar outro porto
	Port2 = Port1 + 1

	try:
		notificaSocket.connect((IP_address,Port2))
	except:
		print "Socket2 : Connection error"
		sys.exit()
	
	conection = notificaSocket.recv(1024)
	print 'Socket2 : Got connection from', conection

	return s, notificaSocket

###Cliente dar login no servidor. Tem 3 tentativas###
###Parametros de entrada : socket 'principal'
###Valores de retorno : em caso de sucesso, o ID do utilizador
def login(s):
	print 'Bem-vindo ao servidor de privacidade ISABELA'
	#so para inicializar
	ID = 'a'
	#Obtem o ID que o utilizador introduz, envia-o para o servidor ver se e valido, recebe a resposta do utilizador e avalia se continua a perguntar ou nao
	while True:
		ID = raw_input('Introduza o seu ID: ')
		send_msg(s,ID)
		result = recv_msg(s)
		if result == 'Success':
			return ID
		else:
			result = int(result)
			if result != 0:
				print 'Introduza um ID existente. Tem',result,'tentativas'
			else:
				print 'Numero maximo de tentativas atingido! Terminando o cliente...'
		result = int(result)
		if result == 0:
			s.close
			sys.exit(0)

###Input do cliente. Verificar se um valor esta dentro de um limite###
###Parametros de entrada : valor minimo e valor maximo
###Valores de retorno : valor introduzido dentro do limite
def verifica_valor(min,max):
	while True:
		valor = raw_input('>>')
		try:
			valor = int(valor)
			if valor < min or valor > max:
				print 'Introduza um valor dentro dos permitidos'
				continue
			else:
				break
		except:
			print 'Introduza um valor inteiro'
	return valor

###Menu principal do cliente. Envia a opcao escolhida para o servidor###
###Parametros de entrada : nenhum
###Valores de retorno : opcao selecionada
def menu():
	os.system('clear')
	#as notificacoes
	printNotificacoes()
	print 'Este e o menu do servidor de privacidade ISABELLA. Selecione uma das seguintes opcoes:'
	print '1. Ver uma das minhas informacoes'
	print '2. Ver todas as minhas informacoes'
	print '3. Ver a media de uma das informacoes do grupo'
	print '4. Ver a media de todas as informacoes do grupo'
	print '5. Configurar subscricoes'
	print '6. Limpar notificacoes'
	print '7. SAIR\n'

	opcao = verifica_valor(1,7)
	#Envia ao servidor a opcao selecionada
	send_msg(s,str(opcao))

	return opcao

###Menu de escolha da informacao a selecionar###
###Parametros de entrada : tipo de menu(depende do menu anterior)
###Valores de retorno : opcao selecionada
def menu_op(op):
	os.system('clear')
	printNotificacoes()
	if op == 'opcao1':
		print 'Qual das informacoes quer ver?\n'
	elif op == 'opcao3':
		print 'Qual das medias quer ver?\n'
	elif op == 'opcao5.1':
		print 'Qual das informacoes individuais quer subscrever?'
	elif op == 'opcao5.2':
		print 'Qual das informacoes de grupo quer subscrever?'


	print '1.  Chamadas perdidas: numero de chamadas perdidas nos ultimos 5 segundos'
	print '2.  Chamadas recebidas: numero de chamadas recebidas nos ultimos 5 segundos'
	print '3.  Chamadas efetuadas: numero de chamadas efetuadas nos ultimos 5 segundos'
	print '4.  Duracao das chamadas: duracao das chamadas efetuadas nos ultimos 5 segundos'
	print '5.  SMS enviados: numero de SMS enviados nos ultimos 5 segundos'
	print '6.  SMS recebidos: numero de SMS recebidos nos ultimos 5 segundos'
	print '7.  Localizacao: localizacao do aluno (Universidade, Casa, Outro)'
	print '8.  Atividade: atividade atual do aluno (Ex. Exercicio,Dormir,Aulas,Deitado...)'
	print '9.  Departamento: nome do departamento (Ex. DEI)'
	if op == 'opcao1':
		print '10. ID: ID do aluno'
		print '11. VOLTAR AO MENU PRINCIPAL'
		opcao = verifica_valor(1,11)
	elif op == 'opcao3' or 'opcao5.1' or 'opcao5.2':
		print '10. VOLTAR AO MENU PRINCIPAL'
		opcao = verifica_valor(1,10)

	#Envia ao servidor a opcao selecionada
	send_msg(s,str(opcao))

	return int(opcao)

###Menu das subscricoes###
###Parametros de entrada : array das subscricoes para serem imprimidas
###Valores de retorno : opcao selecionada
def menu_sub(subscricoes):
	os.system('clear')
	printNotificacoes()
	printSubs(subscricoes,0)
	print 'Menu subscricoes:'
	print '1. Criar uma nova subscricao individual'
	print '2. Criar uma nova subscricao de grupo'
	print '3. Remover uma subscricao'
	print '4. Subscrever todos os parametros individuais'
	print '5. Subscrever todos os parametros de grupo'
	print '6. Remover todas as subscricoes'
	print '7. VOLTAR\n'

	opcao = verifica_valor(1,7)
	#Envia ao servidor a opcao selecionada
	send_msg(s,str(opcao))

	return opcao

###Imprimir as subscricoes###
###Parametros de entrada : array das subscricoes e modo: 0 para imprimir normalmente, 1 para imprimir com o numero a remover
###Valores de retorno : numero de subscricoes
def printSubs(subs,modo):
	if not subs: 
		print 'Nenhuma subscricao criada! Crie uma.\n'
		return -1
	cont = 1
	if modo == 0:
		print 'Subscricoes atuais:\n'
	elif modo == 1:
		print '\nSelecione uma das seguintes subscricoes para remover:\n'

	for elem in subs:
		if int(elem[0]) == 1:
			if modo == 0:
				print 'Subscricao individual :',num_to_key(int(elem[2]))
			elif modo == 1:
				print cont,'Subscricao individual :',num_to_key(int(elem[2]))
		elif int(elem[0]) == 2:
			if modo == 0:
				print 'Subscricao de grupo :',num_to_key(int(elem[2]))
			elif modo == 1:
				print cont,'Subscricao de grupo :',num_to_key(int(elem[2]))

		cont += 1
	if modo == 0:
		print ''
	if modo == 1:
		print '\n',cont,'VOLTAR AO MENU PRINCIPAL'
	return cont

###Imprimir as notificacoes###
###Parametros de entrada : nenhum
###Valores de retorno : nenhum
def printNotificacoes():
	if not notificacoes: 
		print 'Nenhuma notificacao por mostrar\n'
		return -1

	print 'Notificacoes:\n'
	for elem in notificacoes:
		if int(elem[0]) == 1:
				print 'Subscricao individual',num_to_key(int(elem[2])),'alterada!'
		elif int(elem[0]) == 2:
				print 'Subscricao de grupo',num_to_key(int(elem[2])),'alterada!'
	print '\n'

###Funcao executada pela thread para atualizar a API###
###Parametros de entrada : socket das notificacoes
###Valores de retorno : nenhum
def atualizaAPI(notificaSocket):
	i = 0
	global notificacoes
	while condicao == True:
		#Recebe empty ou continue
		mensagem = recv_msg(notificaSocket)
		if mensagem == 'Empty':
			continue
		#else(recebeu a lista das notificaoes)
		if mensagem == 'Nothing changed':
			pass
		else:
		#Este try/except serve para quando o socket e fechado(opcao SAIR) no servidor nao dar erro de NoType. Simplesmente ignora os erros.
			try:
				#juntar as notificacoes, ordenar e selecionar apenas os elementos unicos
				listaNoti = list(mensagem.split(" "))
				novasNotificacoes = notificacoes
				novasNotificacoes.extend(listaNoti)
				notificacoes = novasNotificacoes
				notificacoes = list(set(notificacoes))
				notificacoes.sort()
			except:
				pass
		#Da o 'OK' ao servidor
		send_msg(notificaSocket,'Keep')
	return

###Funcao principal do programa###
###Parametros de entrada : socket das notificacoes e socket 'normal'
###Valores de retorno : nenhum
def main(s,notificaSocket):
	ID = login(s)
	print "Login bem sucedido!"

	#Cria a thread para atualizar a API
	try:
		Thread(target=atualizaAPI, args=(notificaSocket,)).start()
	except:
		print "Erro ao iniciar a thread para atualizar!"
		sys.exit()

	#Ciclo principal
	while True:
		#Para nao haver conflito de envio de dados
		time.sleep(0.001)
		#Recebe as subscricoes para depois as impirmir
		subscricoes = recv_msg(s)
		subscricoes = list(subscricoes.split(" "))

		if subscricoes == ['']:
			subscricoes = []

		opcao = menu()
		#Verifica qual a opcao escolhida e executa a sua funcao
		if opcao == 1:
			opcao_menu_op1 = menu_op('opcao1')
			if opcao_menu_op1 == 11:
				continue
			 #else
			 #Receber o dado pedido
			print 'Valor = ',recv_msg(s)
			raw_input('\n[Introduza qualquer coisa para continuar]')
		elif opcao == 2:
			for i in range(11):
				print recv_msg(s)
			raw_input('\n[Introduza qualquer coisa para continuar]')
		elif opcao == 3:
			opcao_menu_op3 = menu_op('opcao3')
			if opcao_menu_op3 == 10:
				continue
			#else
			#Receber o dado pedido
			print 'Media = ',recv_msg(s)
			raw_input('\n[Introduza qualquer coisa para continuar]')
		elif opcao == 4:
			for i in range(10):
				print recv_msg(s)
			raw_input('\n[Introduza qualquer coisa para continuar]')
		elif opcao == 5:
			#Listar subscricoes e obter a opcao selecionada
			opcao_sub = menu_sub(subscricoes)
			if opcao_sub == 7:
				continue
			elif opcao_sub == 1:
				sub = menu_op('opcao5.1')
				if sub == 10:
					continue
				#else
				print 'Subscricao criada com sucesso!'
				raw_input('\n[Introduza qualquer coisa para continuar]')
			elif opcao_sub == 2:
				sub = menu_op('opcao5.2')
				if sub == 10:
					continue
				#else
				print 'Subscricao criada com sucesso!'
				raw_input('\n[Introduza qualquer coisa para continuar]')
			elif opcao_sub == 3:
				maximo = printSubs(subscricoes,1)

				#Nao existe nenhuma subscricao
				if maximo == -1:
					raw_input('\n[Introduza qualquer coisa para continuar]')
					continue
				#else
				print '\n'
				if verifica_valor(1,maximo) == maximo:
					send_msg(s,'Voltar')
					continue
				#else
				#enviar o parametro a remover
				indiceElementoRemover = maximo - 2
				send_msg(s,str(indiceElementoRemover))
			elif opcao_sub == 4:
				print 'Subscricoes individuais efetuadas com sucesso!'
				raw_input('\n[Introduza qualquer coisa para continuar]')
			elif opcao_sub == 5:
				print 'Subscricoes de grupo efetuadas com sucesso!'
				raw_input('\n[Introduza qualquer coisa para continuar]')
			elif opcao_sub == 6:
				print 'Todas as subscricoes foram removidas com sucesso!'
				raw_input('\n[Introduza qualquer coisa para continuar]')
		elif opcao == 6:
			global notificaoes
			del notificacoes[:]
		elif opcao == 7:
			global condicao
			#Terminar a Thread que atualiza a API
			condicao = False
			s.close
			notificaSocket.close
			sys.exit(0)


if __name__ == '__main__':
	s, notificaSocket = startup()
	main(s,notificaSocket)