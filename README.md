# Fastbin 
An implementation of pastebin.com using fastapi

**I will be using this readme as log file for what I learn each day while implementing this app**.

## Day 2 (Authentication)
### Token Blacklisting
Theres a total of 3 ways to implement token blacklisting (on the backend obv)

#### 1. Database Blacklist :-
1. Create a JTI (JWT ID) and store it in the payload.
2. When login/refresh endpoints are hit , check whether the JTI is blacklisted or not using a simple select query.
3. When the logout endpoint is hit add the JTI to the blacklist table.
4. Initialize a background job and cleanup the blacklist table regularly.

**Pros**
- No additional infrastructure (uses existing DB)
- Persistent across restarts

**Cons**
- Slower than Redis (disk I/O vs memory)
- Requires manual cleanup job
- Database load increases with traffic

#### 2. Redis Blacklist :-
1. Create a JTI (JWT ID) and store it in the payload.
2. When login/refresh endpoints are hit , check for JTI in Redis KV , if its present then the token is not blacklisted.
3. When logout endpoint hit then just delete the JTI from Redis KV.

**Pros**
- Fast: In-memory operations (microseconds)
- Auto-cleanup: TTL (Time To Live) automatically removes expired tokens

**Cons**
- Requires Redis infrastructure
- Non Persistent: Doesnt survive database restarts

#### 3. Redis & Database Blacklist (Hybrid) :-
1. Create a JTI (JWT ID) and store it in the payload.
2. When login/refresh endpoints are hit , check in Redis KV first then check in Database
(if needed).
3. When logout endpoint is hit , delete the JTI from both.
4. Basically, read from both and write to both

**Pros**
- Fast reads (Redis)
- Persistent and reliable (Database)
- Survives Redis crashes

**Cons**
- Most complex implementation
- Requires both Redis and Database
- Synchronization overhead
- Higher operational cost

This app wont require login to access the basic functionalities so database blacklist seems like a good choice.
