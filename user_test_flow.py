import uuid
from locust import HttpUser, task, between, events


class ApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.auth_header_admin = None  # Inicializace

        login_admin_payload = {"username": "admin", "password": "admin123"}

        with self.client.post("/auth/login", json=login_admin_payload, name="Admin Login", catch_response=True) as res:
            if res.status_code == 200:
                data = res.json()
                token = data.get("token") or data.get("accessToken") or data.get("jwt")
                if token:
                    self.auth_header_admin = {"Authorization": f"Bearer {token}"}
                    res.success()
                else:
                    res.failure("Token nenalezen v JSON odpovědi")
            else:
                res.failure(f"Admin login failed ({res.status_code}): {res.text}")
                self.environment.runner.quit()

    @task
    def user_flow(self):
        if not self.auth_header_admin:
            return

        unique_id = str(uuid.uuid4())[:8]
        username = f"Vaclav_{unique_id}"
        password = "Venca321"
        email = f"{username}@gmail.com"
        reg_payload = {"username": username, "password": password, "email": email}

        user_id = None
        # 1. User registration
        with self.client.post("/auth/register", json=reg_payload, name="/auth/register",
                              catch_response=True) as reg_res:
            if reg_res.status_code in [200, 201]:
                data = reg_res.json()
                user_id = data.get("id") or data.get("userId") or data.get("uuid")
                reg_res.success()
            else:
                reg_res.failure(f"Reg failed ({reg_res.status_code}): {reg_res.text}")
                return

        if not user_id:
            return

        # 2. Login user (běžný uživatel, ne admin)
        login_payload = {"username": username, "password": password}
        with self.client.post("/auth/login", json=login_payload, name="/auth/login", catch_response=True) as login_res:
            if login_res.status_code == 200:
                login_res.success()
            else:
                login_res.failure(f"User login failed ({login_res.status_code}): {login_res.text}")
                return

        # 3. Get user by id (vyžaduje admin token)
        with self.client.get(f"/user/{user_id}", headers=self.auth_header_admin, name="/user/[id]",
                             catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by ID failed ({res.status_code}): {res.text}")

        # 4. Update user by id (vyžaduje admin token)
        with self.client.patch(f"/user/update/{user_id}", json={"password": "updatedByAdmin123"},
                               headers=self.auth_header_admin, name="/user/update/[id]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Update failed ({res.status_code}): {res.text}")

        # 5. Get user by username (vyžaduje admin token)
        with self.client.get(f"/user/by-username/{username}", headers=self.auth_header_admin,
                             name="/user/by-username/[name]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by Name failed ({res.status_code}): {res.text}")

        # 6. Get user by mail (vyžaduje admin token)
        with self.client.get(f"/user/mail/{email}", headers=self.auth_header_admin,
                             name="/user/mail/[mail]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by Mail failed ({res.status_code}): {res.text}")

        # 7. Delete user by id (vyžaduje admin token)
        with self.client.delete(f"/user/delete/{user_id}", headers=self.auth_header_admin,
                                name="/user/delete/[id]", catch_response=True) as res:
            if res.status_code in [200, 204]:
                res.success()
            else:
                res.failure(f"Admin Delete failed ({res.status_code}): {res.text}")