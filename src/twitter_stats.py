#!/usr/bin/python 
import sys, math, time; 

import twitter; 

## cmd line input parameter names 
globals()['CTRL'] = "control_var"; 
globals()['test'] = 'testing'; 
globals()['access'] = "access"; 

## standard key names for OAuth configuration 
globals()['aname'] = "app_name"; 
globals()['ckey'] = "consumer_key"; 
globals()['csec'] = "consumer_secret"; 
globals()['atok'] = "access_token"; 
globals()['asec'] = "access_secret"; 

## api specific parameter names 
globals()['ids'] = u"ids"; 
globals()['resources'] = u"resources"; 
globals()['account'] = u'account'; 
globals()['users'] = u"users"; 
globals()['created_at'] = u"created_at"; 
globals()['app'] = u'application'; 
globals()['friendships'] = u"friendships"; 
globals()['statuses'] = u"statuses"; 
globals()['friends'] = u"friends"; 

globals()['vc'] = u"/account/verify_credentials"; 
globals()['ulu'] = u'/users/lookup'; 
globals()['arls'] = u"/application/rate_limit_status"; 
globals()['fds'] = u"/friendships/show"; 
globals()['stfd'] = u"/statuses/friends"; 
globals()['utml'] = u"/statuses/user_timeline"; 

globals()['remaining'] = u'remaining'; 
globals()['lim'] = u"limit"; 

## default authentication settings for testing purposes; 
globals()['chenli_auth'] = { \
	aname:"chenliapp2", \
	ckey:"lCrQAA5TYywy8ddqpAFM4vEvE", \
	csec:"poOOccKCLtRK1r7IkGe53hefFgtnjQNAX2nsXrdocgk6a4o0E7",  \
	atok:"106587287-OxMjyLANUFh2h6oUNSqFjb0sKKLf5b5dL2TefzTA", \
	asec:"qj4lMoTdmpGQ6Ypz9IFr6kd0vLOLIJoWVYD0hRSEtl8ku", \
	} 

## global record of time-limit resources; 
globals()['vc_rem'] = -1; 
globals()['ulu_rem'] = -1; 
globals()['arls_rem'] = -1; 
globals()['fds_rem'] = -1; 
globals()['stfd_rem'] = -1; 
globals()['utml_rem'] = -1; 

globals()['vc_lim'] = -1; 
globals()['ulu_lim'] = -1; 
globals()['arls_lim'] = -1; 
globals()['fds_lim'] = -1; 
globals()['stfd_lim'] = -1; 
globals()['utml_lim'] = -1; 

## standard decorator, for tracking time within some functions
## used for checking certain types of errors 
def dectime(decorated): 
	def wrapper(*vars): 
		curr_time = time.clock(); 
		retval = decorated(*vars); 
		print "curr-action:", decorated.func_name,  "at-time:", curr_time; 
		return retval; 
	return wrapper; 

## decorator for displaying twitter time resource limits 
## >> updated at the beginning of eachr run  
## used for checking time-related resources for certain functions 
def dec_timelim(decorated): 
	def wrapper(*vars): 
		retval = decorated(*vars); 
		print "curr-action:", decorated.func_name, \
			 "times-vrf-lim:", vc_lim, \
			"times-usr-lim:", ulu_lim, \
			"times-app-lim:", arls_lim, \
			"times-fds-lim:", fds_lim, \
			"times-stfd-lim:", stfd_lim, \
			"times-utml-lim:", utml_lim; 
		return retval; 
	return wrapper; 

## decorator for displaying current times-resource remaining 
## >> needs to be updated each time twitter-resource is used 
## used for checking time-related resources for certain functions 
def dec_timeused(decorated): 
	def wrapper(*vars): 
		retval = decorated(*vars); 
		print "curr-action:", decorated.func_name, \
			 "times-vrf-rem:", vc_rem, \
			"times-usr-rem:", ulu_rem, \
			"times-app-rem:", arls_rem, \
			"times-fds-rem:", fds_rem, \
			"times-stfd-rem:", stfd_rem, \
			"times-utml-rem:", utml_rem; 
		return retval; 
	return wrapper; 

