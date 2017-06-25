import praw
import config
import os
import random
import sys
import time

count_up=0
prize_is_list=0
count_down=0
comment_id=0				#comment id
prizes = 0					#number of prizes
post_creator = 0			#post creator id number
comment_creator = 0 		#comment creator id
keyword = 0					#keyword to look for
post_id = 0					#reddit post id number
values = []					#splits comment into a list, should be in certain order to use correctly
entries = []				#entry list
winners = []				#winners list
total_entered = []			# list of people who have entered


#logs into reddit with provided user account info
def bot_login():
	print("Logging in...")
	r = praw.Reddit(username = config.username,		# username from config.py
					password = config.password,					# password form config.py
					client_id = config.client_id,						# client_id from config.py
					client_secret = config.client_secret,			# client secret from config.py
					user_agent = config.user_agent )			# user agent from config.py
	print("Logged in... \n")
	return r

def scan_sub(r,comments_replied_to):
	print ("Getting "+str(config.comments_to_search)+ " comments...")
	for comment in r.subreddit(config.sreddit).comments(limit=config.comments_to_search):
		if config.botname in comment.body and comment.id not in comments_replied_to and comment.author != r.user.me():

			comment_id = comment.id

			comments_replied_to.append(comment.id)
			with open ("comments_replied_to.txt", "a") as f:
				f.write(comment.id + "\n")

			print("Someone called for me!")
			post_creator = comment.submission.author.id
			comment_creator = comment.author.id
			post_id = comment.submission.id
			post = r.submission(id=post_id)

			if post_creator == comment_creator:
				print("I was called by the OP")
				post = r.submission(id=post_id)

				values = comment.body.split()
				if values[0]!= config.botname:
					return
				if len(values) < 3:
					values.append("")
					# print(values)

				prizes, keyword,count_down = set_param(values)

				# print("Commentor: " + comment_creator)
				# print("OP: " + post_creator)
				# print("# of Prizes: " + str(prizes))
				# print("Keyword: " + str(keyword))

				entries,total_entered,reply,console_response = get_entries(keyword,post,post_creator,prizes)
				if reply == 0:
					winners = get_winners(count_down,entries)
					edit_post(r,count_up,total_entered,winners,comment_id)
				else:
					print(console_response)
					r.comment(id=comment_id).reply(reply)
					return

			else:
					print("I was not called by the OP")
	print("Sleeping for " + str(config.sleep_timer) + " seconds...")
	time.sleep(config.sleep_timer)

# sets the values from the message to their variables
def set_param(values):
	prizes = int(values[1])
	keyword = values[2]
	count_down = int(prizes)
	return prizes,keyword,count_down

# Searches the entire post for people who have commented or used the provided keyword
def get_entries(keyword,post,post_creator,prizes):

	post.comments.replace_more(limit=0)
	for comment in post.comments.list():
		if keyword in comment.body and comment.author.name not in entries and comment.author.id != post_creator and comment.author.id != r.user.me():
			entries.append(comment.author.name)
			total_entered.append(comment.author.name)

	#if the keyword is not found then the bot will reply witht he below message
	if len(total_entered) == 0:
		response = "Keyword not found in comments, reply sent"
		reply = "Keyword '" + keyword + "' was not found. Please check you entered it correctly and comment again." + config.im_a_bot

	#if there are more prizes than entries then the bot will reply to the comment with the below message
	if len(total_entered) < prizes:
		console_response = "Not enough people in drawing, reply sent"
		reply = "Not enough people have entered the drawing :( \n\n Wait a little while and call me again." + config.im_a_bot
	else:
		console_response = None
		reply = 0
	return entries,total_entered,reply,console_response

# Randomly picks a name from total_entered and removes it to avoid duplicate pulls
def get_winners(count_down,entries):

	for count_down in range(count_down,0,-1):
			picked = random.choice(entries)
			winners.append(picked)
			entries.remove(picked)
	return winners


# Will respond to the comment with the amount of people who entered and the winners of the giveaway
def edit_post(r,count_up,total_entered,winners,comment_id):
	add_winners = ""
	number_of_winners = len(winners)-1
	total_entered = str(len(total_entered))
	for number_of_winners  in range (number_of_winners,-1,-1):
		if prize_is_list == 1:
			what_prize = " won " + prizes[count_up]
		else:
			what_prize = ""
		add_winners = add_winners + "\n\n /u/" + winners[number_of_winners] +  what_prize
		count_up +=1
	update =  total_entered+ " redditor(s) entered in this drawing \n\n The winner(s):" + add_winners + config.im_a_bot
	#print(update) #uncomment to test in the console
	r.comment(id=comment_id).reply(update)

#logs comments that have already been replied to in a text file it creates/finds
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
comments_replied_to = get_saved_comments()
while True:
	scan_sub(r, comments_replied_to)
