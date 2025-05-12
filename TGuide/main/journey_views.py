import re
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SavedTripPlan, TouristSpot

@login_required
def start_journey(request, plan_id):
    plan = get_object_or_404(SavedTripPlan, id=plan_id, user=request.user)
    day_requested = int(request.GET.get("day", 1))

    pattern = re.compile(r"<h1>Day (\d+) \((.*?)\):</h1>(.*?)(?=(<h1>Day \d+)|\Z)", re.DOTALL)
    day_blocks = pattern.findall(plan.plan_html)

    day_data = []
    for day_num, date_str, content, _ in day_blocks:
        day_data.append({
            "day": int(day_num),
            "date": date_str,
            "html": f"<h1>Day {day_num} ({date_str}):</h1>{content}"
        })

    day_data.sort(key=lambda d: d["day"])
    current_day = next((d for d in day_data if d["day"] == day_requested), None)

    if not current_day:
        return render(request, "start_journey.html", {
            "plan": plan,
            "journey_day_html": "<p>Invalid day selected.</p>",
            "spots_json": "[]",
            "current_day": day_requested,
            "total_days": len(day_data),
        })

    # Extract all spot names from the HTML
    raw_spot_names = re.findall(r'<a href="#" class="tourist-spot" data-name="(.*?)">', current_day["html"])

    # Remove duplicates while keeping order
    spot_names = list(dict.fromkeys(raw_spot_names))

    trip = get_object_or_404(SavedTripPlan, id=plan_id, user=request.user)
    name = TouristSpot.objects.all()
    if not trip.is_started:
        trip.is_started = True
        trip.save()

    return render(request, "start_journey.html", {
        "plan": plan,
        "journey_day_html": current_day["html"],
        "spots_json": json.dumps(spot_names),
        "current_day": current_day["day"],
        "total_days": len(day_data),
        "trip": trip, 
        "name": name,
    })
