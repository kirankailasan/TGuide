from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, PlanTripForm
from .models import PlanTrip, TouristSpot, City, District, Hotel, SavedTripPlan
from django.contrib.auth.forms import AuthenticationForm
from openai import OpenAI
from django.http import JsonResponse, HttpResponse
import requests, folium
from django.http import JsonResponse
from rapidfuzz import process
from django.views.decorators.csrf import csrf_exempt
import json, re, time 
from django.conf import settings
import openai, random
from django.urls import reverse


from datetime import datetime, timedelta
from django.utils.dateparse import parse_date

# Initialize OpenAI client
def get_openai_client(api_key):
    """Returns an OpenAI client with a given API key."""
    return openai.OpenAI(api_key=api_key)



def home(request):
    user_form = UserRegistrationForm(request.POST)
    spots = TouristSpot.objects.filter(
        normalized_name__in=['munnar', 'shanghumukham beach', 'alappuzha beach', 'malampuzha dam and garden']
    )
    # Convert spots queryset to a list of dicts
    spots_json = json.dumps(list(spots.values('name', 'normalized_name', 'image_urls')))

    trips = SavedTripPlan.objects.filter(is_started=True, is_completed=False).exclude(id__isnull=True)
    return render(request, 'home.html', {
        "trips": trips,
        'user_form': user_form,
        'spots': spots,
        'spots_json': spots_json
    })

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.email = user_form.cleaned_data['email'].lower()
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')

            # Set cookie and return the response
            response = redirect('home')
            response.set_cookie('user_created', 'True')
            return response  # <-- return the response with cookie

    else:
        user_form = UserRegistrationForm()

    # Render home.html so the popup works
    return render(request, 'home.html', {'user_form': user_form})

    
