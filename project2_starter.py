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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FOLDER = os.path.join(BASE_DIR, "html_files")

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
 
    
    for card in soup.find_all("div", attrs={"data-testid": "card-container"}):
        # Get the title
        title_tag = card.find("div", attrs={"data-testid": "listing-card-title"})
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
 
        
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
    path = os.path.join(HTML_FOLDER, f"listing_{listing_id}.html")
    
    
    with open(path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f, "html.parser")
    # 1. Policy
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

    # 4. Room Type 
    room_type = "Entire Room"
    subtitle = soup.find("h2")
    if subtitle:
        text = subtitle.get_text()
        if "Private" in text: room_type = "Private Room"
        elif "Shared" in text: room_type = "Shared Room"

    # 5. Location Rating
    location_rating = 0.0
    location_divs = soup.find_all("div", class_=lambda c: c and "_y1ba89" in c)
    for div in location_divs:
        if div.get_text(strip=True) == "Location":
            # The rating number is in the next sibling div's span
            parent = div.find_parent()
            if parent:
                rating_span = parent.find("span", class_=lambda c: c and "_4oybiu" in c)
                if rating_span:
                    try:
                        location_rating = float(rating_span.get_text(strip=True))
                    except ValueError:
                        location_rating = 0.0
            break

    return {
        listing_id: {
            "policy_number": policy,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }


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
    csv_path = os.path.join(BASE_DIR, filename)
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)
    # Use csv_path instead of filename
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Listing Title", "Listing ID", "Policy Number",
            "Host Type", "Host Name", "Room Type", "Location Rating"
        ])
        writer.writerows(sorted_data)



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
    totals = {}
    counts = {}
    for row in data:
        room_type = row[5]
        rating = row[6]
        if rating == 0.0:
            continue
        totals[room_type] = totals.get(room_type, 0) + rating
        counts[room_type] = counts.get(room_type, 0) + 1

    result = {}
    for rt in totals:
        avg = totals[rt] / counts[rt]
        result[rt] = round(avg, 1)
    return result


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    pattern = re.compile(r"^20\d{2}-00\d{4}STR$|^STR-000\d{4}$")
    invalid = []
    for row in data:
        listing_id = row[1]
        policy = row[2]
        if policy in ("Pending", "Exempt"):
            continue
        if not pattern.match(policy):
            invalid.append(listing_id)
    return invalid


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    for tag in soup.find_all("h3", class_="gs_rt"):
        title_text = tag.get_text(strip=True)
        title_text = re.sub(r"^\[.*?\]\s*", "", title_text)
        titles.append(title_text)
    return titles

class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        self.assertEqual(len(self.listings), 18)
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        results = [get_listing_details(i) for i in html_list]

        # 1
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        # 2
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        # 3
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
      

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        # Spot-check the LAST tuple
        self.assertEqual(
            self.detailed_data[-1],
            ("Guest suite in Mission District", "467507", "STR-0005349",
             "Superhost", "Jennifer", "Entire Room", 4.8)
        )

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        output_csv(self.detailed_data, out_path)
        with open(out_path, "r", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        # First data row index 1 skip headder
        self.assertEqual(
            rows[1],
            ["Guesthouse in San Francisco", "49591060", "STR-0000253",
             "Superhost", "Ingrid", "Entire Room", "5.0"]
        )
        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        result = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(result["Private Room"], 4.9)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])



def main():
    search_path = os.path.join(HTML_FOLDER, "search_results.html")
    if os.path.exists(search_path):
        detailed_data = create_listing_database(search_path)
        output_csv(detailed_data, "airbnb_dataset.csv")
    else:
        print(f"Error: Cannot find {search_path}")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)