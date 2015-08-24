#!/usr/bin/python 

import sys; 
import unittest; 

import twitter_stats as TS; 
import twitter_auth as TA; 

class TestAuth(unittest.TestCase): 

	def setUp(self): 
		self.twst = TS.twitter_stats("test1"); 
		self.aname = TA.curr_auth[TA.aname]; 
		self.ckey = TA.curr_auth[TA.ckey]; 
		self.csec = TA.curr_auth[TA.csec]; 
		self.atok = TA.curr_auth[TA.atok]; 
		self.asec = TA.curr_auth[TA.asec]; 
		
		self.auth = TS.twitter.OAuth(self.atok, self.asec, self.ckey, self.csec); 
		self.tw = TS.twitter.Twitter(auth = self.auth, retry=True); 

	## testing manual entry of all 5 auth parameters
	def test_auth_manual(self): 
		self.twst.load_auth(); 
		self.assertTrue(TS.aname in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.ckey in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.csec in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.atok in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.asec in self.twst.auth_tokens.keys()); 

	## testing manual entry of name, ckey, csec, and auth_dance
	def test_auth_semimanual(self): 
		self.twst.load_auth("access"); 
		self.assertTrue(TS.aname in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.ckey in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.csec in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.atok in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.asec in self.twst.auth_tokens.keys()); 

	## testing entry of passed in auth parameters
	def test_auth_5params(self): 
		self.twst.load_auth(self.aname, self.ckey, self.csec, self.atok, self.asec); 
		self.assertTrue(TS.aname in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.ckey in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.csec in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.atok in self.twst.auth_tokens.keys()); 
		self.assertTrue(TS.asec in self.twst.auth_tokens.keys()); 

	## testing OAth, and loading of initial components 
	def test_load_modules(self): 
		self.twst.load_auth(self.aname, self.ckey, self.csec, self.atok, self.asec); 
		self.twst.load_modules(); 
		self.assertEqual(type(self.twst.auth), type(self.auth)); 
		self.assertEqual(type(self.twst.tw), type(self.tw)); 

	def tearDown(self): 
		del self.auth; 
		del self.tw; 
		del self.twst;  

class TestUser(unittest.TestCase): 

	def setUp(self): 
		self.twst = TS.twitter_stats("test1"); 
		self.aname = TA.curr_auth[TA.aname]; 
		self.ckey = TA.curr_auth[TA.ckey]; 
		self.csec = TA.curr_auth[TA.csec]; 
		self.atok = TA.curr_auth[TA.atok]; 
		self.asec = TA.curr_auth[TA.asec]; 
		
		self.twst.load_auth(self.aname, self.ckey, self.csec, self.atok, self.asec); 
		self.twst.load_modules(); 
		
		self.auth = TS.twitter.OAuth(self.atok, self.asec, self.ckey, self.csec); 
		self.tw = TS.twitter.Twitter(auth = self.auth, retry=True); 
		self.rate_lim_status = self.tw.application.rate_limit_status(); 

		self.target_name = "sms1337"; 

	## testing update of usage rate 
	def test_rate_usage(self): 
		self.twst.get_rate_usage(); 
		self.assertEqual(type(self.twst.rate_lim_status), type(self.rate_lim_status)); 
		self.assertNotEqual(self.twst.vc_remaining, -1);
		self.assertNotEqual(self.twst.ulu_remaining, -1); 
		self.assertNotEqual(self.twst.arls_remaining, -1); 
		self.assertNotEqual(self.twst.fds_remaining, -1); 
		self.assertNotEqual(self.twst.stfd_remaining, -1); 
		self.assertNotEqual(self.twst.utml_remaining, -1); 

	## testing inputting target user name 
	def test_input_user(self): 
		self.twst.define_input_user(); 
		self.assertTrue(hasattr(self.twst, "curr_name")); 
		self.assertNotEqual(self.twst.curr_name, ""); 

	## testing getting friends of target user 
	def test_some_friends(self): 
		self.friends_num = 20; 
		self.twst.curr_name = self.target_name; 
		self.twst.get_user_friends_ids(self.friends_num); 
		self.friends_ids = self.tw.friends.ids( \
			screen_name = self.target_name, count = self.friends_num)[TS.ids]; 
		for i in range(0, min(self.friends_num, len(self.friends_ids)), 1): 
			self.assertEqual(self.friends_ids[i], self.twst.curr_friends_ids[i]); 

	def tearDown(self): 
		del self.auth; 
		del self.tw; 
		del self.rate_lim_status; 
		del self.twst;  

