import sys
import json
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "http://localhost:8000/api/v1"

# ANSI Terminal Colors & Formatting
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print("=" * 80)


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def make_request(method: str, endpoint: str, data: dict = None, headers: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    body = json.dumps(data).encode("utf-8") if data is not None else None

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method.upper())

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        error_content = e.read().decode("utf-8")
        try:
            parsed_err = json.loads(error_content)
            print(f"\033[91mHTTP Error {e.code}: {json.dumps(parsed_err, indent=2)}\033[0m")
            return parsed_err
        except Exception:
            print(f"\033[91mHTTP Error {e.code}: {error_content}\033[0m")
            sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\033[91mFailed to connect to backend server at {BASE_URL}. Please verify FastAPI server is running.\nError: {e}\033[0m")
        sys.exit(1)


def wait_for_user(next_step_title: str):
    input(f"\n{BOLD}{YELLOW}---> Press [Enter] to execute {next_step_title}...{RESET}")


def main():
    print_header("Hindsight Experiential AI Memory Interactive Demo")
    print(f"Connecting to Kirana AI Backend API at: {BASE_URL}")

    # 0. Login as Owner
    print(f"\n{BOLD}Logging in as owner@sharmastore.com...{RESET}")
    login_res = make_request("POST", "/auth/login", {
        "email": "owner@sharmastore.com",
        "password": "ChangeMe123!"
    })

    if not login_res.get("success") or "data" not in login_res:
        print(f"\033[91mLogin failed! Please ensure the backend is running and seeded.\033[0m")
        sys.exit(1)

    token_data = login_res["data"]
    access_token = token_data["access_token"]
    shop_id = token_data["shop_id"]
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Shop-Id": shop_id
    }
    print(f"{GREEN}Login successful! Token acquired for shop ID: {shop_id}{RESET}")

    # -------------------------------------------------------------------------
    # STEP 1
    # -------------------------------------------------------------------------
    wait_for_user("Step 1")
    print_header('1. POST /assistant/chat "Maggi kitna order karun?"')
    step1_res = make_request("POST", "/assistant/chat", {
        "message": "Maggi kitna order karun?"
    }, headers=auth_headers)
    print_json(step1_res)

    # -------------------------------------------------------------------------
    # STEP 2
    # -------------------------------------------------------------------------
    wait_for_user("Step 2")
    print_header("2. GET /memory/recall?query=maggi")
    step2_res = make_request("GET", "/memory/recall?query=maggi", headers=auth_headers)
    print_json(step2_res)

    # -------------------------------------------------------------------------
    # STEP 3
    # -------------------------------------------------------------------------
    wait_for_user("Step 3")
    print_header('3. POST /assistant/chat "Main Maggi ek baar mein 35 se zyada order nahi karta hu, storage kam hai"')
    step3_res = make_request("POST", "/assistant/chat", {
        "message": "Main Maggi ek baar mein 35 se zyada order nahi karta hu, storage kam hai"
    }, headers=auth_headers)
    print_json(step3_res)

    # -------------------------------------------------------------------------
    # STEP 4
    # -------------------------------------------------------------------------
    wait_for_user("Step 4")
    print_header("4. GET /memory/recall?query=maggi")
    step4_res = make_request("GET", "/memory/recall?query=maggi", headers=auth_headers)
    print_json(step4_res)

    # -------------------------------------------------------------------------
    # STEP 5
    # -------------------------------------------------------------------------
    wait_for_user("Step 5")
    print_header('5. POST /assistant/chat "Maggi kitna order karun?" again')
    step5_res = make_request("POST", "/assistant/chat", {
        "message": "Maggi kitna order karun?"
    }, headers=auth_headers)
    print_json(step5_res)

    # -------------------------------------------------------------------------
    # STEP 6
    # -------------------------------------------------------------------------
    wait_for_user("Step 6")
    print_header('6. POST Decision on seeded Maggi recommendation (REJECTED)')

    # Query recommendations list to locate seeded Maggi recommendation ID
    recs_res = make_request("GET", "/recommendations", headers=auth_headers)
    recs_list = recs_res.get("data", [])

    maggi_rec_id = None
    for rec in recs_list:
        if "maggi" in rec.get("title", "").lower() or "maggi" in rec.get("recommendation", "").lower():
            maggi_rec_id = rec["id"]
            break

    if not maggi_rec_id and recs_list:
        maggi_rec_id = recs_list[0]["id"]

    if not maggi_rec_id:
        print(f"\033[91mNo recommendation found to decide upon.\033[0m")
    else:
        print(f"Submitting decision for Recommendation ID: {maggi_rec_id}")
        step6_res = make_request("POST", f"/recommendations/{maggi_rec_id}/decision", {
            "decision": "REJECTED",
            "decision_notes": "Too much for my storeroom, ordered 25 instead"
        }, headers=auth_headers)
        print_json(step6_res)

    # -------------------------------------------------------------------------
    # STEP 7
    # -------------------------------------------------------------------------
    wait_for_user("Step 7")
    print_header("7. GET /memory/recall?query=Maggi restock")
    query_encoded = urllib.parse.quote("Maggi restock")
    step7_res = make_request("GET", f"/memory/recall?query={query_encoded}", headers=auth_headers)
    print_json(step7_res)

    print_header("Hindsight Interactive Demo Completed Successfully!")


if __name__ == "__main__":
    main()
