####Funcoes para enviar e receber a totalidade dos pacotes TCP####

import socket
import struct

###Funcao para enviar a mensagem###
###Parametros de entrada : socket e mensagem a enviar
###Valores de retorno : nenhum
def send_msg(sock, msg):
    # Junta um prefixo a mensagem a enviar. Este prefixo ocupa 4 bytes e indica o tamanho da mensagem
    # O argumento > indica que vai ser arazenado em big endian e o I indica que vai ser armazenado em inteiro(dai os 4 bytes) (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

###Funcao para receber mensgem###
###Parametros de entrada : socket
###Valores de retorno : mensagem recebida
def recv_msg(sock):
    #Le o tamanho da mensagem e desempacota-a num inteiro
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Converter a informacao
    return recvall(sock, msglen)

###Funcao auxiliar para ler toda a mensagem e esvaziar o buffer do socket###
###Parametros de entrada : socket e numero de bytes da mensagem
###Valores de retorno : mensagem completa
def recvall(sock, n):
    # Recebe n bytes e retorna a mensagem
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data