## base class for managing twitter resources 
## -- including authentication, time-tracking, time-resource management, etc; 
## members inherited to provide functionality 
## needs 'twitter' module import to access API 
class twitter_resources_record(object): 

	## std initialization function
	def __init__(self, name): 
		self.auth_tokens = {}; 

		self.vc_remaining = -1;
		self.ulu_remaining = -1; 
		self.arls_remaining = -1; 
		self.fds_remaining = -1; 
		self.stfd_remaining = -1; 
		self.utml_remaining = -1; 

		self.reinit_resource_cnts(); 

		self.vc_lim = -1;
		self.ulu_lim = -1; 
		self.arls_lim = -1; 
		self.fds_lim = -1; 
		self.stfd_lim = -1; 
		self.utml_lim = -1; 

		self.req_status_cnt = 200; 
		self.max_status_lim = 3200; 
		self.max_status_cnt = self.max_status_lim + 200; 

		self.rate_lim_status = {}; 
		self.max_backoff_lim = int(math.pow(2.0, 10.0)); 

	## several important time-resources initialized to defaults 
	def reinit_resource_cnts(self): 
		self.arls_cnt = 0; 
		self.utml_cnt = 0; 
		self.ulu_cnt = 0; 

	## function called externally to display twitter resources as a tree; 
	def display_ratelim(self): 
		print '^'*79; 
		print "rate limit status: "; 
		self.display_ratelim_rec(self.rate_lim_status, 0); 
		print '$'*79; 

	## internal function recursively called by display_ratelim() 
	def display_ratelim_rec(self, curr_struct, lvl): 
		keys = (key for key in curr_struct.keys()); 
		for key in keys: 
			if (isinstance(curr_struct[key], dict)): 
				print lvl * "\t", key, ':'; 
				self.display_ratelim_rec(curr_struct[key], lvl+1); 
			else: 
				print lvl * "\t", key, ':', curr_struct[key]; 

	## checks whether the current app has different rate-limitations than standard 
	## must only run at the initialization phase of module 
	def init_check_rate_lim(self): 
		self.record_rate_usage(); 
		if (self.arls_lim > self.arls_remaining): 
			self.arls_lim = self.arls_remaining; 
		if (self.utml_lim > self.utml_remaining): 
			self.utml_lim = self.utml_remaining; 
		if (self.ulu_lim > self.ulu_remaining): 
			self.ulu_lim = self.ulu_remaining; 

	## initializes rate limitations from a twitter object 
	## called when class is loaded 
	## must be called after the twitter.Twitter module is loaded, and authentication complete 
	@ dec_timelim 
	def init_rate_lim(self): 
		self.rate_lim_status = self.tw.application.rate_limit_status(); 
		
		self.vc_lim = self.rate_lim_status[resources][account][vc][lim]; 
		self.ulu_lim = self.rate_lim_status[resources][users][ulu][lim]; 
		self.arls_lim = self.rate_lim_status[resources][app][arls][lim]; 
		self.fds_lim = self.rate_lim_status[resources][friendships][fds][lim]; 
		self.stfd_lim = self.rate_lim_status[resources][statuses][stfd][lim]; 
		self.utml_lim = self.rate_lim_status[resources][statuses][utml][lim]; 

		self.init_check_rate_lim(); 

		globals()['vc_lim'] = int(self.vc_lim); 
		globals()['ulu_lim'] = int(self.ulu_lim); 
		globals()['arls_lim'] = int(self.arls_lim); 
		globals()['fds_lim'] = int(self.fds_lim); 
		globals()['stfd_lim'] = int(self.stfd_lim); 
		globals()['utml_lim'] = int(self.utml_lim); 

	## get updated time-resources object from twitter 
	## then records the necessary internal states 
	@ dectime 
	@ dec_timeused 
	def get_rate_usage(self): 
		self.rate_lim_status = self.tw.application.rate_limit_status(); 
		#self.display_ratelim(); 
		self.record_rate_usage(); 

	## extracts the necessary 'remaining' entries from twitter resource-limit object
	## records those upto date values in internal states 
	def record_rate_usage(self):  
		self.vc_remaining = self.rate_lim_status[resources][account][vc][remaining]; 
		self.ulu_remaining = self.rate_lim_status[resources][users][ulu][remaining]; 
		self.arls_remaining = self.rate_lim_status[resources][app][arls][remaining]; 
		self.fds_remaining = self.rate_lim_status[resources][friendships][fds][remaining]; 
		self.stfd_remaining = self.rate_lim_status[resources][statuses][stfd][remaining]; 
		self.utml_remaining = self.rate_lim_status[resources][statuses][utml][remaining]; 

		globals()['vc_rem'] = int(self.vc_remaining); 
		globals()['ulu_rem'] = int(self.ulu_remaining); 
		globals()['arls_rem'] = int(self.arls_remaining); 
		globals()['fds_rem'] = int(self.fds_remaining); 
		globals()['stfd_rem'] = int(self.stfd_remaining); 
		globals()['utml_rem'] = int(self.utml_remaining); 
		#print "globals", ulu_rem, vc_rem; 
		#print "curr account remaining, lookup:", self.ulu_remaining, \
		#	"verrified:", self.vc_remaining; 

	## reinitialize relevant used resource counts to defaults 
	def restore_relevant_cnts(self): 
		self.arls_cnt = 0; 
		self.utml_cnt = 0; 
		self.ulu_cnt = 0; 

	## updates relevant used counts for time resources 
	## default assumes each relevant count increments by 1 
	def update_relevant_cnts(self, arls_inc=1, utml_inc=1, ulu_inc=1): 
		self.arls_cnt += arls_inc; 
		self.utml_cnt += utml_inc; 
		self.ulu_cnt += ulu_inc; 

	## wait function due to resource constraints 
	## parameters include 
	##	>> checker (checking whether relevant resource limits neared) 
	##	>> releaser (checking whether relevant resource limits restored to acceptable levels) 
	##	>> sequencer (generates exponential backoffs) 
	## if checker determines wait is necessary 
	## 		periodically rechecks if release condition is met
	## 		periodicity provided by sequencer 
	## restores original use counts when procedures complete 
	def wait(self, checker, arls_use, utml_use, ulu_use, releaser, sequencer): 
		if (checker(arls_use, utml_use, ulu_use, 16)): 
			return 0; 
		insufficient = True; 
		timeout = 2; 
		seq_gen = sequencer(self.max_backoff_lim, 2, timeout); 
		seq_gen.send(None); 
		while(insufficient): 
			print "nearing twitter API limit, waiting:", timeout, "..."; 
			time.sleep(timeout); 
			self.get_rate_usage(); 
			if (timeout >= self.max_backoff_lim): 
				timeout = 2; 
			timeout = seq_gen.send(timeout); 
			print "updated_arls:", self.arls_remaining, "updated_utml:", self.utml_remaining, "updated_ulu:", self.ulu_remaining; 
			if (releaser(self.arls_remaining, self.utml_remaining, self.ulu_remaining, 10)):  
				insufficient = False; 
				self.restore_relevant_cnts(); 
		return 1; 

	## loads testing authentication 
	## contains oauth info for pre-configured app 
	## used when having a single cmd line arg of 'testing' 
	def load_test_auth(self): 
		self.auth_tokens = {};  
		self.auth_tokens[aname] = chenli_auth[aname]; 
		self.auth_tokens[ckey] = chenli_auth[ckey]; 
		self.auth_tokens[csec] = chenli_auth[csec]; 
		self.auth_tokens[atok] = chenli_auth[atok]; 
		self.auth_tokens[asec] = chenli_auth[asec]; 

	## default get authentication 
	## number of different options depending on parameter list 
	## :. len(arglist) == 0 .: manual enter all 5 params 
	## :. len(arglist) == 1 .: manual enter app-name, ckey, csec, auth_dance provides access 
	## :. len(arglist) == 3 .: name, app-name, ckey, csec passed in cmd line, then auth_dance 
	## :. len(arglist) == 5 .: all authentication parameters passed in cmd line 
	@ dectime 
	def load_auth(self, *vars): 
		self.auth_tokens = {}; 
		if (len(vars) == 0): 
			print "input twitter app name for authorization:"; 
			self.auth_tokens[aname] = raw_input(); 
			print "input consumer key (necessary for certain rate limiting information access):"; 
			self.auth_tokens[ckey] = raw_input(); 
			print "input consumer secret (necessary for certain rate limiting information access):"; 
			self.auth_tokens[csec] = raw_input(); 
			print "input access token:"; 
			self.auth_tokens[atok] = raw_input(); 
			print "input access secret:"; 
			self.auth_tokens[asec] = raw_input(); 
		if (len(vars) == 1): 
			print "input twitter app name for authorization:"; 
			self.auth_tokens[aname] = raw_input(); 
			print "input consumer key:"; 
			self.auth_tokens[ckey] = raw_input(); 
			print "input consumer secret:"; 
			self.auth_tokens[csec] = raw_input(); 
			self.auth_tokens[atok], self.auth_tokens[asec] = \
				twitter.oauth_dance(self.auth_tokens[aname], \
				self.auth_tokens[ckey], self.auth_tokens[csec]); 
		elif (len(vars) == 3): 
			self.auth_tokens[aname] = vars[0]; 
			self.auth_tokens[ckey] = vars[1]; 
			self.auth_tokens[csec] = vars[2]; 
			self.auth_tokens[atok], self.auth_tokens[asec] = \
				twitter.oauth_dance(self.auth_tokens[aname], \
				self.auth_tokens[ckey], self.auth_tokens[csec]); 
		elif (len(vars) == 5): 
			self.auth_tokens[aname] = vars[0]; 
			self.auth_tokens[ckey] = vars[1]; 
			self.auth_tokens[csec] = vars[2]; 
			self.auth_tokens[atok] = vars[3]; 
			self.auth_tokens[asec] = vars[4]; 

	## loading necess modules 
	## getting OAth through the loaded auth tokens 
	## setting up initial internal states 	
	@ dectime 
	def load_modules(self): 
		self.auth = twitter.OAuth(self.auth_tokens[atok], self.auth_tokens[asec], \
			self.auth_tokens[ckey], self.auth_tokens[csec]); 
		self.tw = twitter.Twitter(auth = self.auth, retry=True); 

		self.init_rate_lim(); 
		self.update_relevant_cnts(2, 2); 

