import os
from engine.bottle import route, run, template
import codecs
from engine.markdown import Markdown
import time
from datetime import datetime

RAW_POSTS_DIR   = "./raw"
BUILD_POSTS_DIR = "./posts"

class Posts:

	def __init__(self):
		self.posts = {}		
		self.freshPost = None
		self._readPosts()		

	def _readPosts(self):
		posts = os.listdir( RAW_POSTS_DIR )
		fresh = 0
		
		for post in posts:
			# Skip files except *.md and *.html
			ext = post.split(".")[-1:][0]
			if not ext in ("md", "html"):
				continue			

			self.posts[ post ] = self._getPostData( post )

			try:
				d = datetime.strptime( self.posts[post]["meta"]["date"], "%d.%m.%y %H:%M")
				postDate = time.mktime(d.timetuple())

				if postDate > fresh: 
					fresh = postDate
					self.freshPost = post
			except:
				pass

	def build(self):
		for filename in self.posts:
			page = self._buildPage( self.posts[filename] )			
			self._savePage( self.posts[filename], page )
		self._buildIndexPage()

	def _buildIndexPage(self):
		if self.freshPost != None:
			page = self._buildPage( self.posts[self.freshPost] )			
			self._savePage( self.posts[self.freshPost], page, "./index.html" )

	# 
	def _getPostData(self, post):
		postObj = {}
		postObj["filename"]     = post		
		postObj["name"]         = ".".join(post.split(".")[:-1])
		postObj["htmlFilename"] = BUILD_POSTS_DIR + "/" + postObj["name"] + ".html" 
		postObj["content"]      = self._readFile( post )
		postObj["ext"]          = post.split(".")[-1:][0]
		postObj["meta"]         = self._getPostMeta( post )

		# If has no title in meta -> use filename
		if not "title" in postObj["meta"].keys():
			postObj["meta"]["title"] = postObj["name"]

		return postObj

	def _getPostMeta(self, filename):
		f = codecs.open(RAW_POSTS_DIR + "/" + filename, "r", "utf-8")
		content = f.read()
		f.close()

		settings = {}
		if content.split('\n')[0] == "<!--":
			pos = content.find("!-->")
			settingsString = content[ len("<!--") : pos ]
			settingsString = settingsString.strip()
			lines = settingsString.split('\n')
			for l in lines:
				param = l.split(":")
				settings[param[0].strip()] = ":".join( param[1:] ).strip()
			

		return settings

	def _readFile(self, postName):
		f = codecs.open(RAW_POSTS_DIR + "/" + postName, "r", "utf-8")
		content = f.read()
		f.close()

		return content

	# Return html
	def _buildPage(self, post):
		if post["ext"] == "md":
			md     = Markdown()
			post["content"] = md.convert( post["content"] )

		return template( "template.html", data = post, list = self.posts )

	def _savePage(self, post, page, path = None):
		savepath = post["htmlFilename"]
		if path != None: savepath = path
		
		f = codecs.open( savepath, "w", "utf-8" )
		f.write( page )
		f.close()

	def getPosts(self):
		return self.posts

posts = Posts()
plist = posts.getPosts()
#print plist.keys()
#print plist
posts.build()