class TestFriends(unittest.TestCase): 

	def setUp(self): 
		self.twst = TS.twitter_stats("test1"); 
		self.aname = TA.curr_auth[TA.aname]; 
		self.ckey = TA.curr_auth[TA.ckey]; 
		self.csec = TA.curr_auth[TA.csec]; 
		self.atok = TA.curr_auth[TA.atok]; 
		self.asec = TA.curr_auth[TA.asec]; 

		self.twst.load_auth(self.aname, self.ckey, self.csec, self.atok, self.asec); 
		self.twst.load_modules(); 
		
		self.auth = TS.twitter.OAuth(self.atok, self.asec, self.ckey, self.csec); 
		self.tw = TS.twitter.Twitter(auth = self.auth, retry=True); 
		self.rate_lim_status = self.tw.application.rate_limit_status(); 

		self.target_name = "sms1337"; 
		self.friends_num = 20; 
		self.twst.curr_name = self.target_name; 
		self.twst.get_user_friends(self.friends_num); 
	
		self.friends_ids = self.tw.friends.ids( \
			screen_name = self.target_name, count = self.friends_num)[TS.ids]; 
		self.friends_names = []; 

	## testing looking up names of friends of target user 
	def test_get_names(self): 
		for friend_id in self.friends_ids: 
			name = self.tw.users.lookup(user_id = friend_id)[0]['screen_name']; 
			self.assertEqual(name, self.twst.curr_friend_names[friend_id]); 

	## testing updating relevant time-resource counts 
	def test_relevant_cnts(self): 
		self.cnt_increment = 3; 
		self.prev_arls = self.twst.arls_cnt; 
		self.prev_utml = self.twst.utml_cnt; 
		self.prev_ulu = self.twst.ulu_cnt; 
		self.twst.update_relevant_cnts(self.cnt_increment, self.cnt_increment, self.cnt_increment); 
		self.assertEqual(self.prev_arls + self.cnt_increment, self.twst.arls_cnt); 
		self.assertEqual(self.prev_utml + self.cnt_increment, self.twst.utml_cnt); 
		self.assertEqual(self.prev_ulu + self.cnt_increment, self.twst.ulu_cnt); 

	def tearDown(self): 
		del self.auth; 
		del self.tw; 
		del self.twst; 