## inherits members from twitter_resource_record 
## implements friends-statuses specific methods 
class twitter_stats(twitter_resources_record): 

	## default init function 
	## calls on base class init 
	def __init__(self, name): 
		self.name = name; 
		super(twitter_stats, self).__init__(name); 
		self.tw_time = self.twitter_times(); 
	
	## embedded class 
	## contains parsed time record for a single status 	
	class time_record: 
		
		def __init__(self, userid, month, date, hr, min, sec): 
			self.id = int(userid);
			self.month = month.encode('ascii', 'ignore').lower(); 
			self.date = int(date.encode('ascii', 'ignore')); 
			self.hr = int(hr); 
			self.min = int(min); 
			self.sec = int(sec); 

		def show_time(self): 
			print "user", self.id, " at ", self.month, self.date, \
				str(self.hr)+':'+str(self.min)+':'+str(self.sec); 

	## embedded class 
	## contains functions for differentiating status times 
	class twitter_times: 

		def __init__(self): 
			self.get_curr_time(); 
			self.month_map = {'jan':1, 'feb':2, 'mar':3, 'apr':4, \
						'may':5, 'jun':6, 'jul':7, 'aug':8, \
						'sep':9, 'oct':10, 'nov':11, 'dec':12}; 
			self.last_day = {1 : 31, 2 : 28, 3 : 31, 4 : 30, \
						5 : 31, 6 : 30, 7 : 31, 8 : 31, \
						9 : 30, 10 : 31, 11 : 30, 12 : 31}; 
			self.setup(); 

		## sets up reversed-mapping 
		def setup(self): 
			self.rev_month_map = {}; 
			for key in self.month_map.keys(): 
				self.rev_month_map[self.month_map[key]] = key; 

		## maps month str to month id 
		def map_month(self, twitter_mon): 
			return self.month_map[twitter_mon.lower()]; 

		## loads current local-time into obj internal state 
		## requires time module imported 
		def get_curr_time(self): 
			t = time.localtime(); 
			self.curr_month = t.tm_mon; 
			self.curr_date = t.tm_mday; 
			self.curr_hour = t.tm_hour; 
			self.curr_min = t.tm_min; 
			self.curr_sec = t.tm_sec; 

		## provides a displaced month-id from current month 
		def displace_month(self, month_id, offset): 
			return ((month_id + offset) % 12) if (month_id + offset != 0) else 12; 

		## gets the last seven days' dates (month, day) 
		## for finding stats for friends statues over 7 days 
		def last_7days(self): 
			self.last7 = [];  
			for d in range(self.curr_date - 1, self.curr_date - 8, -1): 
				if (d >= 1): 
					self.last7.append((self.curr_month, d)); 
				else: 
					self.last7.append(self.displace_month(self.curr_month, -1), \
						(d % self.lastday[self.displace_month(self.curr_month, -1)]) if (d != 0) \
						else self.last_day[self.displace_month(self.curr_month, -1)]); 

	## getting target user, whose friends (followed individuals) statuses being examined 
	## std command line input 
	@ dectime
	def define_input_user(self): 
		print "enter user name:"; 
		self.curr_name = raw_input(); 

	## get some friends (followed individuals) ids 
	## for testing purposes
	def get_user_friends_ids(self, num): 
		self.curr_friends = self.tw.friends.ids(screen_name = self.curr_name, count = num); 
		self.curr_friends_ids = self.curr_friends[ids]; 

	## getting the list of friend ids of target user 
	## requires a valid target user screen-name 
	## also gets friends (followed individuals') screen-names 
	@ dectime 
	@ dec_timeused 
	def get_user_friends(self, friend_lim=1000000): 
		self.curr_friends = self.tw.friends.ids(screen_name = self.curr_name); 
		self.curr_friend_names = {}; 
		#print self.curr_friends; 
		friend_cnt = 0; 
		for friend in self.curr_friends[ids]: 
			#self.display_ratelim(); 
			lim_checker = self.whether_relevant_lims(); 
			lim_releaser = self.whether_relevant_lims_restored(); 
			sequencer = self.statuses_backoff(); 
			waited = self.wait(lim_checker, 1, 0, 1, lim_releaser, sequencer); 
			self.curr_friend_names[friend] = \
				self.tw.users.lookup(user_id = friend)[0]['screen_name']; 
			print self.curr_name, " follows: friend id: ", friend, \
				self.curr_friend_names[friend]; 
			self.update_relevant_cnts(1, 0, 1); 
			friend_cnt += 1; 
			if (friend_cnt > friend_lim): 
				break; 
		##self.update_relevant_cnts(len(self.curr_friends[ids]), len(self.curr_friends[ids])); 

	## returns a closure of a resource-limit checker 
	## currently examines 3 most frequently encountered limitations 
	def whether_relevant_lims(self): 
		arls_surplus = self.arls_lim - self.arls_cnt; 
		utml_surplus = self.utml_lim - self.utml_cnt; 
		ulu_surplus = self.ulu_lim - self.ulu_cnt; 
		return lambda arls_use, utml_use, ulu_use, margin : \
			((arls_surplus > arls_use + margin) and \
			(utml_surplus > utml_use + margin) and \
			(ulu_surplus > ulu_use + margin)); 

	## returns a closure of a resource-limit restorer 
	## currently examines 3 most frequently encountered limitations 
	def whether_relevant_lims_restored(self): 
		relevant_arls_lim = min(self.arls_lim, 180); 
		relevant_utml_lim = min(self.utml_lim, 180); 
		relevant_ulu_lim = min(self.ulu_lim, 180); 
		print "rel_arls:", relevant_arls_lim, "rel_utml:", relevant_utml_lim, "rel_ulu:", relevant_ulu_lim; 
		return lambda updated_arls_rem, updated_utml_rem, updated_ulu_rem, margin : \
			((updated_arls_rem >= (relevant_arls_lim / 4) - margin) and \
			(updated_utml_rem >= (relevant_utml_lim / 4) - margin) and \
			(updated_ulu_rem >= (relevant_ulu_lim / 4) - margin )); 

	## returns a closure of a sequence generator 
	## provides exponential backoff to a limit, then repeats seq as directed by caller 
	## this is the currently used sequencer 
	def statuses_backoff(self): 
		def backoff_seq(max_backoff, factor, backoff=1): 
			while (True): 
				if (backoff <= max_backoff): 
					backoff = yield backoff; 
				backoff *= factor; 
		return backoff_seq; 

	## returns a closure of a sequence generator 
	## provides hyper-exponential backoff to a limit, then repeats seq as directed by caller 
	## this is an alternative sequencer 
	def alt_statuses_backoff(self): 
		def backoff_seq(max_backoff, exp, backoff=2): 
			while (True): 
				if (backoff <= max_backoff): 
					backoff = yield backoff; 
				backoff = int(math.pow(float(backoff), exp)); 
		return backoff_seq; 

	## get statuses with an API call 
	## first checks to see if the most likely encountered API limits are neared 
	## requests a single page of max-size-allowed 
	## :. successful .: encodes as a series of time_record instances 
	@ dec_timeused 
	def get_statuses(self, userid, curr_page, status_count=200): 
		lim_checker = self.whether_relevant_lims(); 
		lim_releaser = self.whether_relevant_lims_restored(); 
		sequencer = self.statuses_backoff(); 
		waited = self.wait(lim_checker, 1, 1, 0, lim_releaser, sequencer); 
		self.friend_statuses = \
			self.tw.statuses.user_timeline( \
				id=userid, count=status_count, page=curr_page); 
		self.update_relevant_cnts(); 
		status_times = \
			((status[created_at].strip().split()[1], \
			status[created_at].strip().split()[2], \
			status[created_at].strip().split()[3].split(':')) \
			for status in self.friend_statuses); 
		print "getting statuses from user: ", userid, \
			"page:", curr_page, "cnt:", status_times.__sizeof__(); 
		self.curr_status_times = []; 
		for (month, date, [hr, min, sec]) in status_times: 
			self.curr_status_times.append(self.time_record( \
				userid, month, date, hr, min, sec)); 
			#self.curr_status_times[-1].show_time(); 
		self.get_rate_usage(); 

	## checks to see if the least-recent status of the last user-statuses req 
	##		contains a message before the last month 
	def over_month(self): 
		return lambda tweet_mon : \
			((self.tw_time.map_month(tweet_mon) != self.tw_time.curr_month) and \
			(self.tw_time.map_month(tweet_mon) != \
			self.tw_time.displace_month(self.tw_time.curr_month, -1))); 

	## attempts to get all recent statuses of a single twitter user 
	## terminates when the last status gotten is over a month old 
	## iterate over multiple pages of user-statuses when necessary 
	def get_user_statuses(self, userid): 
		self.friends_status_times[userid] = []; 
		page_lim = math.ceil(float(self.max_status_cnt) / float(self.req_status_cnt)); 
		##for i in range(1, int(page_lim + 1), 1): 
		curr_page = 1; 
		curr_status_cnt = -1; 
		month_lim_checker = self.over_month(); 
		while ((curr_status_cnt != 0) and (curr_page < int(page_lim + 1))): 
			self.get_statuses(userid, curr_page); 
			curr_status_cnt = len(self.curr_status_times); 
			self.friends_status_times[userid] += self.curr_status_times; 
			if ((len(self.curr_status_times) >= 1) and \
			(month_lim_checker(self.curr_status_times[-1].month))): 
				return 1;  
			curr_page += 1; 
		return 0; 

	## wrapper loop that gets status-streams of all friends of target user 
	@ dec_timeused 
	def get_friends_statuses(self): 
		self.friends_status_times = {}; 
		for friend_id in self.curr_friends[ids]: 
			self.get_user_statuses(friend_id); 

	## collocate stats of friends-statuses 
	## looks for those within the previous 7 days 
	@ dectime 
	def collocate_days(self): 
		self.tw_time.last_7days(); 
		#print self.tw_time.last7; 
		self.friends_tweet_lookup = {}; 
		for friend_id in self.friends_status_times.keys(): 
			self.friends_tweet_lookup[friend_id] = {}; 
			for record in self.friends_status_times[friend_id]: 
				if (record.month not in self.friends_tweet_lookup[friend_id]): 
					self.friends_tweet_lookup[friend_id][record.month] = {}; 
				if (record.date not in self.friends_tweet_lookup[friend_id][record.month]): 
					self.friends_tweet_lookup[friend_id][record.month][record.date] = 1; 
				else: 
					self.friends_tweet_lookup[friend_id][record.month][record.date] += 1; 
			#print friend_id, self.curr_friend_names[friend_id]; 
			#print self.friends_tweet_lookup[friend_id]; 

	## prints out the collected stats 
	## and also outputs it into a file defined by the target user name 
	@ dectime 
	def output_friends_stats(self, filename): 
		filename = self.curr_name+'.friends-statuses.'+filename; 
		handle = open(filename, 'w'); 
		for friend_id in self.friends_tweet_lookup.keys(): 
			handle.write(self.curr_name+'\t'+'follows\t'); 
			handle.write("user-id:"+str(friend_id)+' '); 
			handle.write(self.curr_friend_names[friend_id]+'\n');  
			for (month, day) in self.tw_time.last7: 
				month_name = self.tw_time.rev_month_map[month]; 
				if ((month_name in self.friends_tweet_lookup[friend_id]) \
				and (day in self.friends_tweet_lookup[friend_id][month_name])): 
					print "ON", (month, day), self.curr_friend_names[friend_id], \
						"tweeted", self.friends_tweet_lookup[friend_id][month_name][day], "times"; 
					handle.write('\t'+month_name+'\t'+str(day)+'\t'); 
					handle.write("tweet-cnt: "+str(self.friends_tweet_lookup[friend_id][month_name][day])+'\n'); 
				else: 
					print "ON", (month, day), self.curr_friend_names[friend_id], "did not tweet"; 
					handle.write('\t'+month_name+'\t'+str(day)+'\t'); 
					handle.write("tweet-cnt: "+str(0)+'\n'); 
			handle.write('\n'); 
		print "output written to:", filename; 
		handle.close(); 

