#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import codecs
import glob
import sid


class Ort:
	# creates a datastructure that hold start and end times and POS tag for each word in a audio file
	# words are grouped in chunks and sentences, words have a pos object
	# ort holds sid (speakers object) in speakers, sid holds chunks and sentences and they both hold words
	# sentences are needed for pos tags and surprisal, surprisal needs to be added still, as does frequency
	def __init__(self,fid = None,sid_name = 'spreker1', path = '../IFADV_ANNOTATION/ORT/',awd_path = '../IFADV_ANNOTATION/AWD/WORD_TABLES/',corpus = 'IFADV', pos_path = 'POS_IFADV/FROG_OUTPUT/',register = 'spontaneous_dialogue'):
		if fid == None:
			fid = 'DVA13U'
			print('calling ort class with default file id: ',fid)
		print('creating ort with file id:',fid,' and speaker id:',sid_name)
		self.fid = fid
		self.path = path
		self.awd_path = awd_path
		self.corpus = corpus
		self.pos_path = pos_path
		self.register = register
		self.sids = []
		self.speakers_present = False
		self.nspeakers = 0
		self.speakers = [] 

		if sid:
			self.add_speaker(sid_name)


	def __str__(self):
		#prints info from all speakers
		a = ['file id:\t' + self.fid ]
		a.append('speaker ids:\t'+'  '.join(self.sids))
		for speaker in self.speakers:
			a.append('-'* 50)
			a.append(speaker.__str__())
		return '\n'.join(a)
		

	def add_speaker(self,sid_name):
		#adds a seconds speaker to the file, only needed for ifadv
		self.speakers.append( sid.Sid(self.fid,sid_name,self.path,self.awd_path,self.corpus,self.pos_path,self.register) )
		self.sids.append(sid_name)
		self.speakers_present = True
		self.nspeakers += 1


	def check_overlap(self):
		# check whether words overlap with other words only needed for ifadv
		if len(self.speakers) != 2:
			print('need 2 speaker to check for overlap (> 2 speakers not implemented')
			return 0
		s1,s2 = self.speakers
		for i,w1 in enumerate(s1.words):
			w1.set_overlap(overlap = False)
			for i2,w2 in enumerate(s2.words):
				w2.set_overlap(overlap = False)
				if w1.st and w1.et and w2.st and w2.et:
					if (w1.st >= w2.st and w1.st < w2.et) \
						or (w1.et >= w2.st and w1.et < w2.et):
						if i not in s1.word_overlap_indices:
							s1.word_overlap_indices.append(i)
						if i2 not in s2.word_overlap_indices:
							s2.word_overlap_indices.append(i2)

		for i in s1.word_overlap_indices:
			s1.words[i].set_overlap(overlap = True)
		for i in s2.word_overlap_indices:
			s2.words[i].set_overlap(overlap = True)

		for s in self.speakers:
			for i,c in enumerate(s.chunks):
				c.check_overlap()
				if c.overlap and not c.overlap_unknown:
					s.chunk_overlap_indices.append(i)

		s1.n_chunk_overlap = len(s1.chunk_overlap_indices)
		s1.n_word_overlap = len(s1.word_overlap_indices)
		s2.n_chunk_overlap = len(s2.chunk_overlap_indices)
		s2.n_word_overlap = len(s1.word_overlap_indices)


	def make_sentences(self):
		#makes sentences for each speaker (words between eol markers ... . ! ?)
		for s in self.speakers:
			s.make_sentences()


	def print_sentences(self):
		#prints out all sentences for each speaker into a text file, needed to to FROG pos tagging
		for s in self.speakers:
			s.print_utf8_sentences()

	def create_pos_files(self):
		# creates ifadv pos files similar to the ones on the site, not relevant for EEG process 
		output = []
		for speaker in self.speakers:
			for s in speaker.sentences:
				output.append('< file id: '+speaker.fid+' speaker id: '+speaker.sid+ ' sentence: '+str(s.sentence_number+1)+ ' start time: '+str(s.st) + ' end time:' + str(s.et) + ' >')
				for w in s.words:
					output.append(w.make_pos_info())	
		return output

