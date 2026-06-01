import random
import math
from django.core.mail import send_mail
from django.shortcuts import render
import pymysql

def getConnection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        database='safety',
        charset='utf8'
    )

# ---------------- HOME ----------------
def index(request):
    return render(request, 'index.html')

# ---------------- LOGIN ----------------
def Login(request):
    return render(request, 'UserLogin.html', {})

from django.shortcuts import render, redirect

def LoginAction(request):

    if request.method == 'POST':
        uname = request.POST.get('t1')
        pwd = request.POST.get('t2')
        login_type = request.POST.get('login_type')

        con = getConnection()
        with con:
            cur = con.cursor()

            # 🚗 DRIVER LOGIN
            if login_type == "driver":
                cur.execute(
                    "SELECT username FROM driver WHERE username=%s AND password=%s",
                    (uname, pwd)
                )
                row = cur.fetchone()

                if row:
                    request.session['username'] = uname
                    request.session['role'] = 'driver'

                    return redirect('/driver_requests/')

            
            elif login_type == "user":
                cur.execute(
                    "SELECT username, email FROM register WHERE username=%s AND password=%s",
                    (uname, pwd)
                )
                row = cur.fetchone()

                if row:
                    request.session['username'] = uname
                    request.session['email'] = row[1]
                    request.session['role'] = 'user'

                    return redirect('/user_screen/')

        return render(request, 'UserLogin.html', {'data': 'Invalid Login'})


# ---------------- SIGNUP ----------------
def Signup(request):
    return render(request, 'Register.html', {})

def SignupAction(request):
    if request.method == 'POST':

        uname = request.POST.get('t1')
        pwd = request.POST.get('t2')
        contact = request.POST.get('t3')
        email_id = request.POST.get('t4')
        address = request.POST.get('t5')
        user_type = request.POST.get('user_type')

        con = getConnection()
        with con:
            cur = con.cursor()

            # DRIVER SIGNUP
            if user_type == "driver":
                vehicle = request.POST.get('t6')

                cur.execute(
                    "INSERT INTO driver VALUES(%s,%s,%s,%s,%s,%s)",
                    (uname, pwd, contact, email_id, address, vehicle)
                )
                con.commit()

                return render(request, 'Register.html', {'data': 'Driver Registered Successfully'})

            # USER SIGNUP
            else:
                cur.execute(
                    "INSERT INTO register VALUES(%s,%s,%s,%s,%s)",
                    (uname, pwd, contact, email_id, address)
                )
                con.commit()

                return render(request, 'Register.html', {'data': 'User Registered Successfully'})

# ---------------- DRIVER LOCATION ----------------
def DriverLocation(request):
    if request.method == 'GET':
        return render(request, 'DriverLocation.html', {})

def DriverScreen(request):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    return render(request, 'DriverScreen.html', {
        'user': username
    })


from django.shortcuts import render, redirect

def DriverLocationAction(request):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    if request.method == 'POST':

        location = request.POST.get('location')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')

        try:
            con = getConnection()

            with con:
                cur = con.cursor()

                cur.execute("""
                    INSERT INTO location(driver, location_name, lat, lon)
                    VALUES(%s,%s,%s,%s)
                """, (username, location, lat, lon))

                con.commit()

            msg = f"✅ {location} saved successfully"

        except Exception as e:
            msg = f"❌ Error: {str(e)}"

        return render(request, 'DriverLocation.html', {'data': msg})


# ---------------- BOOK RIDE ----------------
def ShareLocation(request):
    return render(request, 'ShareLocation.html', {})


