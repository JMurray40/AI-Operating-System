

test    : oversized_output
ok      : True
done    : True
reason  : length
eval    : 5
wall_ms : 3911
content : 
err     : 






test    : malformed_model
ok      : False
reason  : 
wall_ms : 18
content : 
err     : The remote server returned an error: (404) Not Found.






test      : cancellation
cancelled : False
wall_ms   : 2922
err       : 
content   : 






test    : timeout_30s
ok      : False
wall_ms : 30008
err     : The request was aborted: The operation has timed out.
content : 






test    : context_oversize
ok      : False
done    : 
reason  : 
wall_ms : 90021
peval   : 
content : 
err     : The request was aborted: The operation has timed out.






test : concurrent_2
w1   : 120580
c1   : 
r1   : 
w2   : 120649
c2   : 
r2   : 






test    : server_health_after
health  : up
wall_ms : 0




