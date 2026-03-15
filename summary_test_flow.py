import uuid
import random
from locust import HttpUser, task, between


class ApiMasterUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Získání Admin tokenu pro autorizované operace."""
        self.auth_header_admin = None
        login_payload = {"username": "admin", "password": "admin123"}

        with self.client.post("/auth/login", json=login_payload, name="Admin Login", catch_response=True) as res:
            if res.status_code == 200:
                data = res.json()
                token = data.get("token") or data.get("accessToken") or data.get("jwt")
                if token:
                    self.auth_header_admin = {"Authorization": f"Bearer {token}"}
                    res.success()
                else:
                    res.failure("Token nenalezen")
            else:
                res.failure(f"Admin login failed: {res.status_code}")
                self.interrupt()

    @task
    def master_integration_flow(self):
        if not self.auth_header_admin:
            return

        # --- GENEROVÁNÍ UNIKÁTNÍCH DAT ---
        u_uuid = str(uuid.uuid4())[:8]
        f_uuid = str(uuid.uuid4())[:8]
        username = f"Vaclav_{u_uuid}"
        email = f"{username}@gmail.com"
        facility_name = f"Pitch {f_uuid}"

        # --- 1. USER LIFECYCLE ---
        user_id = None
        reg_payload = {"username": username, "password": "Venca_Password_123", "email": email}

        with self.client.post("/auth/register", json=reg_payload, name="/auth/register", catch_response=True) as res:
            if res.status_code in [200, 201]:
                user_id = res.json().get("id") or res.json().get("userId") or res.json().get("uuid")
                res.success()
            else:
                res.failure("Reg failed")
                return

        self.client.post("/auth/login", json={"username": username, "password": "Venca_Password_123"},
                         name="/auth/login")

        # Admin User Management
        self.client.get(f"/user/{user_id}", headers=self.auth_header_admin, name="/user/[id]")
        self.client.patch(f"/user/update/{user_id}", json={"password": "updatedByAdmin123"},
                          headers=self.auth_header_admin, name="/user/update/[id]")
        self.client.get(f"/user/by-username/{username}", headers=self.auth_header_admin,
                        name="/user/by-username/[name]")
        self.client.get(f"/user/mail/{email}", headers=self.auth_header_admin, name="/user/mail/[mail]")

        # --- 2. FACILITY LIFECYCLE ---
        facility_id = None
        facility_payload = {
            "name": facility_name,
            "type": "FOOTBALL",
            "location": f"Loc {f_uuid}",
            "description": "Large pitch.",
            "contactNumber": f"123{f_uuid}",
            "capacity": 4,
            "imageUrl": "https://example.com/img.jpg",
            "address": f"Street {f_uuid}"
        }

        with self.client.post("/facilities/add", json=facility_payload, headers=self.auth_header_admin,
                              name="/facilities/add", catch_response=True) as res:
            if res.status_code in [200, 201]:
                facility_id = res.json().get("id") or res.json().get("facilityId")
                res.success()
            else:
                res.failure("Facility creation failed")
                return

        self.client.get(f"/facilities/{facility_id}", headers=self.auth_header_admin, name="/facilities/[id]")
        self.client.patch(f"/facilities/update/{facility_id}", json={"capacity": random.randint(1, 30)},
                          headers=self.auth_header_admin, name="/facilities/update/[id]")
        self.client.get(f"/facilities/name/{facility_name}", headers=self.auth_header_admin,
                        name="/facilities/name/[name]")
        self.client.get("/facilities/type/FOOTBALL", headers=self.auth_header_admin, name="/facilities/type/[type]")

        # --- 3. RESERVATION LIFECYCLE (Propojení uživatele a facility) ---
        reservation_id = None
        reservation_payload = {
            "user": {"id": user_id},
            "sportFacility": {"id": facility_id},
            "startTime": "2026-09-23T10:00:00",
            "endTime": "2026-09-23T11:00:00"
        }

        with self.client.post("/reservation/add", json=reservation_payload, headers=self.auth_header_admin,
                              name="/reservation/add", catch_response=True) as res:
            if res.status_code in [200, 201]:
                reservation_id = res.json().get("id") or res.json().get("reservationId")
                res.success()
            else:
                res.failure("Reservation failed")

        if reservation_id:
            self.client.get(f"/reservation/{reservation_id}", headers=self.auth_header_admin, name="/reservation/[id]")
            self.client.patch(f"/reservation/update/{reservation_id}", json={"endTime": "2026-09-23T13:00:00"},
                              headers=self.auth_header_admin, name="/reservation/update/[id]")
            self.client.get(f"/reservation/user/{user_id}", headers=self.auth_header_admin,
                            name="/reservation/user/[id]")
            self.client.get(f"/reservation/facility/{facility_id}", headers=self.auth_header_admin,
                            name="/reservation/facility/[id]")

            # Delete Reservation
            self.client.delete(f"/reservation/delete/{reservation_id}", headers=self.auth_header_admin,
                               name="/reservation/delete/[id]")

        # --- 4. CLEANUP (Smazání facility a uživatele) ---
        if facility_id:
            self.client.delete(f"/facilities/delete/{facility_id}", headers=self.auth_header_admin,
                               name="/facilities/delete/[id]")

        if user_id:
            self.client.delete(f"/user/delete/{user_id}", headers=self.auth_header_admin, name="/user/delete/[id]")