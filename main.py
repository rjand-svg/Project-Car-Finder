
"""CS1 Car Finder: place beside car_database_4000.py in Thonny."""

from dataclasses import dataclass
from drafter import *
from car_database_4000 import Car, CARS


@dataclass
class State:
    max_price: int
    minimum_year: int
    maximum_year: int
    country_of_origin: str
    minimum_zero_to_sixty: float
    cars: list[Car]
    matching_cars: list[Car]
    error: str


def new_state() -> State:
    return State(0, 0, 0, "Any", 0.0, CARS.copy(), [], "")


def preferences_page(state: State) -> Page:
    countries = ["Any"] + sorted(set(car.country for car in CARS))

    return Page(state, [
        Header("Find Your Next Car"),

        "Leave a number blank to skip that filter. "
        "Enter a 0-60 time to find cars that are at least that fast.",

        "\nMaximum price ($):",
        TextBox("max_price",
                str(state.max_price) if state.max_price else ""),

        "\nEarliest model year (1950-2026):",
        TextBox("minimum_year",
                str(state.minimum_year) if state.minimum_year else ""),

        "\nLatest model year (1950-2026):",
        TextBox("maximum_year",
                str(state.maximum_year) if state.maximum_year else ""),

        "\nCountry of brand origin:",
        SelectBox("country_of_origin", countries),

        "\nMaximum 0-60 time (seconds):",
        TextBox("minimum_zero_to_sixty",
                str(state.minimum_zero_to_sixty)
                if state.minimum_zero_to_sixty else ""),

        "\n" + state.error,

        Button("Review Preferences", "take_preferences"),
        Button("Home", "index")
    ])


@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Welcome to Car Finder"),

        "Search a database of " + str(len(state.cars)) +
        " car records from 1950 through 2026.",

        Button("Find Cars", "find_cars"),
        Button("How It Works", "how_it_works")
    ])


@route
def find_cars(state: State) -> Page:
    return preferences_page(state)


@route
def take_preferences(state: State, max_price: str,
                     minimum_year: str, maximum_year: str,
                     country_of_origin: str,
                     minimum_zero_to_sixty: str) -> Page:

    # Blank entries mean no preference.
    try:
        price = int(max_price) if max_price.strip() else 0
        first_year = int(minimum_year) if minimum_year.strip() else 0
        last_year = int(maximum_year) if maximum_year.strip() else 0
        speed = (float(minimum_zero_to_sixty)
                 if minimum_zero_to_sixty.strip() else 0.0)

    except ValueError:
        state.error = "Please enter valid numbers in the number fields."
        return preferences_page(state)

    if price < 0 or speed < 0:
        state.error = "Price and 0-60 time cannot be negative."
        return preferences_page(state)

    if ((first_year != 0 and not 1950 <= first_year <= 2026)
            or (last_year != 0 and not 1950 <= last_year <= 2026)):
        state.error = "Years must be between 1950 and 2026."
        return preferences_page(state)

    if first_year and last_year and first_year > last_year:
        state.error = "The earliest year must be before the latest year."
        return preferences_page(state)

    state.max_price = price
    state.minimum_year = first_year
    state.maximum_year = last_year
    state.country_of_origin = country_of_origin
    state.minimum_zero_to_sixty = speed
    state.error = ""

    return verify_preferences(state)


def verify_preferences(state: State) -> Page:
    return Page(state, [
        Header("Verify Your Preferences"),

        "Maximum price: " +
        ("Any" if state.max_price == 0
         else "$" + str(state.max_price)),

        "\nEarliest year: " +
        ("Any" if state.minimum_year == 0
         else str(state.minimum_year)),

        "\nLatest year: " +
        ("Any" if state.maximum_year == 0
         else str(state.maximum_year)),

        "\nCountry: " + state.country_of_origin,

        "\n0-60 time: " +
        ("Any" if state.minimum_zero_to_sixty == 0
         else str(state.minimum_zero_to_sixty) +
         " seconds or faster"),

        "\n",

        Button("Show Matching Cars", "filter_and_show_cars"),
        Button("Change Preferences", "change_preferences"),
        Button("Start Over", "start_over")
    ])


@route
def change_preferences(state: State) -> Page:
    return preferences_page(state)


@route
def filter_and_show_cars(state: State) -> Page:
    matches = []

    # Check every car in the original database.
    for car in state.cars:

        # Check maximum price.
        if state.max_price and car.price > state.max_price:
            continue

        # Check earliest year.
        if state.minimum_year and car.year < state.minimum_year:
            continue

        # Check latest year.
        if state.maximum_year and car.year > state.maximum_year:
            continue

        # Check country of origin.
        if (state.country_of_origin != "Any"
                and car.country != state.country_of_origin):
            continue

        # Check maximum 0-60 acceleration time.
        if (state.minimum_zero_to_sixty
                and car.zero_to_sixty > state.minimum_zero_to_sixty):
            continue

        # If the car passes all filters, save it.
        matches.append(car)

    # Save the matching cars without changing the original list.
    state.matching_cars = matches

    content = [
        Header("Matching Cars"),
        str(len(matches)) + " cars matched your preferences."
    ]

    if len(matches) == 0:
        content.append(
            "\nNo matches found. Try changing your filters."
        )

    else:
        # Display the first 100 matching cars.
        for car in matches[:100]:
            content.append(
                "\n" + str(car.year) + " " +
                car.make_and_model +
                " | $" + format(car.price, ",") +
                " | 0-60: " + str(car.zero_to_sixty) + " s" +
                " | " + car.country
            )

        if len(matches) > 100:
            content.append(
                "\nShowing the first 100 matches of " +
                str(len(matches)) +
                ". Narrow your filters to see more."
            )

    content.append(
        Button("Change Preferences", "change_preferences")
    )
    content.append(
        Button("Start Over", "start_over")
    )

    return Page(state, content)


@route
def how_it_works(state: State) -> Page:
    return Page(state, [
        Header("How Car Finder Works"),

        "Choose your budget, model-year range, "
        "country of brand origin, and preferred 0-60 time.",

        "\nThe program checks each car and displays "
        "those meeting every chosen filter.",

        "\nPrices and performance figures are estimates "
        "for a class project, not verified listings.",

        Button("Home", "index"),
        Button("Find Cars", "find_cars")
    ])


@route
def start_over(state: State) -> Page:
    return index(new_state())


if __name__ == "__main__":
    start_server(new_state())