def ShareLocationAction(request):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    if request.method == 'POST':

        destination = request.POST.get('destination')

        lat = float(request.POST.get('lat'))
        lon = float(request.POST.get('lon'))

        # STORE SESSION
        request.session['destination'] = destination
        request.session['lat'] = lat
        request.session['lon'] = lon

        con = getConnection()

        with con:
            cur = con.cursor()

            cur.execute("SELECT * FROM location")
            rows = cur.fetchall()

        output = ""

        for row in rows:

            driver_name = row[0]
            driver_location = row[1]

            dlat = float(row[2])
            dlon = float(row[3])

            # DISTANCE CALCULATION
            dist = math.sqrt((lat - dlat) ** 2 + (lon - dlon) ** 2) * 111

            # SHOW DRIVERS WITHIN 50 KM
            if dist <= 50:

                output += f"""
                <div style="
                    background:#fff;
                    padding:15px;
                    border-radius:12px;
                    margin:10px;
                    box-shadow:0 5px 15px rgba(0,0,0,0.2);
                    text-align:center;
                    width:260px;
                ">

                    <h3>🚗 Driver: {driver_name}</h3>

                    <p><b>Location:</b> {driver_location}</p>

                    <p>📍 Distance: {round(dist, 2)} km</p>

                    <p>📌 Destination: {destination}</p>

                    <a href="/send_request/{driver_name}/">
                        <button style="
                            background:#ff4b2b;
                            color:white;
                            border:none;
                            padding:10px 20px;
                            border-radius:8px;
                            cursor:pointer;
                            font-size:16px;
                        ">
                            Request Ride
                        </button>
                    </a>

                </div>
                """

        # NO DRIVERS
        if output == "":

            output = """
            <h3 style='text-align:center;color:red;'>
                ❌ No drivers available nearby
            </h3>
            """

        return render(request, 'ViewDrivers.html', {'data': output})


# ---------------- SEND REQUEST ----------------
def UserScreen(request):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    con = getConnection()

    with con:
        cur = con.cursor()

        cur.execute("""
            SELECT driver, status, fare
            FROM ride
            WHERE user=%s
            ORDER BY id DESC
        """, (username,))

        rides = cur.fetchall()

    return render(request, 'UserScreen.html', {
        'rides': rides,
        'user': username
    })

from django.shortcuts import redirect

def SendRequest(request, driver):

    username = request.session.get('username')

    if not username:
        return render(request, 'UserLogin.html', {'data': 'Please login first'})

    try:
        con = getConnection()
        with con:
            cur = con.cursor()

            # ❌ DO NOT generate OTP here

            cur.execute("""
                INSERT INTO ride(driver,user,status,source_lat,source_lon,destination,fare)
                VALUES(%s,%s,%s,%s,%s,%s,%s)
            """, (
                driver,
                username,
                "requested",
                request.session.get('lat'),
                request.session.get('lon'),
                request.session.get('destination'),
                0
            ))

            con.commit()

        msg = "✅ Ride Requested Successfully"

    except Exception as e:
        msg = f"❌ Error: {str(e)}"

    return render(request, 'UserScreen.html', {
    'data': msg,
    'user': username
})


# ---------------- DRIVER REQUESTS ----------------
def DriverRequests(request):

    username = request.session.get('username')

    if not username:
        return render(request, 'UserLogin.html', {'data': 'Please login first'})

    con = getConnection()
    with con:
        cur = con.cursor()

        cur.execute("""
            SELECT id, user, status
            FROM ride 
            WHERE driver=%s
            ORDER BY id DESC
        """, (username,))

        rides = cur.fetchall()

    return render(request, 'DriverRequests.html', {'rides': rides})


# ---------------- ACCEPT RIDE ----------------
def AcceptRide(request, ride_id):

    username = request.session.get('username')

    con = getConnection()
    with con:
        cur = con.cursor()

        cur.execute("""
            UPDATE ride 
            SET status='accepted' 
            WHERE id=%s AND driver=%s
        """, (ride_id, username))

        con.commit()

    return redirect('/driver_requests/')

# ---------------- START RIDE ----------------
def StartRide(request, ride_id):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    con = getConnection()

    with con:
        cur = con.cursor()

        # GET RIDE DETAILS
        cur.execute("""
            SELECT user, source_lat, source_lon, destination
            FROM ride
            WHERE id=%s
        """, (ride_id,))

        row = cur.fetchone()

        user_name = row[0]
        source_lat = row[1]
        source_lon = row[2]
        destination = row[3]

        # GET USER EMAIL
        cur.execute("""
            SELECT email
            FROM register
            WHERE username=%s
        """, (user_name,))

        email_row = cur.fetchone()
        user_email = email_row[0]

        # GET DRIVER VEHICLE
        cur.execute("""
            SELECT vehicle
            FROM driver
            WHERE username=%s
        """, (username,))

        vehicle_row = cur.fetchone()
        vehicle_no = vehicle_row[0]

        # UPDATE STATUS
        cur.execute("""
            UPDATE ride
            SET status='started'
            WHERE id=%s AND driver=%s
        """, (ride_id, username))

        con.commit()

    # SEND EMAIL
    send_mail(
        "Alert from SafeRide+",
        f"Ride started from Latitude {source_lat} "
        f"Longitude {source_lon} "
        f"for destination {destination} "
        f"Vehicle No = {vehicle_no}",
        "yourgmail@gmail.com",
        [user_email],
        fail_silently=False,
    )

    return redirect('/driver_requests/')


