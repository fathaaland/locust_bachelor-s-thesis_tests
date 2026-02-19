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
    def reservation_test(self):
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
                reg_res.failure(f"Reg failed: {reg_res.status_code}")
                return

        if not user_id:
            return

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

        # 2. Facility creation
        with self.client.post("/facilities/add", json=facility_payload, headers=self.auth_header_admin,
                              name="/facilities/add", catch_response=True) as fac_res:
            if fac_res.status_code in [200, 201]:
                data = fac_res.json()
                facility_id = data.get("id") or data.get("facilityId")
                facility_name = data.get("name") or data.get("facilityName")
                fac_res.success()
            else:
                fac_res.failure(f"Creation failed: {fac_res.status_code} - {fac_res.text}")
                return

        if not facility_id:
            return

        reservation_payload = {
             "user": {f"{user_id}"},
            "sportFacility": {f"{facility_id}"},
            "startTime": "2025-09-23T10:00:00",
            "endTime": "2025-09-23T11:00:00"
        }

        # 3. Reservation creation
        with self.client.post("reservation/add", json=reservation_payload, headers=self.auth_header_admin,
                              name="/reservation/add", catch_response=True) as res_res:
            if res_res.status_code in [200, 201]:
                data = res_res.json()
                reservation_id = data.get("id") or data.get("reservationId")
                reservation_user = data.get("user") or data.get("userId")
                reservation_facility = data.get("facility") or data.get("facilityId")

                res_res.success()
            else:
                res_res.failure(f"Creation failed: {res_res.status_code}")
                return