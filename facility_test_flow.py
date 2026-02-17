import uuid
from locust import HttpUser, task, between

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






