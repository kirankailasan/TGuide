from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SavedTripPlan
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import TouristSpot

from .models import Profile
import json, re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



def save_trip_plan(request):
    if request.method == "POST":
        selected_hotels_json = request.POST.get("selected_hotels", "[]")
        selected_hotels = json.loads(selected_hotels_json)
        trip = SavedTripPlan.objects.create(
            user=request.user,
            location=request.session.get("location", "Unknown"),
            start_date=request.session.get("start_date"),
            end_date=request.session.get("end_date"),
            budget=request.session.get("budget"),
            people=request.session.get("people"),
            preferences=request.session.get("preferences", ""),
            plan_html=request.POST.get("trip_plan", ""),
            selected_hotels=selected_hotels
            
        )
        messages.success(request, "Trip plan saved successfully!")
        return redirect("view_saved_plans", plan_id=trip.id)
    return redirect("trip_result")


@login_required
def view_saved_plans(request, plan_id):
    trip = get_object_or_404(SavedTripPlan, id=plan_id, user=request.user)
    name = TouristSpot.objects.all()


    return render(request, "saved_plans.html", {"plan": trip, "name": name})



@login_required
def view_trip_plans(request):
    name = TouristSpot.objects.all()

    trips = SavedTripPlan.objects.filter(user=request.user).order_by('-saved_at')
    return render(request, "view_trip_plans.html", {"trips": trips, "name": name})


@login_required
def view_trip_plan_detail(request, plan_id):
    # Fetch the trip plan and associated tourist spots
    trip = get_object_or_404(SavedTripPlan, id=plan_id, user=request.user)
    name = TouristSpot.objects.all()

    if request.method == 'POST':  # Ensure it's a POST request
        # Set the 'is_started' field to True
        trip.is_started = True
        trip.save()

        # After updating, redirect to the start_journey page
        return redirect('start_journey', plan_id=trip.id)

    # If GET request, render the trip details page
    return render(request, "view_trip_plan_detail.html", {"trip": trip, "name": name})





@login_required
def delete_trip_plan(request, plan_id):
    plan = get_object_or_404(SavedTripPlan, id=plan_id)

    if plan.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this plan.")

    plan.delete()
    messages.success(request, "Trip plan removed successfully.")
    return redirect("view_trip_plans")


def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {
            'user': request.user,
            'profile': profile
        })

def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'edit_profile.html', {
            'user': request.user,
            'profile': profile
        })


@csrf_exempt
def mark_trip_completed(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        try:
            trip = SavedTripPlan.objects.get(id=plan_id)
            trip.is_completed = True
            trip.save()
            return JsonResponse({'status': 'success'})
        except SavedTripPlan.DoesNotExist:
            return JsonResponse({'status': 'not found'}, status=404)
    return JsonResponse({'status': 'invalid'}, status=400)


@login_required
@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile  # Assuming the profile is linked to the user
        
        # Get form data
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        emergency_contact = request.POST.get('emergency_contact')
        state = request.POST.get('state')
        district = request.POST.get('district')
        bio = request.POST.get('bio')

        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        # Update profile fields
        profile.name = name
        profile.phone_number = mobile
        profile.emergency_contact = emergency_contact
        profile.state = state
        profile.district = district
        profile.bio = bio
        profile.save()

        return JsonResponse({'success': True})


    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from .models import ContactMessage

@csrf_exempt
def contact(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ContactMessage.objects.create(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        return JsonResponse({'status': 'ok'})




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import random
import json
import difflib

# Load QA pairs only (not embeddings)
with open('main/static/json/qa.json', encoding='utf-8') as f:
    QA_PAIRS = json.load(f)

@login_required
def faqs(request):
    questions_and_answers = [(qa_pair['question'], qa_pair['answer']) for qa_pair in QA_PAIRS]
    search_query = request.GET.get('q', '').strip()
    show_all = request.GET.get('all', '') == '1'

    if search_query:
        # Use difflib to find close matches to the search query in questions
        questions = [q for q, a in questions_and_answers]
        close_matches = set(difflib.get_close_matches(search_query, questions, n=6, cutoff=0.3))
        filtered = []
        for question, answer in questions_and_answers:
            if (
                search_query.lower() in question.lower() or
                search_query.lower() in answer.lower() or
                question in close_matches
            ):
                filtered.append((question, answer))
        displayed_questions_and_answers = filtered
    elif show_all:
        displayed_questions_and_answers = questions_and_answers
    else:
        # Show 6 random questions by default
        displayed_questions_and_answers = random.sample(questions_and_answers, min(6, len(questions_and_answers)))

    context = {
        'questions_and_answers': displayed_questions_and_answers,
        'search_query': search_query,
        'show_all': show_all,
    }
    return render(request, 'faqs.html', context)

def info1(request):
    return render(request, 'about/info1.html')

def info2(request):
    return render(request, 'about/info2.html')

def emergency(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'emergency.html',{'profile': profile})


from django.http import JsonResponse
from .models import TouristSpot

def get_tourist_spots_by_district(request, district_name):
    spots = TouristSpot.objects.filter(district__name=district_name)
    data = []

    for spot in spots:
        first_image = spot.image_urls[0] if spot.image_urls else None
        data.append({
            'name': spot.name,
            'first_image': first_image,
        })

    return JsonResponse(data, safe=False)

def load(request):
    return render(request, 'load.html')