# Flats for sale shown on the "Buy a flat" page.
#
# To publish an approved listing:
#   1. Save the seller's building photo as images/listings/<id>.jpg  (e.g. images/listings/F-001.jpg)
#   2. Copy the example below, remove the leading "# " and fill it in.
#   3. Run:  python3 src/build.py   then commit and push.
# To mark a flat as sold, set "sold": True (it stays on the page with a "Sold" label), or delete the entry.
#
# Text fields are pairs: ("English", "বাংলা"). The seller's own name and phone are NOT entered here;
# keep them in the email FormSubmit sent you.
#
# Example:
# {
#     "id": "F-001",
#     "location": ("Road 5, South Badda, Dhaka", "রোড ৫, দক্ষিণ বাড্ডা, ঢাকা"),
#     "size_sqft": 1250,
#     "bedrooms": 3, "bathrooms": 3,
#     "floor": 5, "total_floors": 9,
#     "price_bdt": 8500000, "negotiable": True,
#     "facilities": ["parking", "lift", "generator"],
#     "details": ("South-facing, ready to move in, near Gulshan link road.",
#                 "দক্ষিণমুখী, উঠার জন্য প্রস্তুত, গুলশান লিংক রোডের কাছে।"),
#     "sold": False,
# },

LISTINGS = [
]