## default __main__ func 
def run(**kvars): 
	twst = twitter_stats("new1"); 
	if (len(kvars.keys()) == 0): 
		twst.load_auth(); 
	elif ((len(kvars.keys()) == 1) and (kvars['control'] == test)): 
		twst.load_test_auth(); 
	elif ((len(kvars.keys()) == 1) and (kvars['control'] == access)): 
		twst.load_auth("access"); 
	elif ((len(kvars.keys()) == 3) and (aname in kvars.keys()) \
	and (ckey in kvars.keys()) and (csec in kvars.keys())): 
		twst.load_auth(kvars[aname], kvars[ckey], kvars[csec]); 
	elif ((len(kvars.keys()) == 5) and (aname in kvars.keys()) \
	and (ckey in kvars.keys()) and (csec in kvars.keys()) \
	and (atok in kvars.keys()) and (asec in kvars.keys())):  
		twst.load_auth(kvars[aname], kvars[ckey], kvars[csec], kvars[atok], kvars[asec]); 
	twst.load_modules(); 

	twst.get_rate_usage(); 	
	twst.define_input_user(); 
	twst.get_user_friends(); 
	twst.get_rate_usage(); 	

	twst.get_friends_statuses(); 
	twst.collocate_days(); 
	twst.output_friends_stats("output.txt"); 

