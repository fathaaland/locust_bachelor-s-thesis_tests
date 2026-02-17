import uuid
from locust import HttpUser, task, between


class ApiUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def complete_flow(self):
        # 1. Registration
        unique_id = str(uuid.uuid4())[:8]
        username = f"Vaclav_{unique_id}"
        password = "Venca321"

        reg_payload = {
            "username": username,
            "password": password,
            "email": f"{username}@gmail.com"
        }

        with self.client.post("/auth/register", json=reg_payload) as reg_res:

            if reg_res.status_code == 200 or reg_res.status_code == 201:
                user_id = reg_res.json().get("id")
                user_username = reg_res.json().get("username")
                user_mail = reg_res.json().get("email")

            else:
                reg_res.failure(f"Registration failed: {reg_res.status_code}")
                return

        # 2. Login
        login_payload = {"username": username, "password": password}
        with self.client.post("/auth/login", json=login_payload) as login_res:
            if login_res.status_code == 200:
                token = login_res.json().get("token")
                self.auth_header = {"Authorization": f"Bearer {token}"}
            else:
               return


        # 3. Get user by id
        with self.client.get(
                f"/user/{user_id}",
                headers=self.auth_header,
                name="/user/update/[id]",
                catch_response=True
        ) as get_by_id_res:
            if get_by_id_res.status_code == 200 or get_by_id_res.status_code == 201:
                get_by_id_res.success()
            else:
                get_by_id_res.failure(f"Get by id failed: {get_by_id_res.status_code}")
                return


        # 4. Update user
        with self.client.patch(
                    f"/user/update/{user_id}",
                    json={"password": "updated password123"},
                    headers=self.auth_header,
                    name="/user/update/[id]",
                    catch_response=True
            ) as update_res:

                if update_res.status_code == 200 or update_res.status_code == 201:
                    updated_id = update_res.json().get("id")
                    update_res.success()
                else:
                    update_res.failure(f"Update failed: {update_res.status_code} - {update_res.text}")
                    return


