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
        reg_payload = {"username": username, "password": "Venca321", "email": f"{username}@gmail.com"}

        # 1. User registration
        user_id = None
        with self.client.post("/auth/register", json=reg_payload, name="/auth/register",
                              catch_response=True) as reg_res:
            if reg_res.status_code in [200, 201]:
                user_id = reg_res.json().get("id") or reg_res.json().get("userId")
                reg_res.success()
            else:
                reg_res.failure(f"Reg failed: {reg_res.status_code}")
                return

        # 2. Facility creation
        f_uuid = str(uuid.uuid4())[:8]
        facility_payload = {
            "name": f"Pitch {f_uuid}",
            "type": "FOOTBALL",
            "location": f"Little Italy {f_uuid}",
            "description": "Large pitch.",
            "contactNumber": f"123{f_uuid}",
            "capacity": 4,
            "imageUrl": "https://example.com/images/pitch.jpg",
            "address": f"Street {f_uuid}"
        }

        facility_id = None
        with self.client.post("/facilities/add", json=facility_payload, headers=self.auth_header_admin,
                              name="/facilities/add", catch_response=True) as fac_res:
            if fac_res.status_code in [200, 201]:
                facility_id = fac_res.json().get("id") or fac_res.json().get("facilityId")
                fac_res.success()
            else:
                fac_res.failure(f"Creation failed: {fac_res.status_code}")
                return

        # 3. Reservation creation (OPRAVENO: Lomítko a Payload)
        reservation_payload = {
            "user": {"id": user_id},
            "sportFacility": {"id": facility_id},
            "startTime": "2025-09-23T10:00:00",
            "endTime": "2025-09-23T11:00:00"
        }

        reservation_id = None
        with self.client.post("/reservation/add", json=reservation_payload, headers=self.auth_header_admin,
                              name="/reservation/add", catch_response=True) as res_res:
            if res_res.status_code in [200, 201]:
                data = res_res.json()
                reservation_id = data.get("id") or data.get("reservationId")
                res_res.success()
            else:
                res_res.failure(f"Reservation creation failed: {res_res.status_code}")
                return

        # --- DALŠÍ KROKY UŽ JSOU MIMO WITH BLOK (Správné odsazení) ---

        # 4. Get reservation by id
        self.client.get(f"/reservation/{reservation_id}", headers=self.auth_header_admin, name="/reservation/[id]")

        # 5. Update reservation (Opraveno: reservation_id místo facility_id)
        updated_payload = {"endTime": "2025-09-23T13:00:00"}
        self.client.patch(f"/reservation/update/{reservation_id}", json=updated_payload,
                          headers=self.auth_header_admin, name="/reservation/update/[id]")

        # 6. Get by User a Facility (Používáme ID, která už máme z předchozích kroků)
        self.client.get(f"/reservation/user/{user_id}", headers=self.auth_header_admin, name="/reservation/user/[id]")
        self.client.get(f"/reservation/facility/{facility_id}", headers=self.auth_header_admin,
                        name="/reservation/facility/[id]")

        # 7. Delete reservation
        with self.client.delete(f"/reservation/delete/{reservation_id}", headers=self.auth_header_admin,
                                name="/reservation/delete/[id]", catch_response=True) as del_res:
            if del_res.status_code in [200, 204]:
                del_res.success()
            else:
                del_res.failure(f"Delete failed: {del_res.status_code}")