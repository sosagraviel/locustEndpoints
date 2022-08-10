import json
import string
import random
import time
from locust import HttpUser, SequentialTaskSet, TaskSet, task, between

USERS = 1
STEP_TIME = 1
STEP_LOAD = 1
SPAWN_RATE = 1


class WebTasks(SequentialTaskSet):
    count = 0

    def on_start(self):
        print("start")
        self.register()

    @task(1)
    def register(self):
        self.count += 1
        print(self.count)
        print("Register")
        response_register = self.client.post("/v1/register", {"name": "test",
                                                              "email": "test+" + str(877) + "@decemberlabs.com",
                                                              "password": "get_random_string",
                                                              "verificationToken": "$2a$10$SpEjDf5qlSALeNMCSKNVuO19u2eQ2SKxuUBhWxVVOIhSjNCOyy96u"})
        print("this is the register response " + response_register.text)
        token_register = json.loads(response_register.text.encode('utf8'))['data']
        print("this is the token register " + token_register)

        print("validate mail")
        with self.client.get(
                "/v1/register/" + "test+" + str(877) + "@decemberlabs.com" + "/" + str(token_register),
                catch_response=True, name="HTTP 200") as validate_res:
            if validate_res.status_code == 200:
                print("the validate response was success " + str(validate_res.status_code))
                validate_res.success()
            else:
                print("the validate response was failure " + str(validate_res.status_code))
                validate_res.failure("got different status code than 200")

        print("login")
        login_res = self.client.post("/v1/authenticate", {
            "email": "test+" + str(877) + "@decemberlabs.com",
            "password": "get_random_string"})
        print("this is the Login response " + login_res.text)
        data_token_login = json.loads(login_res.text.encode('utf8'))['data']
        print("this is the data login " + str(data_token_login))
        token_login = data_token_login['token']
        print("this is the token login " + str(token_login))
        header = {
            'Authorization': 'Bearer ' + str(token_login),
            'content-type': 'application/json', 'accept': 'application/json'
        }
        with self.client.get(
                "/v1/users/" + str(token_register), headers=header,
                catch_response=True, name="HTTP 200") as delete_user_res:
            if delete_user_res.status_code == 200:
                print("the delete response was success " + str(delete_user_res.status_code))
                delete_user_res.success()
            else:
                print("the delete response was failure " + str(delete_user_res.status_code))
                delete_user_res.failure("got different status code than 200 deleting the user")


class WebUser(HttpUser):
    # host = "https://api.openbrewerydb.org"
    host = "https://api.elliegrid.inhouse.decemberlabs.com"
    tasks = [WebTasks]
    wait_time = between(1, 9)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
