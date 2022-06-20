from winotify import Notification, audio
#pip install FlightRadarAPI
from FlightRadar24.api import FlightRadar24

# flightradar setup
fr_api = FlightRadar24()


class AirplanesToSee:

    def __init__(self):
        self.flights = []
        self.previous_flights = []
        self.print = []
        self.sunny = False
        self.area_infront_window = {}

        # winotify setup
        self.toast = Notification(app_id="Look out the window!", title="")
        self.toast.set_audio(audio.Reminder, loop=False)

    def set_weather(self):
        self.sunny = int(input("Please Choose your weather.\n======================\n(1) Sunny (0) Cloudy"
                               "\n======================\n"))
        print("======================")

    def list_of_flights_in_area(self):
        if self.sunny:
            self.area_infront_window = {'tl_y': 51.186454, 'tl_x': 6.363371, 'br_y': 51.102381, 'br_x': 6.578291}
        if not self.sunny:
            self.area_infront_window = {'tl_y': 51.186454, 'tl_x': 6.363371, 'br_y': 51.102381, 'br_x': 6.578291}
        bounds_mgl = fr_api.get_bounds(self.area_infront_window)
        self.flights = fr_api.get_flights(bounds=bounds_mgl)
        if not self.sunny:
            for flight in self.flights:
                if flight.altitude >= 9000:
                    self.flights.remove(flight)

    def new_flight_in_area(self) ->bool:
        # Use counter and increment or decrement the counter depending on the event
        if len(self.flights) == len(self.previous_flights):
            self.previous_flights = self.flights
            return False
        elif self.flights != self.previous_flights:
            if len(self.flights) > len(self.previous_flights):
                self.previous_flights = self.flights
                return True
            if len(self.flights) < len(self.previous_flights):
                self.previous_flights = self.flights
                return False

    def print_flights(self):
        TWENTY_MINS_IN_SEC = 1200
        for flight in self.flights:
            details = fr_api.get_flight_details(flight_id=flight.id)
            try:
                flight.set_flight_details(details)
                flightdetail = f"from: {flight.origin_airport_name}, {flight.origin_airport_country_name}\n" \
                               f"to: {flight.destination_airport_name}, {flight.destination_airport_country_name}"
                if flight.altitude > 9000:
                    height = f"high in the air. Altitude: {flight.altitude*0.3} m"
                else:
                    if flight.time + TWENTY_MINS_IN_SEC > flight.time_details['estimated']['arrival']:
                        height = f"landing. Altitude: {flight.altitude*0.3} m"
                    elif flight.time - TWENTY_MINS_IN_SEC > flight.time_details['real']['departure']:
                        height = f"take-off. Altitude: {flight.altitude*0.3} m"
                    else:
                        height = f"could not be defined. Altitude: {flight.altitude*0.3} m"
                print(f"{flightdetail}\n{height}\n======================")
                toast = Notification(
                    app_id="Look out of the Window!",
                    title=f"{flight.number}, {height}",
                    msg=flightdetail,

                )
                toast.add_actions(label="more details",
                                  launch=f"https://www.flightradar24.com/{flight.id}")
                toast.show()
            except:
                print("No details available\n======================")


def main() -> None:
    radar = AirplanesToSee()
    radar.set_weather()
    while True:
        radar.list_of_flights_in_area()
        if radar.new_flight_in_area():
            radar.print_flights()


if __name__ == '__main__':
    main()
