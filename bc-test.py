import uuid
from locust import HttpUser, task, between


class ApiUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def complete_flow(self):
        # 1. Registration
        unique_id = str(uuid.uuid4())[:8]
        username = f"Vaclav_{unique_id}"
        password = "Venca321"

        reg_payload = {
            "username": username,
            "password": password,
            "email": f"{username}@dobrovsky.com"
        }

        with self.client.post("auth/register", json=reg_payload) as reg_res:

            if reg_res.status_code != 200:
                print("Goodbye!")
                exit()

        # 1. Login
        login_payload = {"username": username, "password": password}