class TestStatus(unittest.TestCase): 

	def setUp(self): 
		self.twst = TS.twitter_stats("test1"); 
		self.aname = TA.curr_auth[TA.aname]; 
		self.ckey = TA.curr_auth[TA.ckey]; 
		self.csec = TA.curr_auth[TA.csec]; 
		self.atok = TA.curr_auth[TA.atok]; 
		self.asec = TA.curr_auth[TA.asec]; 
		
		self.twst.load_auth(self.aname, self.ckey, self.csec, self.atok, self.asec); 
		self.twst.load_modules(); 
		
		self.auth = TS.twitter.OAuth(self.atok, self.asec, self.ckey, self.csec); 
		self.tw = TS.twitter.Twitter(auth = self.auth, retry=True); 
		self.rate_lim_status = self.tw.application.rate_limit_status(); 

		self.target_name = "sms1337"; 
		self.friends_num = 20; 
		self.twst.curr_name = self.target_name; 
		self.twst.get_user_friends(self.friends_num); 
	
		self.friends_ids = self.tw.friends.ids( \
			screen_name = self.target_name, count = self.friends_num)[TS.ids]; 
		self.friends_names = []; 

	## specially defined assertEqual for embedded time_record 
	def time_record_equal(self, record1, record2): 
		return ((record1.month == record2.month) and \
			(record1.date == record2.date) and \
			(record1.hr == record2.hr) and \
			(record1.min == record2.min) and \
			(record1.sec == record2.sec)); 

	## testing individual time_record 
	def test_record(self): 
		self.month_name = "Jun"; 
		self.date = '22'; 
		self.hr = '18'; 
		self.min = '45'; 
		self.sec = '00'; 
		new_record = TS.twitter_stats.time_record(1, self.month_name, self.date, \
			self.hr, self.min, self.sec); 
		self.assertEqual(new_record.month, self.month_name.encode('ascii', 'ignore').lower()); 
		self.assertEqual(new_record.date, int(self.date)); 
		self.assertEqual(new_record.hr, int(self.hr)); 
		self.assertEqual(new_record.min, int(self.min)); 
		self.assertEqual(new_record.sec, int(self.sec)); 

	## testing getting a page of statuses of a friend 
	## and testing writing to records 
	def test_page_status(self): 
		self.curr_friend = self.friends_ids[0];  
		self.twst.get_statuses(self.curr_friend, 1); 
		self.friend_statuses = \
			self.tw.statuses.user_timeline(id=self.curr_friend, count=200, page=1); 

		self.curr_times = \
			((status[TS.created_at].strip().split()[1], \
			status[TS.created_at].strip().split()[2], \
			status[TS.created_at].strip().split()[3].split(':')) \
			for status in self.friend_statuses); 
		self.curr_records = []; 
		for time in self.curr_times: 
			self.curr_records.append(TS.twitter_stats.time_record( \
				self.curr_friend, time[0], time[1], time[2][0], time[2][1], time[2][2]));  
		record_cnt = 0; 
		for record in self.curr_records: 
			self.assertTrue(self.time_record_equal(record, self.twst.curr_status_times[record_cnt])); 
			record_cnt += 1; 

	## testing getting a collocation of records 
	## getting the necessary stats for a single friend 
	def test_collocation(self): 
		self.curr_friend = self.friends_ids[0];  
		self.friend_statuses = \
			self.tw.statuses.user_timeline(id=self.curr_friend, count=200, page=1); 
		self.curr_times = \
			((status[TS.created_at].strip().split()[1], \
			status[TS.created_at].strip().split()[2], \
			status[TS.created_at].strip().split()[3].split(':')) \
			for status in self.friend_statuses); 
		self.curr_records = []; 
		for time in self.curr_times: 
			self.curr_records.append(TS.twitter_stats.time_record( \
				self.curr_friend, time[0], time[1], time[2][0], time[2][1], time[2][2]));  

		self.twst.friends_status_times = {}; 
		self.twst.friends_status_times[self.curr_friend] = self.curr_records; 
		self.twst.collocate_days(); 

		self.single_lookup = {}; 
		for record in self.curr_records: 
			if (record.month not in self.single_lookup): 
				self.single_lookup[record.month] = {}; 
			if (record.date not in self.single_lookup[record.month]): 
				self.single_lookup[record.month][record.date] = 1; 
			else: 
				self.single_lookup[record.month][record.date] += 1; 
		self.assertEqual(self.twst.friends_tweet_lookup[self.curr_friend], self.single_lookup);

	def tearDown(self): 
		del self.auth; 
		del self.tw; 
		del self.twst;  


def main_test(): 
	if __name__ == "__main__": 
		unittest.main(); 

def suite_tests(): 
	asuite = unittest.TestSuite(); 
	asuite.addTest(TestAuth('test_auth_manual')); 
	asuite.addTest(TestAuth('test_auth_semimanual')); 
	asuite.addTest(TestAuth('test_auth_5params')); 
	asuite.addTest(TestAuth('test_load_modules')); 

	usuite = unittest.TestSuite(); 
	usuite.addTest(TestUser('test_rate_usage')); 
	usuite.addTest(TestUser('test_input_user')); 
	usuite.addTest(TestUser('test_some_friends')); 

	fsuite = unittest.TestSuite(); 
	fsuite.addTest(TestFriends('test_get_names')); 
	fsuite.addTest(TestFriends('test_relevant_cnts')); 
	fsuite.addTest(TestStatus('test_record')); 
	fsuite.addTest(TestStatus('test_page_status')); 
	fsuite.addTest(TestStatus('test_collocation')); 

	allsuites = unittest.TestSuite([asuite, usuite, fsuite]); 
	##allsuites = unittest.TestSuite([fsuite]); 
	return allsuites; 

def run_suite(suites): 
	unittest.TextTestRunner(verbosity=2).run(suites); 

run_suite(suite_tests()); 

