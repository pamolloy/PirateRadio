#!/usr/bin/env python3
# Pirate Radio
# Author: Wynter Woods (Make Magazine)

import os
import sys
import subprocess
import configparser
import re
import random
import time

class PirateRadio:
	"""Stream audio over radio frequencies using a Raspberry Pi"""

	def __init__(self):
		self.config_path = "pirateradio.cfg"
		self.fm_process = None
		self.on_off = ["off", "on"]
		self.merge_audio_in = False
		self.music_pipe_r,music_pipe_w = os.pipe()
		self.microphone_pipe_r,microphone_pipe_w = os.pipe()

		# User configuration
		config = configparser.ConfigParser()
		config.read(self.config_path)
		self.play_stereo = config.get('pirateradio', 'stereo_playback', fallback=True)
		self.frequency = config.get('pirateradio','frequency')
		self.shuffle = config.getboolean('pirateradio','shuffle',fallback=False)
		self.repeat_all = config.getboolean('pirateradio','repeat_all', fallback=False)
		self.music_dir = config.get('pirateradio', 'music_dir', fallback='/pirateradio')

	def build_file_list(self):
		file_list = []
		for root, folders, files in os.walk(self.music_dir):
			folders.sort()
			files.sort()
			for filename in files:
				if re.search(".(aac|mp3|wav|flac|m4a|pls|m3u)$", filename) != None: 
					file_list.append(os.path.join(root, filename))
		return file_list

	def play_songs(self, file_list):
		print("Playing songs to frequency ", str(self.frequency))
		print("Shuffle is " + on_off[self.shuffle])
		print("Repeat All is " + on_off[self.repeat_all])
		# print("Stereo playback is " + on_off[self.play_stereo])
		
		if self.shuffle == True:
			random.shuffle(file_list)
		with open(os.devnull, "w") as dev_null:
			for filename in file_list:
				print("Playing ",filename)
				if re.search(".pls$", filename) != None:
					streamurl = parse_pls(filename, 1)
					if streamurl != None:
						print("streaming radio from " + streamurl)
						subprocess.call(["ffmpeg","-i",streamurl,"-f","s16le","-acodec","pcm_s16le","-ac", "2" if self.play_stereo else "1" ,"-ar","44100","-"],stdout=music_pipe_w, stderr=dev_null)
				elif re.search(".m3u$", filename) != None:
					streamurl = parse_m3u(filename, 1)
					if streamurl != None:
						print("streaming radio from " + streamurl)
						subprocess.call(["ffmpeg","-i",streamurl,"-f","s16le","-acodec","pcm_s16le","-ac", "2" if self.play_stereo else "1" ,"-ar","44100","-"],stdout=music_pipe_w, stderr=dev_null)
				else:
					subprocess.call(["ffmpeg","-i",filename,"-f","s16le","-acodec","pcm_s16le","-ac", "2" if self.play_stereo else "1" ,"-ar","44100","-"],stdout=music_pipe_w, stderr=dev_null)

	def parse_pls(self, src, titleindex):
		# breaking up the pls file in separate strings
		lines = []
		with open( src, "r" ) as f:
			lines = f.readlines()

		# and parse the lines
		if lines != None:
			for line in lines:
				# search for the URI
				match = re.match( "^[ \\t]*file" + str(titleindex) + "[ \\t]*=[ \\t]*(.*$)", line, flags=re.IGNORECASE )
				if match != None:
					if match.group( 1 ) != None:
					# URI found, it's saved in the second match group
					# output the URI to the destination file
						return match.group( 1 )
			
		return None
			
	def parse_m3u(self, src, titleindex):
		# create a list of strings, one per line in the source file
		lines = []
		searchindex = int(1)
		with open( src, "r" ) as f:
			  lines = f.readlines()

		if lines != None:
			for line in lines:
			# search for the URI
				if '://' in line:
					if searchindex == titleindex:
						return line
					else:
						searchindex += 1
			
		return None

	def run_pifm(self):
		with open(os.devnull, "w") as dev_null:
			self.fm_process = subprocess.Popen(["/root/pifm","-",str(self.frequency),"44100", "stereo" if self.play_stereo else "mono"], stdin=self.music_pipe_r, stdout=dev_null)

	def record_audio_input(self):
		return subprocess.Popen(["arecord", "-fS16_LE", "--buffer-time=50000", "-r", "44100", "-Dplughw:1,0", "-"], stdout=microphone_pipe_w)

if __name__ == '__main__':
	pirate = PirateRadio()
	pirate.run_pifm()
	files = pirate.build_file_list()
	if self.repeat_all == True:
		while(True):
			pirate.play_songs(files)
	else:
		pirate.play_songs(files)

