#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import codecs
import glob
import match_words
import word

class Chunk:
	# basic unit of orthographic transcription
	def __init__(self,line,chunk_number,filename = None, fid = None,sid = None,cid = None,corpus = None,register =None):
		self.line = line
		self.chunk_number = chunk_number
		self.add_info(filename,fid,sid,cid,corpus,register)
		self.check_line()
		self.st, self.tier, self.label, self.et = self.line
		self.fix_label()
		self.duration = round(self.et - self.st,3)
		self.chunk_id = 'default_id'
		self.add_words()
		self.check_overlap()
		self.add_awd_items_in_chunk()
		self.nwords = len(self.words)


	def __str__(self):
		a = ['chunk:\t\t'+self.label]
		a.append( 'nwords:\t\t'+str(self.nwords))
		a.append( 'awd chunk:\t'+self.string_awd())
		a.append( 'n_awd_words:\t'+str(self.n_awd_words))
		a.append( 'start time:\t'+ str(self.st))
		a.append( 'end time:\t'+ str(self.et))
		a.append( 'duration:\t'+ str(self.duration))
		a.append( 'index:\t\t'+str(self.chunk_number ))
		a.append( 'file id:\t'+self.fid) 
		a.append( 'speaker id:\t'+self.sid) 
		a.append( 'overlap:\t'+str(self.overlap)) 
		a.append( 'overlap unk:\t'+str(self.overlap_unknown)) 
		a.append(' corpus:\t'+str(self.corpus))
		a.append('register:\t'+str(self.register))
		return '\n'.join(a)

	def check_line(self):
		# checks whether line is a good table line
		if type(self.line) == str:
			temp = line.split('\t')
			if len(temp) == 4:
				self.line = temp 
		if type(self.line) != list and self.line != 4:
			dl =[0.0,'default-speaker','default label',0.0]
			self.line = dl
		try:
			st,et = float(self.line[0]),float(self.line[-1])
			self.line[0],self.line[-1] = st,et
		except:
			self.line = dl


	def fix_label(self):
		# checks for interpuction and special code problems and fixes those
		# a problem is a space between .?* and word or the presence of a , 
		self.label_problem = []
		for problem in [' .',',',' ?',' *','  ']:
			if problem in self.label: self.label_problem.append(problem)  
				
		if self.label_problem != []:
			self.label = self.label.replace(' .','.').replace(',','').replace(' *','*').replace(' ?','?').replace('  ',' ')
		
		if self.label[-1] == ' ':
			self.label = self.label[:-1]
		if self.label[0] == ' ':
			self.label = self.label[1:]


	def add_info(self,filename = None, fid = None,sid = None,cid = None,corpus = None,register = None):
		# adds file speaker id corpus name and register info to object
		if filename: self.filename = filename
		else: self.filename = None
		if fid: self.fid = fid
		else: self.fid = None
		if sid: self.sid = sid
		else: self.sid = None
		if cid: self.cid = cid
		else: self.cid = None
		if corpus: self.corpus = corpus
		else: self.corpus = None
		if register: self.register = register
		else: self.register = None

	def add_words(self):
		# creates word object for each word in the chunk
		words = self.label.split(' ')
		self.words = []
		for i,w in enumerate(words):
			if w:
				w = word.Word(w,i,self.chunk_number,self.st,self.et,self.filename,self.fid,self.sid,self.cid,corpus = self.corpus,register = self.register)
				self.words.append(w)

	def check_overlap(self):
		# checks whether any word in the chunk overlaps in time with words uttered by the other speaker
		self.overlap_unknown,self.overlap = False,False
		self.overlap_indices = []
		for i,w in enumerate(self.words):
			if w.overlap_unknown: self.overlap_unknown = True
			if w.overlap == True: 
				self.overlap = True
				self.overlap_indices.append(i)

	def add_awd_items_in_chunk(self,awd_items = None):
		# creates lists with items that occur in the timeslot of the chunk and puts it in seperate lists
		if awd_items == None:
			self.awd_words = None
			self.awd_phon_words = None
			self.awd_phon= None
			self.n_awd_words,self.n_awd_phon_words,self.n_awd_phon = 0, 0, 0
			return 0
		if self.corpus == 'IFADV':
			self.awd_words = [line for line in awd_items if 'ort-word' in line[1]]
			self.awd_phon_words = [line for line in awd_items if 'phon-word' in line[1]]
			self.awd_phon= [line for line in awd_items if 'phon-phon' in line[1]]
		if self.corpus == 'CGN':
			self.awd_words = [line for line in awd_items if '_SEG' not in line[1] and '_FON' not in line[1]]
			self.awd_phon_words = [line for line in awd_items if '_FON' in line[1]]
			self.awd_phon= [line for line in awd_items if '_SEG' in line[1]]
	
		w,pw,p = len(self.awd_words), len(self.awd_phon_words), len(self.awd_phon)
		self.n_awd_words,self.n_awd_phon_words,self.n_awd_phon = w, pw, p

	def string_awd(self,awd_type = 'words'):
		# combines all awd words into a list
		if awd_type == 'words':
			if self.awd_words:
				return ' '.join([line[2] for line in self.awd_words])
		if awd_type == 'phon_words':
			if self.awd_words:
				return ' '.join([line[2] for line in self.awd_phon_words])
		if awd_type == 'phon':
			if self.awd_phon:
				return ' '.join([line[2] for line in self.awd_phon])
		

	def match_awd2word(self):
		#uses a matcher object to match awd and ort words, matcher class is defined in match_words
		awd_word_list = [line[2] for line in self.awd_words]
		self.matcher = match_words.Matcher(self.label,awd_word_list)
		for i,w in enumerate(self.words):
			if i in self.matcher.ort_index2awd_index.keys():
				awd_index = self.matcher.ort_index2awd_index[i]
				st = float(self.awd_words[awd_index][0])
				et = float(self.awd_words[awd_index][-1])
				w.add_times(st = st, et = et)
				w.awd_ok = True
			else:
				w.add_times(st = self.st, et = self.et)
				w.awd_ok = False
		if self.matcher.ratio < 1:
			print('not a complete match between ort and awd')
			print(self.matcher)

		
