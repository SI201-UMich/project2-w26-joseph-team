# SI 201 HW4 (Library Checkout System)
# Your name: Joseph
# Your student id: 64220721
# Your email: jjpeng@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): chatgpt
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    results = []
    seen_ids = set()
 
    # Each listing card has a div with data-testid="listing-card-title"
    # and a nearby <a> with href containing /rooms/<id>
    for card in soup.find_all("div", attrs={"data-testid": "card-container"}):
        # Get the title
        title_tag = card.find("div", attrs={"data-testid": "listing-card-title"})
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
 
        # Get the listing ID from the anchor href
        link = card.find("a", href=re.compile(r"/rooms/"))
        if not link:
            continue
        href = link.get("href", "")
        match = re.search(r"/rooms/(?:plus/)?(\d+)", href)
        if not match:
            continue
        listing_id = match.group(1)
 
        if listing_id not in seen_ids:
            seen_ids.add(listing_id)
            results.append((title, listing_id))
 
    return results


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    path = os.path.join("html_files", f"listing_{listing_id}.html")
    with open(path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 1. Policy Number
    policy = "Exempt"
    policy_section = soup.find(string=re.compile(r"Policy number", re.I))
    if policy_section:
        parent = policy_section.find_parent("li")
        raw_val = parent.get_text().split(":")[-1].strip() if parent else ""
        if "pending" in raw_val.lower(): policy = "Pending"
        elif "exempt" in raw_val.lower(): policy = "Exempt"
        else: policy = raw_val

    # 2. Host Type
    host_type = "Superhost" if soup.find(string=re.compile(r"Superhost", re.I)) else "regular"

    # 3. Host Name
    host_name = ""
    host_tag = soup.find("h2", string=re.compile(r"hosted by", re.I))
    if host_tag:
        host_name = re.sub(r".*hosted by\s+", "", host_tag.get_text(), flags=re.I).strip()

    # 4. Room Type (Based on subtitle logic)
    room_type = "Entire Room"
    subtitle = soup.find("h2")
    if subtitle:
        text = subtitle.get_text()
        if "Private" in text: room_type = "Private Room"
        elif "Shared" in text: room_type = "Shared Room"

    # 5. Location Rating
    location_rating = 0.0
    loc_tag = soup.find("div", string="Location")
    if loc_tag:
        rating_span = loc_tag.find_next("span", class_=re.compile(r".*"))
        if rating_span:
            location_rating = float(rating_span.get_text())

    return {listing_id: {"policy_number": policy, "host_type": host_type, 
                         "host_name": host_name, "room_type": room_type, 
                         "location_rating": location_rating}}


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    
    listings = load_listing_results(html_path)
    database = []
    for title, listing_id in listings:
        details = get_listing_details(listing_id)
        d = details[listing_id]
        database.append((
            title,
            listing_id,
            d["policy_number"],
            d["host_type"],
            d["host_name"],
            d["room_type"],
            d["location_rating"]
        ))
    return database

def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)