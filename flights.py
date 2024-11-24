import requests


def get_cheapest_flights(api_key, departure_id, arrival_id, max_price, outbound_date, return_date, max_results=3, stops=1):

    url = "https://serpapi.com/search"

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "max_price": max_price,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "stops": stops,
        "api_key": api_key
    }

    # GET request to SerpApi
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        flights = data.get("other_flights", [])

        # sort all potential flights by price
        sorted_flights = sorted(flights, key=lambda x: x["price"])
        cheapest_flights = sorted_flights[:max_results]

        if not cheapest_flights:
            print("No flights found matching the criteria.")
        else:
            for i, flight in enumerate(cheapest_flights, start=1):
                print(f"Flight {i}:")
                for leg in flight["flights"]:
                    print(f"  From: {leg['departure_airport']['name']} ({leg['departure_airport']['id']})")
                    print(f"  To: {leg['arrival_airport']['name']} ({leg['arrival_airport']['id']})")
                    print(f"  Departure Time: {leg['departure_airport']['time']}")
                    print(f"  Arrival Time: {leg['arrival_airport']['time']}")
                print(f"  Price: ${flight['price']}")
                print(f"  Total Duration: {flight['total_duration']} minutes")
                print("-" * 30)
    else:
        print(f"Error: Not able to get flight data. Status code: {response.status_code}")
        print(response.text)


# Example usage
api_key = "c9146ac820f428992ee77f33da2cf873e208404cdcb5a9729bb2ede8dc8e5444"
departure_id = "LAX"
arrival_id = "JFK"
max_price = 1000
outbound_date = "2024-11-25"
return_date = "2024-12-11"
stops = 1

get_cheapest_flights(api_key, departure_id, arrival_id, max_price, outbound_date, return_date, max_results=3, stops=stops)
