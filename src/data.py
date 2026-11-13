# Site content for JJ Works. Edit this file, then run:  python3 src/build.py
# Every text field is a pair: (English, Bangla).

SITE_URL = "https://jjworks.bd"
EMAIL = "jjworks.info@gmail.com"
WHATSAPP = "8801991111333"          # number used by every WhatsApp button
FORM_ACTION = "https://formsubmit.co/" + EMAIL

PEOPLE = [
    {"name": ("Engr. Md. Abu Naim Mia", "প্রকৌ. মো. আবু নাঈম মিয়া"),
     "role": ("Managing Partner", "ম্যানেজিং পার্টনার"),
     "phones": ["+88 01991-111333", "+88 01540-704123"]},
    {"name": ("Badrul Amin", "বদরুল আমিন"),
     "role": ("", ""), "phones": ["+88 01921-553299"]},
]

OFFICES = [
    ("House 105, Park Road, Mohakhali DOHS, Dhaka",
     "বাড়ি ১০৫, পার্ক রোড, মহাখালী ডিওএইচএস, ঢাকা"),
    ("54 Mujahidnagar, Rayerbag Road, Dhaka-1362",
     "৫৪ মুজাহিদনগর, রায়েরবাগ রোড, ঢাকা-১৩৬২"),
]

TYPES = {
    "residential": ("Residential", "আবাসিক"),
    "commercial": ("Commercial", "বাণিজ্যিক"),
    "mixed": ("Commercial + residential", "বাণিজ্যিক + আবাসিক"),
    "mosque": ("Mosque", "মসজিদ"),
}

# slug, name, location (or None), type, optional image focus (CSS object-position)
PROJECTS = [
    ("baitur-rahman-jame-mosque", ("Baitur Rahman Jame Mosque", "বাইতুর রহমান জামে মসজিদ"), None, "mosque", "50% 40%"),
    ("s-m-plaza", ("S M Plaza", "এস এম প্লাজা"), ("Victoria Road, Tangail", "ভিক্টোরিয়া রোড, টাঙ্গাইল"), "commercial", None),
    ("lake-garden", ("Lake Garden", "লেক গার্ডেন"), ("BA-81, 82, South Badda", "BA-81, 82, দক্ষিণ বাড্ডা"), "residential", None),
    ("paradise-nirjhor", ("Paradise Nirjhor", "প্যারাডাইস নির্ঝর"), None, "residential", "50% 15%"),
    ("lake-view-nibash", ("Lake View Nibash", "লেক ভিউ নিবাস"), ("BA-73/1, South Badda", "BA-73/1, দক্ষিণ বাড্ডা"), "residential", None),
    ("residential-tower-2025", ("Residential tower", "আবাসিক টাওয়ার"), None, "residential", None),
    ("rowshonara-nibash", ("Rowshonara Nibash", "রওশনারা নিবাস"), None, "residential", "50% 12%"),
    ("sopno-nibash", ("Sopno Nibash", "স্বপ্ন নিবাস"), ("BA-49, 50, 51, South Badda", "BA-49, 50, 51, দক্ষিণ বাড্ডা"), "residential", "50% 12%"),
    ("green-halmet", ("Green Halmet", "Green Halmet"), ("Savar, Dhaka", "সাভার, ঢাকা"), "residential", "50% 30%"),
    ("neoge-lodge", ("Neoge Lodge", "Neoge Lodge"), ("Tangail", "টাঙ্গাইল"), "mixed", None),
    ("karims-nibash", ("Karim's Nibash", "করিমস নিবাস"), None, "mixed", "50% 15%"),
    ("ba-75", ("BA-75", "BA-75"), None, "residential", None),
    ("ba-76", ("BA-76", "BA-76"), None, "residential", None),
    ("mohabbat", ("Mohabbat", "মোহাব্বত"), None, "residential", None),
    ("sayeda-nibash", ("Sayeda Nibash", "সাঈদা নিবাস"), ("Tangail", "টাঙ্গাইল"), "residential", None),
    ("apon-nibash", ("Apon Nibash", "আপন নিবাস"), ("BA-26, 27, South Badda", "BA-26, 27, দক্ষিণ বাড্ডা"), "residential", None),
    ("sofi-nibash", ("Sofi Nibash", "সফি নিবাস"), ("Vatara, Dhaka", "ভাটারা, ঢাকা"), "residential", "50% 12%"),
    ("mir-nibash", ("Mir Nibash", "মীর নিবাস"), ("South Badda, Dhaka", "দক্ষিণ বাড্ডা, ঢাকা"), "residential", "50% 12%"),
    ("noorjahan-nibash", ("Noorjahan Nibash", "নূরজাহান নিবাস"), ("TA-134/1, Middle Badda", "TA-134/1, মধ্য বাড্ডা"), "residential", None),
    ("suraiya-nibash", ("Suraiya Nibash", "সুরাইয়া নিবাস"), ("Akur Takur Para, Tangail", "আকুর টাকুর পাড়া, টাঙ্গাইল"), "residential", "50% 8%"),
]

