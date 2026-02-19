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
                    res.failure("Admin token NOT FOUND")
            else:
                res.failure(f"Admin login failed: {res.status_code}")

    @task
    def facility_test(self):
        f_uuid = str(uuid.uuid4())[:8]
        facility_payload = {
            "name": f"Pitch {f_uuid}",
            "type": "FOOTBALL",
            "location": f"Little Italy {f_uuid}",
            "description": "Large pitch.",
            "contactNumber": f"123{f_uuid}",
            "capacity": "4",
            "imageUrl": "https://example.com/images/pitch.jpg",
            "address": f"Street {f_uuid}"
        }

        facility_id = None
        facility_name = None
        facility_type = "FOOTBALL"

        # 1. Facility creation
        with self.client.post("/facilities/add", json=facility_payload, headers=self.auth_header_admin,
                              name="/facilities/add", catch_response=True) as add_res:
            if add_res.status_code in [200, 201]:
                data = add_res.json()
                facility_id = data.get("id") or data.get("facilityId")
                facility_name = data.get("name") or data.get("facilityName")
                add_res.success()
            else:
                add_res.failure(f"Creation failed: {add_res.status_code} - {add_res.text}")
                return

        if not facility_id:
            return

        # 2. Get facility by id
        self.client.get(f"/facilities/{facility_id}", headers=self.auth_header_admin, name="/facilities/[id]")

        # 3. Update facility by id
        random_capacity = random.randint(1, 30)
        self.client.patch(f"/facilities/update/{facility_id}",
                          json={"capacity": random_capacity},
                          headers=self.auth_header_admin,
                          name="/facilities/update/[id]")

        # 4. Get facility by name
        if facility_name:
            self.client.get(f"/facilities/name/{facility_name}", headers=self.auth_header_admin, name="/facilities/name/[name]")

        # 5. Get facility by type
        self.client.get(f"/facilities/type/{facility_type}", headers=self.auth_header_admin, name="/facilities/type/[type]")

        # 6. Delete facility by id
        self.client.delete(f"/facilities/delete/{facility_id}", headers=self.auth_header_admin, name="/facilities/delete/[id]")