from django.core.mail import send_mail
from django.contrib.auth.models import User

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"success": False, "error": "Email required."})
        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({"success": False, "error": "Email address is already in use."})
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['email'] = email.lower()
        send_mail(
            'Your OTP for Registration',
            f'Your OTP is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request."})

@csrf_exempt
def verify_otp_ajax(request):
    if request.method == "POST":
        data = json.loads(request.body)
        input_otp = data.get("otp")
        session_otp = request.session.get("otp")
        if input_otp == session_otp:
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Invalid OTP."})
    return JsonResponse({"success": False, "error": "Invalid request."})

def dashboard(request):
    name = TouristSpot.objects.all()
    trips = SavedTripPlan.objects.filter(is_started=True, is_completed=False).exclude(id__isnull=True)
    return render(request, 'dashboard.html', {"name": name, "trips": trips})

def search_place(request):
    query = request.GET.get("query", "").strip().lower()

    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    # Fetch all names of tourist spots, districts, and cities
    tourist_spots = list(TouristSpot.objects.values_list("name", flat=True))
    districts = list(District.objects.values_list("name", flat=True))
    cities = list(City.objects.values_list("name", flat=True))
    all_places = tourist_spots + districts + cities

    # Find best matches using fuzzy search (limit to 5 results)
    matches = process.extract(query, all_places, limit=5, score_cutoff=50)

    # Ensure unique results in related places
    matched_places = {match[0] for match in matches}  # Extract place names from fuzzy matches
    related_places = [
        {"name": place} for place in all_places if query in place.lower() and place not in matched_places
    ][:5]  # Limit related places

    # Fetch details for the best-matched place
    selected_place = None
    if matches:
        best_match = matches[0][0]

        selected_place = TouristSpot.objects.filter(name=best_match).values(
            "name", "latitude", "longitude", "description", "address", "image_urls", "entrance_fee", "opening_hours"
        ).first() or District.objects.filter(name=best_match).values(
            "name", "description", "latitude", "longitude", "image_urls"
        ).first() or City.objects.filter(name=best_match).values(
            "name", "description", "latitude", "longitude", "image_urls"
        ).first()

    return JsonResponse({
        "suggestions": [{"name": match[0]} for match in matches],
        "related_places": related_places,
        "selected_place": selected_place
    })


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TouristSpot  # Assuming TouristSpot model is in the same app
import openai


from datetime import datetime


def call_openai(prompt):
    """Function to call OpenAI API with fallback mechanism."""
    api_keys = settings.OPENAI_API_KEY 
    random.shuffle(api_keys) # List of API keys
    key_index = 0

    while key_index < len(api_keys):
        try:
            client = get_openai_client(api_keys[key_index])
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an expert AI trip planner specializing in Kerala travel. You create structured itineraries using only the provided tourist spots."},
                          {"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()  # Return generated trip plan

        except openai.RateLimitError:
            print(f"Rate limit exceeded for API Key {key_index + 1}. Switching to next key...")
            key_index += 1
            if key_index < len(api_keys):
               time.sleep(2)

        except openai.OpenAIError as e:
            print(f"OpenAI API error with Key {key_index + 1}: {str(e)}")
            key_index += 1
        
        except Exception as e:
            print(f"unexpected error with key {key_index + 1}: {str(e)}")
            key_index += 1

    return None  # Fallback if no response

def count_days(trip_plan):
    """Count the number of days in a trip plan using regex."""
    return len(re.findall(r"<h1>Day (\d+):", trip_plan))


def calculate_days(start_date, end_date):
    """Calculate the number of days between start_date and end_date (inclusive)."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days + 1
    except ValueError:

        
        return None  # Return None if date format is incorrect
    


def get_tourist_spots_for_location(location):
    selected_spot = TouristSpot.objects.filter(name=location).first()
    selected_city = City.objects.filter(name = location).first()
    selected_district = District.objects.filter(name= location).first()

    if selected_spot:  # If a tourist spot is selected
        district = selected_spot.district
        spots = list(TouristSpot.objects.filter(district=district).values_list("name", flat=True))
        spots.remove(selected_spot.name)  # Ensure selected spot comes first
        return [selected_spot.name] + spots  # Prioritize selected spot

    elif selected_city:  # If a city is selected, find its district
        district = selected_city.district
        return list(TouristSpot.objects.filter(district=district).values_list("name", flat=True))

    elif selected_district:  # If a district is selected
        return list(TouristSpot.objects.filter(district=selected_district).values_list("name", flat=True))
    
        

    return []  # No valid locations found
    
    

def extract_tourist_spots(response_text):
    spot_pattern = re.findall(r"<a>(.*?)</a>", response_text)
    return set(spot_pattern)

@csrf_exempt
def plan_trip(request):
    if request.method == "POST":
        try:
            # Accept both JSON and form POST
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            # Parse multi_locations and AI suggestion flag
            multi_locations_raw = data.get("multi_locations")
            if multi_locations_raw:
                try:
                    multi_locations = json.loads(multi_locations_raw) if isinstance(multi_locations_raw, str) else multi_locations_raw
                except Exception:
                    multi_locations = []
            else:
                multi_locations = []

            allow_ai_suggestions = data.get("allow_ai_suggestions", "false") == "true"

            start_date = data.get("start_date")
            end_date = data.get("end_date")
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            budget = data.get("budget")
            people = data.get("people")
            preferences = data.get("preferences")

            # Validate required fields
            if not start_date or not end_date or not start_time or not end_time:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # --- Build the list of spots to use ---
            selected_spots = []
            ai_area_notes = []  # For AI prompt
            trip_area = ""
            if multi_locations:
                trip_area = ", ".join(multi_locations)
                for loc in multi_locations:
                    # Check if it's a tourist spot
                    spot = TouristSpot.objects.filter(name__iexact=loc).first()
                    if spot:
                        selected_spots.append(spot.name)
                        if allow_ai_suggestions:
                            ai_area_notes.append(
                                f"Add more tourist spots from the district of {spot.name} ({spot.district.name}) if suitable."
                            )
                        continue

                    # Check if it's a city
                    city = City.objects.filter(name__iexact=loc).first()
                    if city:
                        city_spots = list(TouristSpot.objects.filter(district=city.district).values_list("name", flat=True))
                        if not allow_ai_suggestions:
                            selected_spots.extend(city_spots)
                        else:
                            ai_area_notes.append(
                                f"Add suitable tourist spots from the city {city.name} and its district ({city.district.name})."
                            )
                        continue

                    # Check if it's a district
                    district = District.objects.filter(name__iexact=loc).first()
                    if district:
                        district_spots = list(TouristSpot.objects.filter(district=district).values_list("name", flat=True))
                        if not allow_ai_suggestions:
                            selected_spots.extend(district_spots)
                        else:
                            ai_area_notes.append(
                                f"Add suitable tourist spots from the district {district.name}."
                            )
                        continue

                # Remove duplicates, preserve order
                selected_spots = list(dict.fromkeys(selected_spots))

                if not selected_spots and not ai_area_notes:
                    return JsonResponse({"error": "No valid tourist spots, cities, or districts found."}, status=400)

                # Compose AI prompt
                ai_note = ""
                if allow_ai_suggestions and ai_area_notes:
                    ai_note = "\n".join(ai_area_notes)
                else:
                    ai_note = "Strictly use only the selected spots. Do not add any other places."

            else:
                # Fallback to single location
                location = data.get("location")
                if not location:
                    return JsonResponse({"error": "Missing required fields"}, status=400)
                selected_spots = get_tourist_spots_for_location(location)
                trip_area = location
                ai_note = "Strictly use only the selected spots. Do not add any other places."

            total_days = calculate_days(start_date, end_date)
            if total_days is None or total_days <= 0:
                return JsonResponse({"error": "Invalid date range"}, status=400)

            max_days_per_prompt = 5
            full_trip_plan = []
            used_spots = set()

            # --- Build the AI prompt ---
            first_prompt = f"""
You are an expert AI trip planner specializing in Kerala travel.
Create a **structured and detailed** trip plan for {people} people to **{trip_area}** within a budget of **{budget} INR** from **{start_date}** (arriving at **{start_time}**) to **{end_date}** (leaving at **{end_time}**).

**Preferences:** {preferences if preferences else "General sightseeing"}.

**Only use these tourist spots**: {', '.join(selected_spots)}
{ai_note}

### **Strict Itinerary Format (Use HTML Tags Properly)**
Provide trip plan for **only the first {min(total_days, max_days_per_prompt)} days**.

<h1>Day X (DD-MM-YYYY):</h1>:
<ul>
    <li>🌅 Morning:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>🍽️ **Lunch:** Restaurant name, approx cost</li>
    <li>☀️ Afternoon:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>🌙 Evening:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>💰 **Estimated Cost:** Entry fees, food, transport, total</li>
</ul>
"""

            first_part = call_openai(first_prompt)
            if not first_part:
                return JsonResponse({'error': 'Failed to generate trip plan from API'}, status=500)
            used_spots.update(extract_tourist_spots(first_part))
            full_trip_plan.append(first_part)

            # Handle remaining days
            if total_days > max_days_per_prompt:
                current_start_day = max_days_per_prompt + 1

                while current_start_day <= total_days:
                    remaining_days = min(max_days_per_prompt, total_days - current_start_day + 1)

                    new_start_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=current_start_day - 1)).strftime("%Y-%m-%d")
                    new_end_date = (datetime.strptime(new_start_date, "%Y-%m-%d") + timedelta(days=remaining_days - 1)).strftime("%Y-%m-%d")

                    available_spots = set(selected_spots) - used_spots
                    if not available_spots:
                        return JsonResponse({'error': 'No new tourist spots available'}, status=400)

                    next_prompt = f"""
Continue generating the trip plan for **Day {current_start_day} to Day {current_start_day + remaining_days - 1}**.
This is the continuation of the trip plan from **{start_date}** to **{end_date}**.

- The user **arrives at {start_time}** on **{start_date}** and **leaves at {end_time}** on **{end_date}**.
- This part covers the trip from **{new_start_date} to {new_end_date}**.
- Use the **same structured format** as the previous parts.
- Ensure **correct date calculation** for each day.
- **Only use these available tourist spots**: {', '.join(available_spots)}

### **Strict Itinerary Format (Use HTML Tags Properly)**
Strictly plan a trip to **{trip_area}** only.

<h1>Day X (DD-MM-YYYY):</h1>:
<ul>
    <li>🌅 Morning:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>🍽️ **Lunch:** Restaurant name, approx cost</li>
    <li>☀️ Afternoon:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>🌙 Evening:
        <ul>
            <li>
                <a>Spot Name</a> <a>Time to enter and leave</a><br>
                <a>Description (Include highlights of the spot)</a><br>
                <a>Cost</a><br>
                <a>Transportation (Specify mode and estimated time)</a>
            </li>
            **add other spots if there is time
        </ul>
    </li>
    <li>💰 **Estimated Cost:** Entry fees, food, transport, total</li>
</ul>

### **Additional Rules**
--On **the last day**, ensure activities **end before {end_time}**.
"""

                    next_part = call_openai(next_prompt)
                    if not next_part:
                        return JsonResponse({'error': 'Failed generating additional days'}, status=500)

                    used_spots.update(extract_tourist_spots(next_part))
                    full_trip_plan.append(next_part)
                    current_start_day += remaining_days

            final_trip_plan = "\n".join(full_trip_plan)

            # Save to session
            request.session["trip_plan"] = final_trip_plan
            request.session["location"] = trip_area
            request.session["start_date"] = start_date
            request.session["end_date"] = end_date
            request.session["budget"] = budget
            request.session["people"] = people
            request.session["preferences"] = preferences

            return JsonResponse({"redirect_url": "/trip_result/"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "plan_trip.html")






def trip_result(request):
    
    trip_plan = request.session.get("trip_plan", "No trip plan available.")
    print(trip_plan)
    location = request.session.get("location", "Unknown location")
    start_date = request.session.get("start_date", "N/A")
    end_date = request.session.get("end_date", "N/A")
    budget = request.session.get("budget", "N/A")
    people = request.session.get("people", "N/A")
    preferences = request.session.get("preferences", "N/A")
    
    

    tourist_spots = list(TouristSpot.objects.values_list('name', flat=True))
    name = TouristSpot.objects.all()

    for spot in tourist_spots:
        trip_plan = re.sub(
            fr'\b{re.escape(spot)}\b',
            f'<a href="#" class="tourist-spot" data-name="{spot}">{spot}</a>',
            trip_plan
        )

    
    

    return render(request, "trip_result.html", {
        "trip_plan": trip_plan,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "people": people,
        "preferences": preferences,
        "name": name,
        
        
    })

def get_place_details(request):
    name = request.GET.get("name")
    if not name:
        return JsonResponse({"error": "No place name provided"}, status=400)

    spot = TouristSpot.objects.filter(name=name).values(
        "name", "description", "address", "entrance_fee", "opening_hours", "image_urls"
    ).first()

    if spot:
        return JsonResponse({
            "name": spot["name"],
            "description": spot["description"],
            "address": spot["address"],
            "entrance_fee": spot["entrance_fee"],
            "opening_hours": spot["opening_hours"],
            "image_urls": spot["image_urls"] if spot["image_urls"] else [],  # Show first image
        })
    else:
        return JsonResponse({"error": "Place not found"}, status=404)


def get_spots_details(request):
    spots_param = request.GET.get("spots")
    if not spots_param:
        return JsonResponse({"error": "No spots provided"}, status=400)

    try:
        spots_list = json.loads(spots_param)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    spots_data = []
    for spot_name in spots_list:
        spot = TouristSpot.objects.filter(name__iexact=spot_name).first()
        if spot:
            spots_data.append({
                "name": spot.name,
                "latitude": spot.latitude,
                "longitude": spot.longitude,
            })

    if not spots_data:
        return JsonResponse({"error": "No valid spots found"}, status=404)

    return JsonResponse({"spots": spots_data})

def get_openai_client1():   
    api_key = random.choice(settings.OPENAI_API_KEY1)  # Select a key randomly
    return openai.OpenAI(api_key=api_key)


def fetch_hotels(request):
    location = request.session.get("location", None)
    # Find the district based on location
    selected_spot = TouristSpot.objects.filter(name=location).first()
    selected_city = City.objects.filter(name=location).first()
    selected_district = District.objects.filter(name=location).first()

    district = None

    if selected_spot:
        district = selected_spot.district
    elif selected_city:
        district = selected_city.district
    elif selected_district:
        district = selected_district

    if not district:
        return JsonResponse({"error": "No district found for this location."}, status=404)

    # Fetch hotels from the found district
    hotels = Hotel.objects.filter(district=district)

    if not hotels.exists():
        return JsonResponse({"error": "No hotels found in this district."}, status=404)

    # Serialize hotel data
    hotel_list = []
    for hotel in hotels:
        hotel_list.append({
            "name": hotel.name,
            "price": hotel.price,
            "amenities": hotel.amenities,
            "image_url": hotel.image_url if hotel.image_url else None,
        })

    return JsonResponse(hotel_list, safe=False)




def get_openai_client_chatbot_v2(api_key):
    return openai.OpenAI(api_key=api_key)

from .qa_loader import find_similar_answer


@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip().lower()

            if not message:
                return JsonResponse({'response': "Please enter a message."})

            # Initialize conversation history
            if 'conversation_history_v2' not in request.session:
                request.session['conversation_history_v2'] = [
                    {"role": "system", "content": "You are a helpful Kerala travel assistant. Respond like a normal human in a short, natural, and complete way. Keep replies within 200 tokens. Avoid long lists or detailed breakdowns unless asked explicitly."}
                ]

            request.session['conversation_history_v2'].append({"role": "user", "content": message})

            # Detect intent to offer button
            if re.search(r'\b(plan|create|make)\b.*\btrip\b', message):
                plan_url = request.build_absolute_uri(reverse('plan_trip'))  # full URL
                user=request.user
                if user.is_authenticated:
                    button_html = f'''
                        Sure! You can click the button below to plan your trip:
                        <br><br>
                        <a href="{plan_url}" class="btn btn-primary" 
                        style="padding: 5px 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 9px;">
                            🧭 Plan Your Trip
                        </a>
                        <br><br>
                    '''
                else:
                    button_html = f'''
                        You haven't logged in, so please login to continue:
                        <br><br>
                        <a href="#" onclick="document.getElementById('navbarLogin').click(); return false;" class="btn btn-primary" 
                        style="padding: 5px 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 9px;">
                            Login to Create your Plan
                        </a>
                        <br><br>
                    '''
                return JsonResponse({'response': button_html, 'is_button': True})

            similar_answer = find_similar_answer(message)
            if similar_answer:  # Only return if a valid answer is found
                return JsonResponse({'response': similar_answer, 'is_button': False})

            # Fallback to OpenAI if no similar answer
            client = get_openai_client_chatbot_v2(settings.OPENAI_API_KEY_0)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=request.session['conversation_history_v2'],
                max_tokens=200,
                temperature=0.7
            )

            bot_response = response.choices[0].message.content.strip()
            request.session['conversation_history_v2'].append({"role": "assistant", "content": bot_response})
            request.session.modified = True

            return JsonResponse({'response': bot_response, 'is_button': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except openai.OpenAIError as e:
            return JsonResponse({'error': f"OpenAI API Error: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({'error': f"Unexpected Error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)




BOT_INFO = """
You are a travel assistant bot provided travelling assistance for travelling in Kerala. 
"""



def get_bot_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({'response': "Please enter a message."})

            # Initialize conversation history if not in session
            if 'conversation_history' not in request.session:
                request.session['conversation_history'] = [
                    {"role": "system", "content": f"You are a helpful AI assistant. {BOT_INFO}"}
                ]

            # Append user message to conversation history
            request.session['conversation_history'].append({"role": "user", "content": message})

            # Get an OpenAI client (Make sure you have implemented `get_openai_client`)
            client = get_openai_client(settings.OPENAI_API_KEY_1)

            # Make OpenAI API request
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=request.session['conversation_history'],
                max_tokens=100
            )

            bot_response = response.choices[0].message.content.strip()

            # Append bot response to conversation history
            request.session['conversation_history'].append({"role": "assistant", "content": bot_response})
            request.session.modified = True  # ✅ Ensure session updates

            return JsonResponse({'response': bot_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except openai.OpenAIError as e:
            return JsonResponse({'error': f"OpenAI API Error: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({'error': f"Unexpected Error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)






def test(request):
    return render(request, 'test.html')

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').lower()
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': 'dashboard'})  # Redirect to homepage after successful login
        else:
            return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})