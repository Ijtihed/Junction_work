from flask import (
    Flask, render_template, request, redirect,
    url_for, session, send_file, jsonify, Response, g
)
from PIL import Image
import requests
import qrcode
import base64
import io
from dotenv import load_dotenv
import os
import os.path
from flask_cors import CORS
import csv

load_dotenv()  # Load .env file
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "default_fallback_key")  # Replace in production
POCKETBASE_URL = os.getenv("POCKETBASE_URL", "http://127.0.0.1:8090")  # Replace in production
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def is_logged_in():
    return "pb_token" in session and "pb_user_id" in session

def get_auth_headers():
    token = session.get("pb_token")
    if not token:
        return {}
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

def add_padding(b64_str):
    missing = len(b64_str) % 4
    if missing:
        b64_str += "=" * (4 - missing)
    return b64_str

########################################
# Error Handlers (use error.html)
########################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html",
                           error_title="404 - Not Found",
                           error_message="We are sorry, that page does not exist."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html",
                           error_title="500 - Server Error",
                           error_message="Oops, something went wrong on our side. Please try again later."), 500

########################################
# Auth Routes
########################################

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        print("Signup route called!")  
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        print(f"Received data - Email: {email}, Password: {password}, Confirm: {password_confirm}")  

        if not email or not password:
            print("Error: Missing email or password")  
            return render_template("signup.html", error="Email and password are required"), 400
        if password != password_confirm:
            print("Error: Passwords do not match")  
            return render_template("signup.html", error="Passwords do not match"), 400
        
        # PocketBase API endpoint and data payload
        url = f"{POCKETBASE_URL}/api/collections/users/records"
        data = {
            "email": email,
            "password": password,
            "passwordConfirm": password_confirm,
            "role": "user"  # Explicitly set the role to "user"
        }
        print(f"Sending data to PocketBase: {data}")  

        try:
            resp = requests.post(url, json=data)
            print(f"PocketBase response: {resp.status_code} - {resp.text}")  
            if resp.status_code in (200, 201):
                print("Signup successful, redirecting to login...")  
                return redirect(url_for("login"))
            else:
                print("Signup failed")  
                return render_template("signup.html",
                                       error=f"Sign-up failed: {resp.text}"), 400
        except Exception as e:
            print(f"Error contacting PocketBase: {e}")  
            return render_template("error.html",
                                   error_title="Error",
                                   error_message=f"Error contacting PocketBase: {e}"), 500

    print("Rendering signup.html for GET request")  
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        auth_url = f"{POCKETBASE_URL}/api/collections/users/auth-with-password"
        data = {"identity": email, "password": password}
        try:
            resp = requests.post(auth_url, json=data)
            if resp.status_code == 200:
                auth_data = resp.json()
                print(f"Auth Data: {auth_data}")  # Debug the response
                
                session["pb_token"] = auth_data["token"]
                session["pb_user_id"] = auth_data["record"]["id"]
                session["pb_user_email"] = auth_data["record"].get("email", "")
                session["pb_user_role"] = auth_data["record"].get("role", "user")  # Fetch the role
                
                print(f"User Role: {session['pb_user_role']}")  # Debug the role
                return redirect(url_for("generate_qr"))
            else:
                print(f"Failed Login: {resp.text}")  # Debug login errors
                return render_template("login.html",
                                       error="Incorrect Password/Email"), 401
        except Exception as e:
            print(f"Error: {e}")  # Debug exceptions
            return render_template("error.html",
                                   error_title="Error",
                                   error_message=f"Error contacting PB: {e}"), 500

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

########################################
# Generate Page
########################################
# Preload logos into memory to avoid repeated disk I/O
def preload_logos():
    if not hasattr(g, "junction_black_logo"):
        g.junction_black_logo = Image.open("static/images/junction_black.png").convert("RGBA")
    if not hasattr(g, "junction_white_logo"):
        g.junction_white_logo = Image.open("static/images/junction_white.png").convert("RGBA")

@app.before_request
def setup():
    preload_logos()