## cmd line arglist switch: 
if __name__ != "__main__": 
	pass; 
elif (len(sys.argv) == 1): 
	run(); 
elif ((len(sys.argv) == 2) and ((sys.argv[1] == test) or (sys.argv[1] == access))): 
	run(control=sys.argv[1]); 
elif (len(sys.argv) == 4): 
	run(app_name=sys.argv[1], consumer_key=sys.argv[2], consumer_secret=sys.argv[3]); 
elif (len(sys.argv) == 6): 
	run(app_name=sys.argv[1], consumer_key=sys.argv[2], consumer_secret=sys.argv[3], \
		access_token=sys.argv[4], access_secret=sys.argv[5]); 
else: 
	### shows acceptable command line structure 
	print "cmd line arguments not correctly formatted"; 
	print "potential input formats:\n"; 
	print "-> cmd line with no args to manually input:" 
	print "\tapp-name, consumer-key, consumer-secret, access-token, access-secret"; 
	print "-> cmd line with single arg 'access' for mannually inputting only:" 
	print "\tapp-name, consumer-key, consumer-secret to authenticate"; 
	print "\tby getting new access token/secret !"; 
	print "\tmay require browser access, login to twitter account";  
	print "\t\tand entering returned pin !!!"; 
	print "-> use single arg 'testing' for testing with default authentication tokens."; 
	print "\tuse a default access-authorized app"; 
	print "-> 3 args:"; 
	print "\tapp-name, consumer-key, consumer-secret"; 
	print "-> 5 args:"; 
	print "\tapp-name, consumer-key, consumer-secrete, access-token, access-secret"; 

