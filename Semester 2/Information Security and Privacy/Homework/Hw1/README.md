# Information Security and Privacy - Homework 1
### Mocanu Alexandru, Data Science
***

## Exercise 1
We open the page's source and observe in the **<script>** that the password is compared against a one-time-pad encoding of user's email for which the key is given in plain. We therefore run the encryption in the browser's console and using this password we obtain the token.
***

## Exercise 2
Starting from the statement that after logging in E-Corp will automatically know when you're back, we can deduce that there are some kind of cookies that may be of interest. We find that there is indeed a **LoginCookie**. After using **base64** decryption, we find out that the cookie content is actually the user's email address along with its status (user/administrator). Thus, computing the base64 encoding of the previous plain cookie content in which we replace *user* by *administator* (I first tried *admin*, but it didn't work) holds the cookie content that gives us admin access. We remove the cookie generated at login and replace it with a cookie with the content generated above. This gives us admin access and we retrieve the token.
***

## Exercise 3
As suggested in the statement, we collect http packages in the queue and decode their content. We see that there are packages containing a dictionary in which there is a *'shipping_address': 'lausanne'* key-value pair. We thus parse this json content and replace 'lausanne' with our email address. Then, we use the requests package to send the new message to the server in the json/application format. This leads to the server responding with the token. The script used for this exercise is *interceptor.py* which automatically intercepts, changes and sends the desired package.
***

## Exercise 4
We use the script from the previous exercise with a small modification to only list packages' contents. Given the small number of secrets and the small number of different packages that we observe, we manually extract the secrets. Using *secret_sender.py* we then send the secrets to the server and get the token.
***