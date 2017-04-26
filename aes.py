#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os.path
import base64
import copy
import binascii

BLOCK_SIZE = 8
KEY_SIZE = 16

s_box = (
		0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
		0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
		0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
		0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
		0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
		0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
		0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
		0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
		0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
		0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
		0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
		0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
		0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
		0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
		0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
		0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
		)

inv_s_box = (
		0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
		0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
		0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
		0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
		0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
		0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
		0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
		0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
		0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
		0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
		0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
		0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
		0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
		0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
		0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
		0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
		)

Rcon = ( 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a )

# God praise stack overflow, basically cross product
xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

# Reads key and returns bytes of that key
def read_key(keyname):
	file = open(keyname, "rb")
	key = base64.b16encode(file.read(KEY_SIZE))
	keyCheck = base64.b16encode(file.read(KEY_SIZE))

	if not key or len(key) < KEY_SIZE*2:
		print("ERROR: Key is not large enough.")
		return -1
	if keyCheck:
		print("ERROR: Key is too large.")
		return -1
	return key

def xor(s1, s2):
    return tuple(a^b for a,b in zip(s1, s2))
    
def sub_word(word):
    return (s_box[b] for b in word)
    
def rot_word(word):
    return word[1:] + word[:1]

def expand_key(key):
    nb = 4
    nr = 10
    nk = 4
    expanded = []
    expanded.extend(map(ord, key))
    for i in range(nk, nb * (nr + 1)):
        t = expanded[(i-1)*4:i*4]
        if i % nk == 0:
            t = xor(sub_word(rot_word(t)), (Rcon[i // nk],0,0,0) )
        elif nk > 6 and i % nk == 4:
            t = sub_word(t)
        expanded.extend( xor(t, expanded[(i-nk)*4:(i-nk+1)*4]))
    subList = [expanded[n:n+4] for n in range(0, len(expanded), 4)]
    return subList


def read_file(filename):
	""" Reads file and returns list with 16byte-blocks """
	file = open(filename, "rb")
	fileBytes = []
	while True:
		block = base64.b16encode(file.read(BLOCK_SIZE))
		if not block:
			break
		# Adds 01 and 00's to complete block
		if len(block) < (BLOCK_SIZE*2):
			block += b'01'
			while len(block) < (BLOCK_SIZE*2):
				block += b'00'
		fileBytes.append(block)
	return fileBytes

def bytes_to_matrix(block):
	""" Converts 16 byte array to 4x4 matrix. """
	matrix = [list(block[i:i+4]) for i in range(0, len(block), 4)]
	return matrix


def matrix_to_bytes(matrix):
	""" Converts 4x4 matrix to a 16 byte array. """
	return bytes(sum(matrix, []))

def print_matrix(matrixOfMatrices):
	string = []
	for matrix in matrixOfMatrices:
		string.append(matrix_to_bytes(matrix))
		# print(matrixOfMatrices[m])
		# for j, row in enumerate(matrix):

		# 	for i, byte in enumerate(row):
		# 		string += hex(byte)[2:].zfill(2)
		# 		if (i+1)%2 == 0:
		# 			string += ' '
		# 	if (j+1)%4 == 0:
		# 		string += '\n'
	for s in string:
		print(s)

def print_encoded_matrix(matrixOfMatrices):
	string = ''
	for matrix in matrixOfMatrices:
		# print(matrix)
		for j, row in enumerate(matrix):
			# print(row)
			# s = ''
			# for i, byte in enumerate(row):
			# 	print(hex(byte)[2:].zfill(2))

			for i, byte in enumerate(row):
				string += hex(byte)[2:].zfill(2)
				if (i+1)%2 == 0:
					string += ' '
			if (j+1)%4 == 0:
				string += '\n'
	print(string)


class AES:

	def __add_round_key(self, state, key):

		s = [[None for j in range(4)] for i in range(len(state))]
		for i, x in enumerate(state):
			for j, byte in enumerate(x):
				s[i][j] = byte ^ key[i][j]
		return s

	def __sub_bytes(self, state):
		return [[s_box[byte] for byte in x] for x in state]

	def __inv_sub_bytes(self, state):
		return [[inv_s_box[byte] for byte in x] for x in state]

	def __shift_rows(self, s):
		s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
		s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
		s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]
		return s

	def __inv_shift_rows(self, s):
		s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
		s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
		s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]
		return s

	def __mix_columns(self, s):
		for i in range(4):
			t = s[i][0] ^ s[i][1] ^ s[i][2] ^ s[i][3]
			u = s[i][0]
			s[i][0] ^= t ^ xtime(s[i][0] ^ s[i][1])
			s[i][1] ^= t ^ xtime(s[i][1] ^ s[i][2])
			s[i][2] ^= t ^ xtime(s[i][2] ^ s[i][3])
			s[i][3] ^= t ^ xtime(s[i][3] ^ u)
		return s

	def __inv_mix_columns(self, s):
		for i in range(len(s)):
			u = xtime(xtime(s[i][0] ^ s[i][2]))
			v = xtime(xtime(s[i][1] ^ s[i][3]))
			s[i][0] ^= u
			s[i][1] ^= v
			s[i][2] ^= u
			s[i][3] ^= v

		return self.__mix_columns(s)

	def encrypt(self, block, expanded_key, rounds):
		""" Function that will call every stage of the encryption """
		state = self.__add_round_key(block, expanded_key[:len(block)])

		for i in range(1, rounds):
			state = self.__sub_bytes(state)
			state = self.__shift_rows(state)
			state = self.__mix_columns(state)
			state = self.__add_round_key(state, expanded_key[i*len(block):(i+1)*len(block)])

		state = self.__sub_bytes(state)
		state = self.__shift_rows(state)
		state = self.__add_round_key(state, expanded_key[rounds*len(block):(rounds+1)*len(block)])

		return state

	def decrypt(self, block, expanded_key, rounds):
		""" Function that will call every the inverse of the encryption """
		state = self.__add_round_key(block, expanded_key[rounds*len(block):(rounds+1)*len(block)])

		for i in range(rounds -1, 0, -1):

			state = self.__inv_shift_rows(state)
			state = self.__inv_sub_bytes(state)
			state = self.__add_round_key(state, expanded_key[i*len(block):(i+1)*len(block)])
			state = self.__inv_mix_columns(state)

		state = self.__inv_shift_rows(state)
		state = self.__inv_sub_bytes(state)
		state = self.__add_round_key(state, expanded_key[:rounds])

		return state


def main(filename, keyfile):
	name = filename
	key = read_key(keyfile)

	if key == -1:
		return
	else:
		key = str(key)
		expanded_key = expand_key(key)

	byteArray = read_file(filename)
	for block in byteArray:
		print(block)

	""" OK, HERE WE NEED TO PASS THE BLOCK AND THE EXPANDED KEY """
	""" THESE ARE THE VALUES I AM USING:"""
	# KEY 000102030405060708090a0b0c0d0e0f
	# PLAINTEXT 48454c4c4f2041455320574f524c4421
	""" MAKE SURE THAT IN THE FUCTION IF WE USE THAT KEY WE GET THIS EXPANDED KEY: :"""
	#expanded_key = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [214, 170, 116, 253], [210, 175, 114, 250], [218, 166, 120, 241], [214, 171, 118, 254], [182, 146, 207, 11], [100, 61, 189, 241], [190, 155, 197, 0], [104, 48, 179, 254], [182, 255, 116, 78], [210, 194, 201, 191], [108, 89, 12, 191], [4, 105, 191, 65], [71, 247, 247, 188], [149, 53, 62, 3], [249, 108, 50, 188], [253, 5, 141, 253], [60, 170, 163, 232], [169, 159, 157, 235], [80, 243, 175, 87], [173, 246, 34, 170], [94, 57, 15, 125], [247, 166, 146, 150], [167, 85, 61, 193], [10, 163, 31, 107], [20, 249, 112, 26], [227, 95, 226, 140], [68, 10, 223, 77], [78, 169, 192, 38], [71, 67, 135, 53], [164, 28, 101, 185], [224, 22, 186, 244], [174, 191, 122, 210], [84, 153, 50, 209], [240, 133, 87, 104], [16, 147, 237, 156], [190, 44, 151, 78], [19, 17, 29, 127], [227, 148, 74, 23], [243, 7, 167, 139], [77, 43, 48, 197]]
	""" AND THE PLAINTEXT SHOULD BECOME THIS: """
	# block = [[0, 17, 34, 51], [68, 85, 102, 119], [136, 153, 170, 187], [204, 221, 238, 255]]

	rounds = 10

	#This works for a block, just do block in blocks if needed for a larger file
	# print ("Plaintext")
	# print (block)
	aes = AES()
	encrypted = []
	decrypted = []

	for i, block in enumerate(byteArray):
		byteArray[i] = bytes_to_matrix(block)

	print ("\nPre ecrypted")
	# print(byteArray)
	print_matrix(byteArray)

	for block in byteArray:
		encrypted.append(aes.encrypt(
			block,
			expanded_key,
			rounds
			)
		)
	print ("\nEcrypted")
	# print (encrypted)
	print_matrix(encrypted)

	for block in encrypted:
		decrypted.append(aes.decrypt(
			block,
			expanded_key,
			rounds
			)
		)
	print ("\nDecrypted")
	# print (decrypted)
	print_matrix(decrypted)



if __name__ == "__main__":
	if (len(sys.argv) != 3):
		print("Usage aes.py <file> <key>")
	else:
		if os.path.isfile(sys.argv[1]):
			main(sys.argv[1], sys.argv[2])
		else:
			print("File does not exist")
