# Twitter Rate Limiting 

## Rate limit status 
Rate limits are segmented by specific athorizations that are performed through Twitter API, each type has a access, such as place_id in geo information, or direct_messages sent.  The rate limits are assessed on a per user, as well as per application basis. The limit for individual access types are often set at a value within a specific period of time, such as 180 within a 15 minute time.  For each of these access type, Twitter API provides set of fields within its **rate\_limit\_status** object, reporting the limitation on the count of accesses of this type, and the amount of allowed accesses remaining.  The amount of remaining for each access type is updated in the rate\_limit\_status, which can be used to assess  

## Exceeding rate limit 
Exceeding a specific rate limit for an access type within the specified window results in Twitter API returning HTTP 429 **“Too Many Requests"** code to the client application.  The specific limits that may be exceeded can be accessed at <https://dev.twitter.com/rest/public/rate-limits> .  According to Twitter, there may be some inconsistencies at times for rate limit values; it is also difficult to always correctly determine the exact type of access and which rate limit resource an access is consumed. 