# ---------------- COMPLETE RIDE ----------------
def CompleteRide(request, ride_id):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    con = getConnection()

    with con:
        cur = con.cursor()

        cur.execute("""
            UPDATE ride
            SET status='completed', fare=100
            WHERE id=%s AND driver=%s
        """, (ride_id, username))

        con.commit()

    return redirect('/driver_requests/')


# ---------------- CANCEL RIDE ----------------
def CancelRide(request, ride_id):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    con = getConnection()

    with con:
        cur = con.cursor()

        # UPDATE STATUS
        cur.execute("""
            UPDATE ride
            SET status='cancelled'
            WHERE id=%s AND user=%s
        """, (ride_id, username))

        con.commit()

    return redirect('/past_rides/')


# ---------------- ALERT ----------------
def Panic(request):
    return render(request, 'Panic.html', {})

def PanicAction(request):

    username = request.session.get('username')
    email = request.session.get('email')

    # ✅ LOGIN CHECK
    if not username or not email:
        return redirect('/login/')

    # ✅ CURRENT LOCATION FROM FORM
    location = request.POST.get('location')

    con = getConnection()

    # DEFAULT VALUES
    source_lat = "Not Available"
    source_lon = "Not Available"
    destination = location
    vehicle_no = "Not Available"

    with con:
        cur = con.cursor()

        # ✅ GET LATEST RIDE DETAILS OF USER
        cur.execute("""
            SELECT driver, source_lat, source_lon, destination
            FROM ride
            WHERE user=%s
            ORDER BY id DESC
            LIMIT 1
        """, (username,))

        row = cur.fetchone()

        # ✅ IF RIDE EXISTS
        if row:

            driver_name = row[0]
            source_lat = row[1]
            source_lon = row[2]
            destination = row[3]

            # ✅ GET VEHICLE NUMBER FROM DRIVER TABLE
            cur.execute("""
                SELECT vehicle
                FROM driver
                WHERE username=%s
            """, (driver_name,))

            vehicle_row = cur.fetchone()

            if vehicle_row:
                vehicle_no = vehicle_row[0]

    # ✅ EMAIL MESSAGE
    message = f"""
🚨 EMERGENCY ALERT 🚨

User: {username}

Current Location: {location}

Latitude: {source_lat}

Longitude: {source_lon}

Destination: {destination}

Vehicle No: {vehicle_no}

Please respond immediately.
"""

    # ✅ SEND EMAIL
    send_mail(
        "Emergency Alert from SafeRide+",
        message,
        "yourgmail@gmail.com",
        [email],
        fail_silently=False,
    )

    return render(request, 'Panic.html', {
        'data': '🚨 Emergency Alert Sent Successfully'
    })


# ---------------- PAST RIDES ----------------
def PastRides(request):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    con = getConnection()

    with con:
        cur = con.cursor()

        cur.execute("""
            SELECT id, driver, status, destination, fare
            FROM ride
            WHERE user=%s
            ORDER BY id DESC
        """, (username,))

        rows = cur.fetchall()

    return render(request, 'PastRides.html', {'data': rows})


# ---------------- FEEDBACK ----------------
def Feedback(request, ride_id):

    username = request.session.get('username')

    if not username:
        return redirect('/login/')

    if request.method == 'POST':

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        try:
            con = getConnection()

            with con:
                cur = con.cursor()

                cur.execute("""
                    INSERT INTO feedback (ride_id, rating, comment)
                    VALUES (%s, %s, %s)
                """, (ride_id, rating, comment))

                con.commit()

            # ✅ SUCCESS MESSAGE
            return render(request, 'Feedback.html', {
                'data': '⭐ Ratings accepted! Thank you'
            })

        except Exception as e:

            return render(request, 'Feedback.html', {
                'data': f'Error: {str(e)}'
            })

    return render(request, 'Feedback.html')

from django.shortcuts import redirect

def Logout(request):
    request.session.flush()   # ✅ clear session
    return redirect('/login/')   # go back to login page