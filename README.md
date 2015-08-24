## Python modules 
requires _python2.7_ as well as imported modules: _sys, math, time, twitter, unittest_ 

## twitter_stats.py CMD line options 

run with the following command line options: 

- cmd line with no args to manually input: 

   **app-name, consumer-key, consumer-secret, access-token, access-secret** 

- cmd line with single arg 'access' for mannually inputting only:

   **app-name, consumer-key, consumer-secret** 
   to authenticate by getting new access token/secret
   may require browser access, login to twitter account and entering returned pin 

- use single arg 'testing' for testing with default authentication tokens 

   use a default access-authorized app 

- 3 args on command line: 

    app-name, consumer-key, consumer-secret 

- 5 args on command line: 

    app-name, consumer-key, consumer-secrete, access-token, access-secret 

## twitter\_stats\_test.py Notes: 
No arguments necessary.  However, need to have __currently up-to-date__ authentication tokens, in the file **twitter\_auth.py**.  **NEED TO REPLACE** *globals()['curr\_auth']* members with currently valid OAuth parameters, for unit-tests to work correctly: 

- aname : twitter app name 
- ckey : consumer-key 
- csec : consumer-secret 
- atok : access-token 
- asec : access-secret 

**Replace the above members** with currently valid OAuth information in *globals()['curr\_auth']* within the included **twitter\_auth.py** file in src/ 