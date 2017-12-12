import os
import praw
import time
import config
import random

class console:
	notop = "Not the OP\n"
	wformat = "Wrong format\n"
	notenough = "not enough people in drawing\n"
	error = "There was an error\n"


class res:
	notop = "You are not the OP for the linked post."+config.help_message
	wformat = "Incorrect format, please make sure you're using the correct input."+ config.help_message
	notenough = "Not enough people in drawing at this time. Leave another comment later."
	error = "I ran into a problem getting results for this drawing. Please make sure the format is correct."+config.help_message

def bot_login():
	print("\nPosts Logging in...")
	r = praw.Reddit(username = config.username,     # username from config.py
					password = config.password,                 # password form config.py
					client_id = config.client_id,                       # client_id from config.py
					client_secret = config.client_secret,           # client secret from config.py
					user_agent = config.user_agent )            # user agent from config.py
	print("Logged in... \n")
	return r

def post_scan(r,posts_replied_to):
	print("Getting "+str(config.posts_to_search)+" posts\n")
	for submission in r.subreddit(config.sreddit).new(limit=config.posts_to_search):
			if config.botname in submission.selftext and submission.id not in posts_replied_to and submission.author.name != r.user.me():
				try:
					post_id = submission.id
					posts_replied_to.append(post_id)
					with open("posts_replied_to.txt","a") as f:
						f.write(post_id+"\n")
					response = None
					print("Called by post: "+post_id)
					while response == None:
						values = submission.selftext.split()
						if config.botname == values[0]:
							post_url,prizes,keyword = get_param(values)

							if submission.author.id == r.submission(url=post_url).author.id:
								entries = get_entries(post_url,keyword)
								total_entered = len(entries)
								if total_entered < prizes:
									console_response = console.notenough
									response = res.notenough
								winners = get_winners(entries,prizes)
								response = reply_comment(total_entered,winners)
								console_response = str(total_entered)+" entered "+str(prizes)+" picked\n"
							else:
								console_response = console.notop
								response = res.notop
						else:
							console_response = console.wformat
							response = res.wformat
				except BaseException as error:
					print(error)
					console_response= console.error
					response=res.error
				print(console_response)
				r.redditor(submission.author.name).message('Giveaway Results',response)

def comment_scan(r,comments_replied_to):
	print("Getting "+str(config.comments_to_search)+" comments\n")
	for comment in r.subreddit(config.sreddit).comments(limit=config.comments_to_search):

			if config.botname in comment.body and comment.id not in comments_replied_to and comment.author.name != r.user.me():
				try:
					comment_id = comment.id
					comments_replied_to.append(comment_id)
					with open("comments_replied_to.txt","a") as f:
						f.write(comment_id+"\n")
					response = None
					print("Called by comment: "+comment_id)
					while response == None:
						values = comment.body.split()
						if config.botname == values[0]:
							post_url,prizes,keyword = get_param(values)

							if comment.author.id == r.submission(url=post_url).author.id:
								entries = get_entries(post_url,keyword)
								total_entered = len(entries)
								if total_entered < prizes:
									console_response = console.notenough
									response = res.notenough
								winners = get_winners(entries,prizes)
								response = reply_comment(total_entered,winners)
								console_response = str(total_entered)+" entered "+str(prizes)+" picked\n"
							else:
								console_response = console.notop
								response = res.notop
						else:
							console_response = console.wformat
							response = res.wformat
				except BaseException as error:
					print(error)
					console_response= console.error
					response=res.error
				print(console_response)
				r.redditor(comment.author.name).message('Giveaway Results',response)

def get_param(values):
	if len(values)<4:
		values.append("")
	post_url = values[1]
	prizes = int(values[2])
	keyword = values[3]

	return post_url,prizes,keyword

def get_entries(post_url,keyword):
	entries = []
	post = r.submission(url=post_url)
	post.comments.replace_more(limit=None)
	print("getting entries...")
	for comment in post.comments.list():
		if comment.author==None:
			pass
		elif keyword in comment.body and comment not in entries and comment.author != post.author:
			entries.append(comment.author.name)
	return entries

def get_winners(entries,prizes):
	count_down = prizes
	winners = []
	for count_down in range(count_down,0,-1):
			picked = random.choice(entries)
			winners.append(picked)
			entries.remove(picked)
	return winners

def reply_comment(total_entered,winners):
	count_up = 0
	add_winners = ""
	number_of_winners = len(winners)-1
	total_entered = str(total_entered)
	for number_of_winners  in range (number_of_winners,-1,-1):

		what_prize = ""
		add_winners = add_winners + "\n\n" + winners[number_of_winners] +  what_prize
		count_up +=1
	response =  total_entered+ " redditor(s) entered in this drawing \n\n The winner(s):" + add_winners
	return response

#logs comments that have already been replied to in a text file it creates/finds
def get_saved_posts():
	if not os.path.isfile("posts_replied_to.txt"):
		posts_replied_to = []
	else:
		with open("posts_replied_to.txt", "r") as f:
			posts_replied_to = f.read()
			posts_replied_to = posts_replied_to.split("\n")
			posts_replied_to = list(filter(None, posts_replied_to))
	return posts_replied_to

def get_saved_comments():
	if not os.path.isfile("comments_replied_to.txt"):
		comments_replied_to = []
	else:
		with open("comments_replied_to.txt", "r") as f:
			comments_replied_to = f.read()
			comments_replied_to = comments_replied_to.split("\n")
			comments_replied_to = list(filter(None, comments_replied_to))
	return comments_replied_to

r = bot_login()
posts_replied_to = get_saved_posts()
comments_replied_to = get_saved_comments()

while True:
	post_scan(r,posts_replied_to)
	comment_scan(r,comments_replied_to)
	print("No posts or comments found.\nSleeping for "+str(config.sleep_timer)+" seconds... \n")
	time.sleep(config.sleep_timer)
