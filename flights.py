import requests
from datetime import datetime, timedelta

def get_flights(api_key, departure_id, arrival_id, date, stops=1, max_results=1):
    """
    Fetch the cheapest one-way flight for a specific date.
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": date,
        "stops": stops,
        "type": 2,  #indicates a one way flight
        "api_key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        flights = data.get("other_flights", [])
        if not flights:
            return None
        # sorts flights by price and returns the cheapest one
        sorted_flights = sorted(flights, key=lambda x: x["price"])
        return sorted_flights[:max_results]
    else:
        print(f"Error fetching data for {date}: {response.status_code}")
        print(response.text)
        return None


def find_cheapest_round_trips(api_key, departure_id, arrival_id, start_date, end_date, trip_length, stops=1, top_n=3):

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    cheapest_outbound = {}
    cheapest_round_trips = []

    # cheapest outbound flight
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        outbound_flights = get_flights(api_key, departure_id, arrival_id, date_str, stops)
        if outbound_flights:
            cheapest_outbound[date_str] = outbound_flights[0]  # Only store the cheapest flight
        current_date += timedelta(days=1)

    # match each of the outbound flights with returning flight
    for outbound_date, outbound_flight in cheapest_outbound.items():
        return_date = datetime.strptime(outbound_date, "%Y-%m-%d") + timedelta(days=trip_length)
        if return_date > end_date:
            continue
        return_date_str = return_date.strftime("%Y-%m-%d")
        return_flights = get_flights(api_key, arrival_id, departure_id, return_date_str, stops)
        if return_flights:
            for return_flight in return_flights:
                total_price = outbound_flight["price"] + return_flight["price"]
                cheapest_round_trips.append({
                    "outbound": outbound_flight,
                    "return": return_flight,
                    "total_price": total_price
                })

    # only givens the i cheapest options
    cheapest_round_trips.sort(key=lambda x: x["total_price"])
    for i, trip in enumerate(cheapest_round_trips[:top_n], start=1):
        print(f"Round-Trip {i}:")
        print(f"  Outbound Flight:")
        for leg in trip["outbound"]["flights"]:
            print(f"    From: {leg['departure_airport']['name']} ({leg['departure_airport']['id']})")
            print(f"    To: {leg['arrival_airport']['name']} ({leg['arrival_airport']['id']})")
            print(f"    Departure Time: {leg['departure_airport']['time']}")
            print(f"    Arrival Time: {leg['arrival_airport']['time']}")
        print(f"  Return Flight:")
        for leg in trip["return"]["flights"]:
            print(f"    From: {leg['departure_airport']['name']} ({leg['departure_airport']['id']})")
            print(f"    To: {leg['arrival_airport']['name']} ({leg['arrival_airport']['id']})")
            print(f"    Departure Time: {leg['departure_airport']['time']}")
            print(f"    Arrival Time: {leg['arrival_airport']['time']}")
        print(f"  Combined Price: ${trip['total_price']}")
        print("-" * 30)


# set variables instead of command line args
api_key = "c9146ac820f428992ee77f33da2cf873e208404cdcb5a9729bb2ede8dc8e5444"
departure_id = "LAX"
arrival_id = "JFK"
start_date = "2024-11-28"
end_date = "2024-12-05"
trip_length = 5  
stops = 1

find_cheapest_round_trips(api_key, departure_id, arrival_id, start_date, end_date, trip_length, stops, top_n=3)