@app.route("/", methods=["GET", "POST"])
def generate_qr():
    if request.method == "POST":
        url_str = request.form.get("url", "").strip()
        if not url_str:
            return render_template("index.html", error="Please provide a valid URL.", qr_url=None, qr_preview=None), 400

        fill_color = request.form.get("fill_color", "#000000")
        back_color = request.form.get("back_color", "#ffffff")
        box_size_str = request.form.get("box_size", "10").strip()
        logo_option = request.form.get("logo_option", "junction_black")
        logo_size_percent = int(request.form.get("logo_size", "25"))
        qr_dimensions = request.form.get("qr_dimensions", "400x400").strip()

        try:
            box_size = int(box_size_str)
        except ValueError:
            box_size = 10
        box_size = max(1, min(15, box_size))

        try:
            width, height = map(int, qr_dimensions.split("x"))
        except ValueError:
            width, height = 400, 400  # Default dimensions

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=4,
        )
        qr.add_data(url_str)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        try:
            # Handle logo options
            logo = None
            if logo_option == "junction_black":
                logo = g.junction_black_logo
            elif logo_option == "junction_white":
                logo = g.junction_white_logo
            elif logo_option == "more":
                logo_file = request.files.get("logo")
                if not logo_file:
                    raise ValueError("Upload logo is required for 'More' option.")
                logo = Image.open(logo_file).convert("RGBA")

            if logo:
                # Calculate logo size based on percentage
                logo_size = (img.size[0] * logo_size_percent // 100, img.size[1] * logo_size_percent // 100)
                logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

                # Calculate position to center the logo
                logo_position = (
                    (img.size[0] - logo.size[0]) // 2,
                    (img.size[1] - logo.size[1]) // 2,
                )

                # Create a copy of the QR code image that supports alpha channel
                qr_rgba = img.convert("RGBA")
                qr_rgba.paste(logo, logo_position, logo)

                # Convert back to RGB for final output
                img = qr_rgba.convert("RGB")

        except Exception as e:
            return render_template(
                "index.html",
                error=f"Error processing logo: {str(e)}",
                qr_url=url_str,
                qr_preview=None,
                last_fill_color=fill_color,
                last_back_color=back_color,
                last_box_size=box_size,
                last_logo_option=logo_option,
            ), 500

        # Resize the QR code image to the specified dimensions
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        qr_b64 = base64.b64encode(img_io.getvalue()).decode()

        # Save to database only if user is logged in
        if is_logged_in():
            headers = get_auth_headers()
            create_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records"
            data = {
                "url": url_str,
                "qr_code": qr_b64,
                "owner": session.get("pb_user_id"),
                "box_size": box_size,
                "fill_color": fill_color,
                "back_color": back_color,
                "logo_size_percent": logo_size_percent,
                "qr_dimensions": qr_dimensions,
            }
            try:
                resp = requests.post(create_url, headers=headers, json=data)
                if resp.status_code not in (200, 201):
                    raise ValueError(f"Failed to save QR code: {resp.text}")
            except Exception as e:
                return render_template(
                    "index.html",
                    error=f"Error contacting server: {str(e)}",
                    qr_url=url_str,
                    qr_preview=qr_b64,
                    last_fill_color=fill_color,
                    last_back_color=back_color,
                    last_box_size=box_size,
                    last_logo_option=logo_option,
                ), 500

        return render_template(
            "index.html",
            qr_url=url_str,
            qr_preview=qr_b64,
            last_fill_color=fill_color,
            last_back_color=back_color,
            last_box_size=box_size,
            last_logo_option=logo_option,
        )

    return render_template("index.html", qr_url=None, qr_preview=None, last_fill_color="#000000", last_back_color="#ffffff", last_box_size=10, last_logo_option="junction_white")

    
########################################
# History Page
########################################

@app.route("/history")
def history():
    if not is_logged_in():
        return redirect(url_for("login"))
    user_id = session["pb_user_id"]
    headers = get_auth_headers()
    list_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records?filter=(owner='{user_id}')&sort=-created"
    try:
        resp = requests.get(list_url, headers=headers)
        if resp.status_code == 200:
            records = resp.json().get("items", [])
            if not records:
                return render_template("history.html", qr_codes=[])
            return render_template("history.html", qr_codes=records)
        else:
            return render_template(
                "index.html",
                error=f"Failed to get QRs: {resp.text}",
                qr_url=session.get("last_url"),
                qr_preview=session.get("last_qr_b64"),
            ), 400
    except Exception as e:
        return render_template(
            "error.html",
            error_title="Error",
            error_message=f"Error contacting PB: {e}",
        ), 500
        
@app.route("/delete_qr_code/<record_id>", methods=["POST"])
def delete_qr_code(record_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    headers = get_auth_headers()
    delete_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records/{record_id}"
    
    try:
        # Attempt to delete the specific QR code record
        resp = requests.delete(delete_url, headers=headers)
        if resp.status_code in (200, 204):
            return redirect(url_for("history"))  # Redirect back to history page after deletion
        else:
            return render_template(
                "history.html",
                error=f"Failed to delete QR code: {resp.text}",
                qr_codes=session.get("last_qr_codes"),
            ), 500
    except Exception as e:
        return render_template(
            "history.html",
            error=f"Error deleting QR code: {e}",
            qr_codes=session.get("last_qr_codes"),
        ), 500


@app.route("/delete_all_qr_codes", methods=["POST"])
def delete_all_qr_codes():
    if not is_logged_in():
        return redirect(url_for("login"))

    user_id = session["pb_user_id"]
    headers = get_auth_headers()

    # Get all QR codes associated with the user
    list_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records?filter=(owner='{user_id}')"
    try:
        resp = requests.get(list_url, headers=headers)
        if resp.status_code == 200:
            records = resp.json().get("items", [])
            if records:
                # Delete each QR code
                for record in records:
                    delete_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records/{record['id']}"
                    delete_resp = requests.delete(delete_url, headers=headers)
                    if delete_resp.status_code not in (200, 204):
                        return render_template(
                            "history.html",
                            error=f"Failed to delete QR code: {delete_resp.text}",
                        ), 500
                return render_template("history.html", success="All QR codes have been deleted from your history.")
            else:
                return render_template("history.html", error="No QR codes found in your history.")
        else:
            return render_template("history.html", error=f"Failed to fetch QR codes: {resp.text}"), 500
    except Exception as e:
        return render_template("history.html", error=f"Error contacting server: {e}"), 500

########################################
# Download
########################################

@app.route("/download/<record_id>")
def download_qr(record_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    headers = get_auth_headers()
    get_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records/{record_id}"
    try:
        resp = requests.get(get_url, headers=headers)
        if resp.status_code == 200:
            record = resp.json()
            qr_b64 = add_padding(record.get("qr_code", ""))
            qr_data = base64.b64decode(qr_b64)
            img_io = io.BytesIO(qr_data)
            img_io.seek(0)
            return send_file(
                img_io, mimetype="image/png",
                as_attachment=True, download_name="qr_code.png"
            )
        else:
            return render_template("error.html",
                                   error_title="Not Found",
                                   error_message="That QR code was not found or you lack permission."), 404
    except Exception as e:
        return render_template("error.html",
                               error_title="Error",
                               error_message=f"Error contacting PB: {e}"), 500

@app.route("/clear_local")
def clear_local():
    session.clear()
    return "Local session cleared! <a href='/login'>Login</a>"

def is_admin():
    return is_logged_in() and session.get("pb_user_role") == "admin"

@app.route("/dashboard")
def dashboard():
    if not is_admin():
        return redirect(url_for("login"))

    headers = get_auth_headers()
    list_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records?sort=-created"

    try:
        resp = requests.get(list_url, headers=headers)
        if resp.status_code == 200:
            qr_codes = resp.json().get("items", [])
            analytics = {
                "total_qr_codes": len(qr_codes),
                "by_owner": {},
                "by_color": {},
                "by_box_size": {},
                "by_logo_option": {}
            }
            for qr in qr_codes:
                owner = qr.get("owner", "Unknown")
                fill_color = qr.get("fill_color", "#000000")
                box_size = qr.get("box_size", "Unknown")
                logo_option = qr.get("logo_option", "Unknown")

                analytics["by_owner"][owner] = analytics["by_owner"].get(owner, 0) + 1
                analytics["by_color"][fill_color] = analytics["by_color"].get(fill_color, 0) + 1
                analytics["by_box_size"][box_size] = analytics["by_box_size"].get(box_size, 0) + 1
                analytics["by_logo_option"][logo_option] = analytics["by_logo_option"].get(logo_option, 0) + 1

            return render_template("dashboard.html", qr_codes=qr_codes, analytics=analytics)
        else:
            error_message = resp.json().get("message", "Unknown error")
            return render_template(
                "error.html",
                error_title="Error",
                error_message=f"Failed to fetch QR codes: {error_message}."
            ), 500
    except Exception as e:
        return render_template("error.html", error_title="Error", error_message=f"Error: {e}"), 500

@app.route("/export_qr_codes")
def export_qr_codes():
    headers = get_auth_headers()
    list_url = f"{POCKETBASE_URL}/api/collections/qrcodes/records"
    try:
        resp = requests.get(list_url, headers=headers)
        if resp.status_code == 200:
            qr_codes = resp.json().get("items", [])
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Owner", "URL", "Fill Color", "Back Color", "Box Size", "Logo Option", "Created", "Updated"])
            for qr in qr_codes:
                writer.writerow([qr["id"], qr["owner"], qr["url"], qr["fill_color"], qr["back_color"], qr["box_size"], qr["logo_option"], qr["created"], qr["updated"]])
            output.seek(0)
            return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=qr_codes.csv"})
        else:
            return "Failed to fetch QR codes", 500
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
