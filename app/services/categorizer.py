# Rules are checked in order — first match wins
CATEGORY_RULES = [
    ("Cloud & Software", ["AMAZON WEB SERVICES", "AWS.AMAZON"]),
    ("Streaming", ["NETFLIX", "HBOMAX", "HELP.HBOMAX", "SLING TV", "YOUTUBE", "DISNEY+"]),
    ("Subscriptions", [
        "APPLE.COM/BILL", "MICROSOFT*XBOX", "GOOGLE ONE", "ADOBE",
        "AMAZON PRIME", "HP INSTANT INK", "DOORDASHDASHPASS", "EQUIFAX",
    ]),
    ("Groceries", [
        "WHOLE FOODS", "WHOLEFDS", "SAFEWAY", "COSTCO WHSE",
        "TRADER JOE", "KROGER", "SPROUTS",
    ]),
    ("Restaurants & Food Delivery", [
        "URBAN PLATES", "TST*", "DOORDASH", "IN-N-OUT", "DAVES HOT CHICKEN",
        "BIRYANI", "PROPOSITION CHICKEN", "LOCANDA", "CHIPOTLE",
    ]),
    ("Gas", ["COSTCO GAS", "CHEVRON", "SHELL", "EXXON", "ARCO", "MOBIL"]),
    ("Shopping", ["AMAZON MKTPL", "AMAZON.COM", "CRATE & BARREL", "ECOMX"]),
    ("Insurance", ["CSAA INSURANCE", "GEICO", "STATE FARM"]),
    ("Utilities & Phone", ["PRIMO BRANDS", "AT&T", "COMCAST", "XFINITY", "PG&E", "BARKER HEATING"]),
    ("Transportation", ["BART PARKING", "FASTRAK", "CA DMV", "PRESIDIO-CALE PARK", "LYFT", "UBER"]),
    ("Education & Activities", [
        "WHARTON GLOBAL", "TPC BASEBALL", "SUMMER DISCOVERY", "UCD COSMOS", "DRIVERSED",
    ]),
    ("Health", ["WALGREEN", "LIPPMAN", "CVS", "KAISER", "CHIROPRACTIC", "PHARMACY"]),
    ("Home Services", ["BARKER HEATING", "HOME DEPOT", "LOWES"]),
]


def categorize(description: str) -> str:
    desc_upper = description.upper()
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword.upper() in desc_upper:
                return category
    return "Other"
