import uuid
from locust import HttpUser, task, between
import random

class ApiFacility(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.auth_header_admin = {}
        login_admin_payload = {"username": "admin", "password": "admin123"}

        with self.client.post("/auth/login", json=login_admin_payload, name="Admin Login", catch_response=True) as res:
            if res.status_code == 200:
                data = res.json()
                token = data.get("token") or data.get("accessToken") or data.get("jwt")
                if token:
                    self.auth_header_admin = {"Authorization": f"Bearer {token}"}
                    res.success()
                else:
                    res.failure("Admin token NOT FOUND in JSON")
            else:
                res.failure(f"Admin login failed: {res.status_code}")

    @task
    def facility_test(self):
        facility_id = str(uuid.uuid4())[:8]
        facility_name = f"Salieri's football pitch {facility_id}"
        facility_location = f"Little Italy {facility_id}"
        facility_description = "A large pitch next to Work's Quater."
        facility_contact = f"{facility_id}"
        facility_image = f"{facility_id}"
        facility_adress = f"{facility_id} Long Street, Lost Heaven"

        facility_payload = {
            "facility_id": facility_id,
            "facility_name": facility_name,
            "facility_location": facility_location,
            "facility_description": facility_description,
            "facility_contact": facility_contact,
            "facility_image": facility_image,
            "facility_adress": facility_adress
        }

        # 1. Facility creation
        with self.client.post("/facilities/add", json=facility_payload, name="/facilities/add",
                              catch_response=True) as add_facility_res:
            if add_facility_res.status_code in [200, 201]:
                data = add_facility_res.json()
                facility_id = data.get("id") or data.get("facilityId") or data.get("uuid")
                add_facility_res.success()
            else:
                add_facility_res.failure(f"Creation facility failed: {add_facility_res.status_code}")
                return

        if not facility_id:
            return

        # 2. Get facility by id
        with self.client.get(f"/facilities/{facility_id}", headers=self.auth_header_admin, name="/facilities/[id]",
                             catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by ID failed: {res.status_code}")

        # 3. Update facility
        random_capacity = random.randint(1, 30)
        with self.client.patch(f"/facilities/update/{facility_id}", json={f"capacity": {random_capacity}},
                               headers=self.auth_header_admin, name="/facilities/update/[id]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Update failed: {res.status_code}")

        # 5. Admin: Get user by name
        with self.client.get(f"/user/by-username/{username}", headers=self.auth_header_admin,
                             name="/user/by-username/[name]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by Name failed: {res.status_code}")

        # 6. Admin: Get user by mail
        with self.client.get(f"/user/mail/{email}", headers=self.auth_header_admin,
                             name="/user/mail/[mail]", catch_response=True) as res:
            if res.status_code == 200:
                res.success()
            else:
                res.failure(f"Admin Get by Mail failed: {res.status_code}")

        # 7. Admin: Delete user by id
        with self.client.delete(f"/user/delete/{user_id}", headers=self.auth_header_admin,
                                name="/user/delete/[id]", catch_response=True) as res:
            if res.status_code in [200, 204]:
                res.success()
            else:
                res.failure(f"Admin Delete failed: {res.status_code}")





