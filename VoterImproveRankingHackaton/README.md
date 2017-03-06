Website signup script with random email and allows that username to click on vote. 
Then logout from the site and repeat it randomly

Script uses wide variety of emails and names. 
Voting is  implemented in random interval (sleep_duration). 
It is in seconds, in range [first_number, second_number). Additional logging added. Bunch of proxies added.

Implemented commenting. Comments should be located in comments.txt file, separated by newline.
video comment is called "Commentaires" in french ....top of the page

Implemented automatic proxy. It recieves only proxies from France. If proxy is bad, it removes it from the list. 
If the proxy list is empty, it fetches new proxy list (refreshed on the site automatically every minute).