SERVICES = [
    (("Architectural design", "স্থাপত্য নকশা"),
     ("Plans, elevations and sections for homes, apartment buildings and commercial blocks, drawn to suit the plot and the RAJUK approval process.",
      "প্লট ও রাজউক অনুমোদন প্রক্রিয়া মাথায় রেখে বাড়ি, অ্যাপার্টমেন্ট ভবন ও বাণিজ্যিক ভবনের প্ল্যান, এলিভেশন ও সেকশন।")),
    (("Structural design", "কাঠামোগত নকশা"),
     ("RCC design for foundations, columns, beams and slabs, checked against BNBC requirements.",
      "ফাউন্ডেশন, কলাম, বিম ও স্ল্যাবের আরসিসি ডিজাইন, বিএনবিসি অনুযায়ী যাচাইকৃত।")),
    (("Civil works", "সিভিল কাজ"),
     ("Site preparation, piling, foundations and the structural frame, supervised by our engineers.",
      "সাইট প্রস্তুতি, পাইলিং, ফাউন্ডেশন ও কাঠামো নির্মাণ, আমাদের প্রকৌশলীদের তত্ত্বাবধানে।")),
    (("Interior design and execution", "ইন্টেরিয়র ডিজাইন ও বাস্তবায়ন"),
     ("Layouts, 3D views, materials and fit-out for flats, offices and shops, built by our own team.",
      "ফ্ল্যাট, অফিস ও দোকানের লেআউট, থ্রিডি ভিউ, ম্যাটেরিয়াল নির্বাচন ও কাজ, আমাদের নিজস্ব দল দিয়ে।")),
    (("Exterior and facade design", "এক্সটেরিয়র ও ফাসাড ডিজাইন"),
     ("Facade concepts, colour and material choices that look good and hold up to Dhaka weather.",
      "ঢাকার আবহাওয়ায় টেকসই ও সুন্দর ফাসাড, রং ও ম্যাটেরিয়াল নির্বাচন।")),
    (("Construction", "নির্মাণ"),
     ("Full building construction with a BOQ, a schedule and regular progress reports.",
      "বিওকিউ, সময়সূচি ও নিয়মিত অগ্রগতি প্রতিবেদনসহ সম্পূর্ণ ভবন নির্মাণ।")),
    (("Consultancy", "পরামর্শ সেবা"),
     ("Second opinions, structural checks, BOQ preparation and code-compliance advice.",
      "দ্বিতীয় মতামত, কাঠামোগত পরীক্ষা, বিওকিউ প্রস্তুতি ও বিল্ডিং কোড বিষয়ে পরামর্শ।")),
    (("Landscape and space planning", "ল্যান্ডস্কেপ ও স্পেস প্ল্যানিং"),
     ("Rooftops, courtyards, parking and setbacks planned so every square foot is used well.",
      "ছাদ, উঠান, পার্কিং ও সেটব্যাক এমনভাবে পরিকল্পনা যাতে প্রতিটি বর্গফুট কাজে লাগে।")),
]

REASONS = [
    (("Engineers on the team", "দলেই প্রকৌশলী"),
     ("Our structural engineers work alongside the designers, so what is drawn can be built.",
      "আমাদের স্ট্রাকচারাল প্রকৌশলীরা ডিজাইনারদের সাথেই কাজ করেন, তাই যা আঁকা হয় তা বাস্তবে নির্মাণযোগ্য।")),
    (("One point of contact", "একটিই যোগাযোগ"),
     ("Design, approvals support and construction are handled by one team.",
      "ডিজাইন, অনুমোদন সহায়তা ও নির্মাণ এক দলই সামলায়।")),
    (("Built to code", "কোড মেনে নির্মাণ"),
     ("Every project follows BNBC and RAJUK DAP 2022–2035.",
      "প্রতিটি প্রকল্প বিএনবিসি ও রাজউক ড্যাপ ২০২২–২০৩৫ মেনে চলে।")),
    (("Clear proposals", "স্পষ্ট প্রস্তাব"),
     ("Defined scope, payment milestones and a stated revision policy before work starts.",
      "কাজ শুরুর আগেই নির্দিষ্ট কাজের পরিধি, কিস্তির ধাপ ও সংশোধন নীতি।")),
    (("Direct access", "সরাসরি যোগাযোগ"),
     ("You can call the engineer working on your building at any stage.",
      "যেকোনো পর্যায়ে আপনার ভবনের দায়িত্বপ্রাপ্ত প্রকৌশলীকে সরাসরি ফোন করতে পারবেন।")),
]

PROCESS = [
    (("Consultation and site visit", "পরামর্শ ও সাইট পরিদর্শন"),
     ("We meet you, visit the plot and talk through your needs and budget.",
      "আপনার সাথে কথা বলে, প্লট দেখে প্রয়োজন ও বাজেট বুঝে নিই।")),
    (("Concept drawings", "প্রাথমিক নকশা"),
     ("First layout options so you can choose a direction.",
      "দিক ঠিক করতে প্রথম কয়েকটি লেআউট বিকল্প।")),
    (("Design development", "নকশা উন্নয়ন"),
     ("Detailed drawings, 3D views and material choices.",
      "বিস্তারিত ড্রয়িং, থ্রিডি ভিউ ও ম্যাটেরিয়াল নির্বাচন।")),
    (("Structure and compliance", "কাঠামো ও কোড যাচাই"),
     ("RCC design, BOQ and code checks.",
      "আরসিসি ডিজাইন, বিওকিউ ও কোড যাচাই।")),
    (("Construction and supervision", "নির্মাণ ও তত্ত্বাবধান"),
     ("Building work, quality control and progress reports.",
      "নির্মাণকাজ, মান নিয়ন্ত্রণ ও অগ্রগতি প্রতিবেদন।")),
    (("Handover", "হস্তান্তর"),
     ("A final walkthrough together, then the keys are yours.",
      "একসাথে চূড়ান্ত পরিদর্শন, তারপর চাবি আপনার হাতে।")),
]
