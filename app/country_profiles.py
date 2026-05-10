"""
app/country_profiles.py
=======================
Static profiles for all 47 Asian countries covered by the Asia Livability AI project.

Each profile contains:
  - Quick facts  : capital, population, area, languages
  - Brief history: ~4-sentence overview
  - Currency     : name, ISO code, symbol, approximate 2024 USD rate
  - Cost of living: approximate monthly USD figures (2024 Numbeo-style estimates)
  - Fun facts    : 3 interesting facts
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Schema reference (for type checking)
# ---------------------------------------------------------------------------
# Profile = {
#   "name": str,
#   "capital": str,
#   "population": str,
#   "area_km2": int,
#   "languages": list[str],
#   "history": str,
#   "currency": {
#       "name": str, "code": str, "symbol": str,
#       "approx_usd_rate": float,   # units of local currency per 1 USD
#   },
#   "cost_of_living": {
#       "monthly_rent_city_1br": float,    # USD
#       "monthly_groceries": float,         # USD
#       "monthly_transport": float,         # USD (monthly pass)
#       "monthly_utilities": float,         # USD (85 m² apt)
#       "avg_monthly_salary_net": float,    # USD
#       "meal_cheap_restaurant": float,     # USD
#   },
#   "fun_facts": list[str],
# }

COUNTRY_PROFILES: dict[str, dict] = {

    # ── East Asia ─────────────────────────────────────────────────────────────
    "CHN": {
        "name": "China",
        "capital": "Beijing",
        "population": "1.41 billion",
        "area_km2": 9_596_960,
        "languages": ["Mandarin Chinese"],
        "history": (
            "China is one of the world's oldest civilisations, with continuous recorded history "
            "spanning over 3,500 years. Imperial dynasties — from the Qin and Han to the Ming "
            "and Qing — shaped East Asian culture, writing, and philosophy. Following the 1911 "
            "revolution and decades of civil war, the People's Republic was founded in 1949. "
            "Market-oriented reforms since the 1980s transformed China into the world's second-"
            "largest economy and a major global power."
        ),
        "currency": {
            "name": "Chinese Yuan Renminbi",
            "code": "CNY",
            "symbol": "¥",
            "approx_usd_rate": 7.24,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 580,
            "monthly_groceries": 200,
            "monthly_transport": 35,
            "monthly_utilities": 60,
            "avg_monthly_salary_net": 1_200,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "China is home to the world's largest high-speed rail network (over 40,000 km).",
            "The Great Wall stretches more than 21,000 km across northern China.",
            "China produces and consumes about half of the world's pork each year.",
        ],
    },

    "JPN": {
        "name": "Japan",
        "capital": "Tokyo",
        "population": "123 million",
        "area_km2": 377_975,
        "languages": ["Japanese"],
        "history": (
            "Japan's recorded history begins around the 3rd century BCE, with early society "
            "shaped by Chinese and Korean cultural influences. The feudal era (12th–19th century) "
            "was dominated by samurai clans, culminating in the Edo period of isolation. After "
            "the Meiji Restoration (1868), Japan rapidly modernised and became an imperial power. "
            "Defeated in World War II, Japan rebuilt under a pacifist constitution and rose to "
            "become the world's third-largest economy."
        ),
        "currency": {
            "name": "Japanese Yen",
            "code": "JPY",
            "symbol": "¥",
            "approx_usd_rate": 150,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 900,
            "monthly_groceries": 350,
            "monthly_transport": 90,
            "monthly_utilities": 130,
            "avg_monthly_salary_net": 2_500,
            "meal_cheap_restaurant": 8,
        },
        "fun_facts": [
            "Japan has the world's highest life expectancy — over 84 years on average.",
            "There are more vending machines per person in Japan than in almost any other country.",
            "Japan experiences around 1,500 earthquakes every year.",
        ],
    },

    "KOR": {
        "name": "South Korea",
        "capital": "Seoul",
        "population": "51.7 million",
        "area_km2": 100_210,
        "languages": ["Korean"],
        "history": (
            "The Korean peninsula has been inhabited for thousands of years and was unified "
            "under the Silla dynasty in 676 CE. After centuries of dynastic rule, Korea was "
            "annexed by Japan (1910–1945). The peninsula was divided after World War II, and "
            "the Korean War (1950–53) cemented the North–South split. South Korea's subsequent "
            "\"Miracle on the Han River\" turned it from a war-torn nation into a high-tech "
            "global economy in just a few decades."
        ),
        "currency": {
            "name": "South Korean Won",
            "code": "KRW",
            "symbol": "₩",
            "approx_usd_rate": 1_350,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 700,
            "monthly_groceries": 300,
            "monthly_transport": 70,
            "monthly_utilities": 120,
            "avg_monthly_salary_net": 2_200,
            "meal_cheap_restaurant": 6,
        },
        "fun_facts": [
            "South Korea has the world's fastest average internet speed.",
            "Seoul's metro system is one of the longest in the world at over 1,000 km.",
            "South Korea is the world's largest exporter of ships.",
        ],
    },

    "MNG": {
        "name": "Mongolia",
        "capital": "Ulaanbaatar",
        "population": "3.3 million",
        "area_km2": 1_564_116,
        "languages": ["Mongolian"],
        "history": (
            "Mongolia is the birthplace of Genghis Khan, who in the 13th century united nomadic "
            "tribes to forge the largest contiguous land empire in history. After the empire's "
            "fragmentation, the region came under Qing Chinese rule from the 17th century until "
            "independence in 1911. A communist Mongolian People's Republic existed from 1924 to "
            "1990, when peaceful democratic reforms transformed the country into a parliamentary "
            "republic with a growing mining-driven economy."
        ),
        "currency": {
            "name": "Mongolian Tögrög",
            "code": "MNT",
            "symbol": "₮",
            "approx_usd_rate": 3_450,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 350,
            "monthly_groceries": 150,
            "monthly_transport": 25,
            "monthly_utilities": 45,
            "avg_monthly_salary_net": 450,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Mongolia is the most sparsely populated sovereign country in the world.",
            "About 30% of Mongolians still lead a nomadic or semi-nomadic lifestyle.",
            "The Gobi Desert, covering 1.3 million km², spans southern Mongolia and northern China.",
        ],
    },

    "PRK": {
        "name": "North Korea",
        "capital": "Pyongyang",
        "population": "25.9 million",
        "area_km2": 120_538,
        "languages": ["Korean"],
        "history": (
            "North Korea traces its modern origin to the Soviet-backed government established "
            "after Japan's 1945 defeat. The Korean War (1950–1953) ended in an armistice, leaving "
            "the peninsula divided. Under the Kim family dynasty — Kim Il-sung, Kim Jong-il, and "
            "Kim Jong-un — the country developed one of the world's most centralised and secretive "
            "command economies, pursuing nuclear weapons despite severe international sanctions."
        ),
        "currency": {
            "name": "North Korean Won",
            "code": "KPW",
            "symbol": "₩",
            "approx_usd_rate": 900,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 50,
            "monthly_groceries": 100,
            "monthly_transport": 5,
            "monthly_utilities": 10,
            "avg_monthly_salary_net": 50,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "North Korea operates its own calendar system — the Juche calendar — starting from Kim Il-sung's birth in 1912.",
            "Every able-bodied citizen is required to serve in the military for up to 10 years.",
            "Pyongyang has a metro system that doubles as one of the world's deepest nuclear shelters.",
        ],
    },

    # ── Southeast Asia ────────────────────────────────────────────────────────
    "BRN": {
        "name": "Brunei Darussalam",
        "capital": "Bandar Seri Begawan",
        "population": "450,000",
        "area_km2": 5_765,
        "languages": ["Malay", "English"],
        "history": (
            "The Bruneian Empire was a powerful maritime sultanate from the 15th to the 17th "
            "century, controlling much of Borneo and the Philippines. After centuries of decline, "
            "Brunei became a British protectorate in 1888, gaining full independence in 1984. "
            "Oil and natural gas, discovered in 1929, transformed the tiny sultanate into one of "
            "Southeast Asia's wealthiest nations, enabling a cradle-to-grave welfare state under "
            "Sultan Hassanal Bolkiah."
        ),
        "currency": {
            "name": "Brunei Dollar",
            "code": "BND",
            "symbol": "B$",
            "approx_usd_rate": 1.34,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 600,
            "monthly_groceries": 250,
            "monthly_transport": 40,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 2_000,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Brunei citizens pay no income tax and receive free education and healthcare.",
            "The Sultan's palace, Istana Nurul Iman, is the world's largest residential palace.",
            "Brunei is entirely surrounded by Malaysia except for its coastline on the South China Sea.",
        ],
    },

    "IDN": {
        "name": "Indonesia",
        "capital": "Jakarta (moving to Nusantara)",
        "population": "278 million",
        "area_km2": 1_904_569,
        "languages": ["Indonesian (Bahasa Indonesia)", "700+ regional languages"],
        "history": (
            "Indonesia's archipelago has been home to advanced Hindu-Buddhist kingdoms such as "
            "Srivijaya and Majapahit since the 7th century CE. The region was gradually "
            "Islamised from the 13th century and later colonised by the Dutch East India Company, "
            "becoming the Dutch East Indies. Independence was proclaimed in 1945, and after "
            "decades of authoritarian rule under Sukarno and Suharto, Indonesia transitioned to "
            "democracy in 1998, becoming the world's third-largest democracy."
        ),
        "currency": {
            "name": "Indonesian Rupiah",
            "code": "IDR",
            "symbol": "Rp",
            "approx_usd_rate": 15_900,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 120,
            "monthly_transport": 30,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 400,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Indonesia is the world's largest archipelago, comprising over 17,000 islands.",
            "It is the world's largest Muslim-majority country by population.",
            "Indonesia is home to the Komodo dragon, the world's largest living lizard.",
        ],
    },

    "KHM": {
        "name": "Cambodia",
        "capital": "Phnom Penh",
        "population": "16.7 million",
        "area_km2": 181_035,
        "languages": ["Khmer"],
        "history": (
            "The Khmer Empire (9th–15th century) was one of Southeast Asia's most powerful "
            "civilisations, constructing Angkor Wat — the world's largest religious monument. "
            "After centuries of decline and colonial rule under France (1863–1953), Cambodia "
            "endured devastating civil war and the Khmer Rouge genocide (1975–1979), which "
            "killed an estimated 1.5–2 million people. Since the 1990s peace agreements, the "
            "country has rebuilt and experienced strong economic growth driven by garments and tourism."
        ),
        "currency": {
            "name": "Cambodian Riel",
            "code": "KHR",
            "symbol": "៛",
            "approx_usd_rate": 4_100,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 300,
            "monthly_groceries": 100,
            "monthly_transport": 25,
            "monthly_utilities": 60,
            "avg_monthly_salary_net": 300,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "Angkor Wat is the world's largest religious monument, covering about 400 acres.",
            "The US dollar is widely accepted alongside the riel in everyday transactions.",
            "Tonlé Sap Lake is Southeast Asia's largest freshwater lake and reverses its flow seasonally.",
        ],
    },

    "LAO": {
        "name": "Lao PDR",
        "capital": "Vientiane",
        "population": "7.4 million",
        "area_km2": 236_800,
        "languages": ["Lao"],
        "history": (
            "The Lan Xang Kingdom ('Kingdom of a Million Elephants'), founded in 1353, united "
            "much of present-day Laos and became a major power in mainland Southeast Asia. "
            "After fragmentation and Siamese and Vietnamese domination, Laos became a French "
            "protectorate in 1893. Independence came in 1953, followed by civil war and a "
            "communist Pathet Lao takeover in 1975. Today the country is governed by a single-"
            "party state while gradually opening its economy to foreign investment."
        ),
        "currency": {
            "name": "Lao Kip",
            "code": "LAK",
            "symbol": "₭",
            "approx_usd_rate": 21_000,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 90,
            "monthly_transport": 20,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 250,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Laos is the most heavily bombed country per capita in history, due to US bombing during the Vietnam War era.",
            "The Plain of Jars — thousands of ancient stone vessels — remains a UNESCO World Heritage site.",
            "Laos is the only landlocked country in Southeast Asia.",
        ],
    },

    "MMR": {
        "name": "Myanmar",
        "capital": "Naypyidaw",
        "population": "54 million",
        "area_km2": 676_578,
        "languages": ["Burmese"],
        "history": (
            "Myanmar's ancient kingdoms — Pagan, Ava, and Toungoo — dominated mainland Southeast "
            "Asia for centuries. British colonisation (1824–1948) transformed the economy and "
            "created lasting ethnic tensions. Independence in 1948 was followed by military rule "
            "from 1962 and international isolation. A brief democratic opening under Aung San "
            "Suu Kyi (2011–2021) ended with a military coup in February 2021, triggering ongoing "
            "civil conflict."
        ),
        "currency": {
            "name": "Myanmar Kyat",
            "code": "MMK",
            "symbol": "K",
            "approx_usd_rate": 2_100,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 80,
            "monthly_transport": 20,
            "monthly_utilities": 40,
            "avg_monthly_salary_net": 200,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Myanmar has more Buddhist pagodas than any other country, including over 2,000 in Bagan alone.",
            "Naypyidaw, the purpose-built capital, has a 20-lane highway that is largely empty.",
            "Myanmar produces about 90% of the world's rubies.",
        ],
    },

    "MYS": {
        "name": "Malaysia",
        "capital": "Kuala Lumpur",
        "population": "33 million",
        "area_km2": 329_847,
        "languages": ["Malay (Bahasa Malaysia)", "English", "Chinese dialects", "Tamil"],
        "history": (
            "The Malacca Sultanate (15th–16th century) was a thriving Islamic trading hub before "
            "Portuguese, then Dutch, then British colonisation. British Malaya became a rubber "
            "and tin export powerhouse. Malaysia gained independence in 1957 and formed the "
            "federation in 1963. Rapid industrialisation under Mahathir Mohamad's Vision 2020 "
            "agenda turned Malaysia into one of Southeast Asia's most developed economies."
        ),
        "currency": {
            "name": "Malaysian Ringgit",
            "code": "MYR",
            "symbol": "RM",
            "approx_usd_rate": 4.7,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 150,
            "monthly_transport": 40,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 800,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "The Petronas Twin Towers in Kuala Lumpur were the world's tallest buildings from 1998 to 2004.",
            "Malaysia is one of only 12 'megadiverse' countries in the world, with extraordinary biodiversity.",
            "Malaysia is the world's second-largest producer of palm oil.",
        ],
    },

    "PHL": {
        "name": "Philippines",
        "capital": "Manila",
        "population": "115 million",
        "area_km2": 300_000,
        "languages": ["Filipino (Tagalog)", "English"],
        "history": (
            "The Philippine archipelago was home to diverse indigenous polities before Spanish "
            "colonisation in 1565, which brought Catholicism and 333 years of colonial rule. "
            "The Philippines became a US territory after the 1898 Spanish-American War, gaining "
            "independence in 1946. After the Marcos dictatorship (1972–1986), a 'People Power' "
            "revolution restored democracy. Today, the Philippines is Southeast Asia's fastest-"
            "growing major economy, driven by services, remittances, and a young population."
        ),
        "currency": {
            "name": "Philippine Peso",
            "code": "PHP",
            "symbol": "₱",
            "approx_usd_rate": 57,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 350,
            "monthly_groceries": 150,
            "monthly_transport": 25,
            "monthly_utilities": 80,
            "avg_monthly_salary_net": 500,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "The Philippines is the world's third-largest English-speaking country.",
            "Filipino workers overseas send home over $30 billion per year — about 9% of GDP.",
            "The jeepney, a colourfully decorated bus derived from WWII US jeeps, is a national icon.",
        ],
    },

    "SGP": {
        "name": "Singapore",
        "capital": "Singapore (city-state)",
        "population": "5.9 million",
        "area_km2": 733,
        "languages": ["English", "Mandarin", "Malay", "Tamil"],
        "history": (
            "A small fishing village until Sir Stamford Raffles established a British trading "
            "post in 1819, Singapore rapidly became one of Asia's most important ports. It was "
            "occupied by Japan (1942–45) and merged briefly with Malaysia before full independence "
            "in 1965. Under Lee Kuan Yew's leadership, Singapore transformed itself within a "
            "generation from a developing city into a global financial hub and one of the world's "
            "highest-income nations."
        ),
        "currency": {
            "name": "Singapore Dollar",
            "code": "SGD",
            "symbol": "S$",
            "approx_usd_rate": 1.34,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 2_800,
            "monthly_groceries": 400,
            "monthly_transport": 100,
            "monthly_utilities": 180,
            "avg_monthly_salary_net": 3_800,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "Singapore is the world's only city-state that is also an island nation.",
            "Changi Airport has won 'World's Best Airport' more than any other airport.",
            "Singapore has no natural freshwater resources and imports water from Malaysia.",
        ],
    },

    "THA": {
        "name": "Thailand",
        "capital": "Bangkok",
        "population": "71 million",
        "area_km2": 513_120,
        "languages": ["Thai"],
        "history": (
            "Thailand — formerly Siam — is the only Southeast Asian country never colonised by "
            "a European power, maintaining sovereignty through shrewd diplomacy. The Sukhothai "
            "and Ayutthaya kingdoms shaped Thai culture and Buddhism from the 13th century. "
            "The country modernised under King Chulalongkorn (Rama V) in the late 19th century "
            "and became a constitutional monarchy in 1932. Despite periodic military coups, "
            "Thailand has built a large tourism and export manufacturing economy."
        ),
        "currency": {
            "name": "Thai Baht",
            "code": "THB",
            "symbol": "฿",
            "approx_usd_rate": 36,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 150,
            "monthly_transport": 30,
            "monthly_utilities": 70,
            "avg_monthly_salary_net": 600,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "Thailand is the world's top exporter of rice.",
            "Bangkok has the world's longest city name: Krungthepmahanakhon Amonrattanakosin Mahintharayutthaya…",
            "Over 94% of Thailand's population identifies as Buddhist.",
        ],
    },

    "TLS": {
        "name": "Timor-Leste",
        "capital": "Dili",
        "population": "1.3 million",
        "area_km2": 14_874,
        "languages": ["Tetum", "Portuguese"],
        "history": (
            "Timor-Leste was colonised by Portugal for nearly 450 years until 1975, when "
            "Indonesia invaded and occupied the territory for 24 years in a conflict that "
            "killed tens of thousands. After a 1999 UN-sponsored referendum, the population "
            "voted overwhelmingly for independence, which was formally achieved in 2002, making "
            "Timor-Leste one of the world's newest nations. The country depends heavily on "
            "oil revenues from the Timor Sea, which it is working to diversify as reserves decline."
        ),
        "currency": {
            "name": "United States Dollar",
            "code": "USD",
            "symbol": "$",
            "approx_usd_rate": 1.0,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 200,
            "monthly_transport": 30,
            "monthly_utilities": 80,
            "avg_monthly_salary_net": 200,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Timor-Leste uses the US dollar as its currency despite never being a US territory.",
            "It is one of the youngest countries in the world, gaining independence in 2002.",
            "The country is split between the western Indonesian province of West Timor and the independent east.",
        ],
    },

    "VNM": {
        "name": "Viet Nam",
        "capital": "Hanoi",
        "population": "98 million",
        "area_km2": 331_212,
        "languages": ["Vietnamese"],
        "history": (
            "Vietnam has a civilisation dating back over 2,000 years, with long periods of "
            "Chinese rule followed by centuries of independence under dynasties such as the Ly "
            "and Nguyen. French colonisation (1883–1954) ended with the decisive Battle of "
            "Dien Bien Phu. The subsequent Vietnam War (1955–1975) between North and South, "
            "with US involvement, ended with reunification under communist rule in 1975. Doi Moi "
            "economic reforms from 1986 opened Vietnam to markets, and it has since become one "
            "of Asia's fastest-growing economies."
        ),
        "currency": {
            "name": "Vietnamese Đồng",
            "code": "VND",
            "symbol": "₫",
            "approx_usd_rate": 25_400,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 300,
            "monthly_groceries": 100,
            "monthly_transport": 20,
            "monthly_utilities": 40,
            "avg_monthly_salary_net": 400,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Vietnam is the world's second-largest exporter of coffee, after Brazil.",
            "The country has over 3,000 km of coastline along the South China Sea.",
            "Ha Long Bay — featuring nearly 2,000 limestone islands — is a UNESCO World Heritage Site.",
        ],
    },

    # ── South Asia ────────────────────────────────────────────────────────────
    "AFG": {
        "name": "Afghanistan",
        "capital": "Kabul",
        "population": "41 million",
        "area_km2": 652_230,
        "languages": ["Dari (Persian)", "Pashto"],
        "history": (
            "At the crossroads of empires, Afghanistan has been invaded by Persians, Alexander "
            "the Great, Mongols, and British forces across its long history. It became a buffer "
            "state during the 19th-century 'Great Game' between Britain and Russia. The Soviet "
            "invasion (1979–1989) triggered a decade of war, followed by civil conflict and "
            "Taliban rule. The US-led coalition ousted the Taliban in 2001; however, the Taliban "
            "returned to power in August 2021, triggering a severe humanitarian crisis."
        ),
        "currency": {
            "name": "Afghan Afghani",
            "code": "AFN",
            "symbol": "؋",
            "approx_usd_rate": 70,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 150,
            "monthly_groceries": 80,
            "monthly_transport": 15,
            "monthly_utilities": 30,
            "avg_monthly_salary_net": 100,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Afghanistan has some of the world's largest untapped mineral reserves, estimated at $1–3 trillion.",
            "Buzkashi — a sport in which horsemen compete to carry a goat carcass — is the national sport.",
            "The Minaret of Jam, a 65-metre UNESCO World Heritage site, dates to the 12th century.",
        ],
    },

    "BGD": {
        "name": "Bangladesh",
        "capital": "Dhaka",
        "population": "170 million",
        "area_km2": 147_570,
        "languages": ["Bengali (Bangla)"],
        "history": (
            "Bangladesh was part of British India's Bengal province until Partition in 1947, when "
            "it became East Pakistan. Suppression of Bengali culture and economic marginalisation "
            "sparked the 1971 Liberation War; with Indian assistance, Bangladesh won independence "
            "in December 1971. Despite being one of the world's most densely populated countries "
            "and highly vulnerable to cyclones and flooding, Bangladesh has achieved remarkable "
            "economic growth, driven by the garment industry, which makes it one of the world's "
            "top clothing exporters."
        ),
        "currency": {
            "name": "Bangladeshi Taka",
            "code": "BDT",
            "symbol": "৳",
            "approx_usd_rate": 110,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 150,
            "monthly_groceries": 70,
            "monthly_transport": 15,
            "monthly_utilities": 30,
            "avg_monthly_salary_net": 200,
            "meal_cheap_restaurant": 0.8,
        },
        "fun_facts": [
            "Bangladesh is the world's most densely populated large country, with about 1,100 people per km².",
            "It is the world's second-largest garment exporter, accounting for ~80% of total exports.",
            "The Sundarbans mangrove forest, shared with India, is the world's largest mangrove ecosystem.",
        ],
    },

    "BTN": {
        "name": "Bhutan",
        "capital": "Thimphu",
        "population": "780,000",
        "area_km2": 38_394,
        "languages": ["Dzongkha"],
        "history": (
            "Bhutan was unified in the 17th century under the Zhabdrung Ngawang Namgyal, a "
            "Tibetan Buddhist lama who established a distinct national identity. It successfully "
            "repelled British attempts at annexation and signed a treaty of friendship in 1910, "
            "becoming a protectorate without losing sovereignty. Bhutan became a constitutional "
            "monarchy in 2008 when the fourth king voluntarily transferred power to an elected "
            "parliament. The country is internationally known for measuring progress by Gross "
            "National Happiness rather than GDP."
        ),
        "currency": {
            "name": "Bhutanese Ngultrum",
            "code": "BTN",
            "symbol": "Nu",
            "approx_usd_rate": 83,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 200,
            "monthly_groceries": 100,
            "monthly_transport": 20,
            "monthly_utilities": 25,
            "avg_monthly_salary_net": 350,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "Bhutan measures national progress using Gross National Happiness rather than GDP.",
            "Bhutan is the world's only carbon-negative country — it absorbs more CO₂ than it emits.",
            "Tourism to Bhutan is managed through a high-value, low-impact policy with a daily tourist fee.",
        ],
    },

    "IND": {
        "name": "India",
        "capital": "New Delhi",
        "population": "1.43 billion",
        "area_km2": 3_287_263,
        "languages": ["Hindi", "English", "21 other official languages"],
        "history": (
            "India is home to one of the world's oldest civilisations — the Indus Valley — "
            "dating back to around 3300 BCE. It was the birthplace of Hinduism, Buddhism, and "
            "Jainism. Mughal emperors ruled much of the subcontinent from the 16th century until "
            "British East India Company and then Crown control. India's independence in 1947, led "
            "by Mahatma Gandhi's nonviolent movement, was accompanied by a painful Partition that "
            "created Pakistan. Today, India is the world's most populous country and the fifth-"
            "largest economy."
        ),
        "currency": {
            "name": "Indian Rupee",
            "code": "INR",
            "symbol": "₹",
            "approx_usd_rate": 83,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 80,
            "monthly_transport": 15,
            "monthly_utilities": 30,
            "avg_monthly_salary_net": 500,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "India surpassed China in 2023 to become the world's most populous country.",
            "India produces the most films annually — over 1,800 per year, spread across many languages.",
            "The game of chess was invented in India around the 6th century CE.",
        ],
    },

    "LKA": {
        "name": "Sri Lanka",
        "capital": "Sri Jayawardenepura Kotte (legislative) / Colombo (commercial)",
        "population": "22 million",
        "area_km2": 65_610,
        "languages": ["Sinhala", "Tamil", "English"],
        "history": (
            "Sri Lanka has a recorded history of over 3,000 years, with ancient kingdoms at "
            "Anuradhapura and Polonnaruwa. The island was colonised successively by the "
            "Portuguese, Dutch, and British, who called it Ceylon. Independence came in 1948. "
            "A bitter civil war between the government and Tamil Tiger separatists lasted from "
            "1983 to 2009. In 2022, a severe economic crisis triggered by forex shortages led to "
            "mass protests and the ousting of President Gotabaya Rajapaksa."
        ),
        "currency": {
            "name": "Sri Lankan Rupee",
            "code": "LKR",
            "symbol": "Rs",
            "approx_usd_rate": 305,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 100,
            "monthly_transport": 20,
            "monthly_utilities": 40,
            "avg_monthly_salary_net": 350,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Sri Lanka produces some of the world's finest tea (Ceylon tea) and is a top exporter.",
            "The country has the world's oldest documented tree still in the same spot — the Jaya Sri Maha Bodhi, planted 288 BCE.",
            "Sri Lanka was the first country in the world to elect a female head of government (Sirimavo Bandaranaike, 1960).",
        ],
    },

    "MDV": {
        "name": "Maldives",
        "capital": "Malé",
        "population": "530,000",
        "area_km2": 298,
        "languages": ["Dhivehi"],
        "history": (
            "The Maldives has been inhabited for at least 2,500 years and converted to Islam in "
            "1153 CE. It was a British protectorate from 1887 to 1965, when it gained "
            "independence, becoming a republic in 1968. The Maldives is best known internationally "
            "as a luxury tourism destination and for its vulnerability to rising sea levels — "
            "most of its land lies just 1.5 metres above sea level, making it one of the most "
            "climate-threatened nations on Earth."
        ),
        "currency": {
            "name": "Maldivian Rufiyaa",
            "code": "MVR",
            "symbol": "Rf",
            "approx_usd_rate": 15.4,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 700,
            "monthly_groceries": 400,
            "monthly_transport": 50,
            "monthly_utilities": 150,
            "avg_monthly_salary_net": 800,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "The Maldives is the lowest-lying country in the world, with a maximum elevation of just 2.4 metres.",
            "It is the smallest Asian country by land area and one of the most geographically dispersed.",
            "Tourism accounts for about 28% of GDP and employs about 60% of the workforce.",
        ],
    },

    "NPL": {
        "name": "Nepal",
        "capital": "Kathmandu",
        "population": "30 million",
        "area_km2": 147_181,
        "languages": ["Nepali"],
        "history": (
            "Nepal was never colonised by European powers, maintaining independence through "
            "savvy diplomacy and its formidable Himalayan terrain. The Shah dynasty unified "
            "Nepal in 1768 under Prithvi Narayan Shah. A constitutional monarchy was introduced "
            "in 1990 and a brutal Maoist insurgency (1996–2006) ended with a peace deal that "
            "abolished the monarchy in 2008. Nepal is now a federal democratic republic and "
            "home to eight of the world's ten highest mountains, including Everest."
        ),
        "currency": {
            "name": "Nepalese Rupee",
            "code": "NPR",
            "symbol": "रू",
            "approx_usd_rate": 133,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 150,
            "monthly_groceries": 60,
            "monthly_transport": 10,
            "monthly_utilities": 25,
            "avg_monthly_salary_net": 200,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Nepal is home to eight of the world's ten tallest mountains, including Mount Everest.",
            "The Nepali flag is the only national flag in the world that is not rectangular.",
            "Nepal is the birthplace of Siddhartha Gautama (the Buddha), born in Lumbini c. 563 BCE.",
        ],
    },

    "PAK": {
        "name": "Pakistan",
        "capital": "Islamabad",
        "population": "231 million",
        "area_km2": 881_913,
        "languages": ["Urdu", "English", "Punjabi", "Sindhi", "Pashto", "others"],
        "history": (
            "Pakistan was created in 1947 from Muslim-majority regions of British India during "
            "the Partition, which caused one of history's largest mass migrations. Tensions with "
            "India over Kashmir have persisted, leading to three wars. East Pakistan separated "
            "in 1971 to become Bangladesh. Pakistan has experienced alternating civilian and "
            "military governments and developed nuclear weapons by 1998. It remains a pivotal "
            "state in South Asia, grappling with economic challenges, security threats, and "
            "recurring political crises."
        ),
        "currency": {
            "name": "Pakistani Rupee",
            "code": "PKR",
            "symbol": "₨",
            "approx_usd_rate": 278,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 200,
            "monthly_groceries": 100,
            "monthly_transport": 15,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 250,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Pakistan is home to K2, the world's second-highest mountain.",
            "The Indus Valley Civilisation (c. 3300–1300 BCE) flourished in what is now Pakistan.",
            "Pakistan has the world's second-largest salt mine — the Khewra Salt Mine in Punjab.",
        ],
    },

    # ── Central Asia ──────────────────────────────────────────────────────────
    "KAZ": {
        "name": "Kazakhstan",
        "capital": "Astana",
        "population": "19.6 million",
        "area_km2": 2_724_900,
        "languages": ["Kazakh", "Russian"],
        "history": (
            "The Kazakh Khanate was established in the 15th century as a confederation of nomadic "
            "Turkic tribes across the vast Eurasian steppes. Russian expansion absorbed Kazakhstan "
            "in the 18th–19th centuries, and Soviet collectivisation in the 1930s caused a "
            "catastrophic famine that killed around 1.5 million Kazakhs. Kazakhstan declared "
            "independence from the USSR in December 1991. Under President Nursultan Nazarbayev "
            "(1991–2019), oil wealth fuelled rapid economic growth and urban development."
        ),
        "currency": {
            "name": "Kazakhstani Tenge",
            "code": "KZT",
            "symbol": "₸",
            "approx_usd_rate": 450,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 450,
            "monthly_groceries": 150,
            "monthly_transport": 25,
            "monthly_utilities": 60,
            "avg_monthly_salary_net": 700,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Kazakhstan is the world's largest landlocked country by area.",
            "The first human spaceflight (Gagarin, 1961) launched from the Baikonur Cosmodrome in Kazakhstan.",
            "Kazakhstan holds about 40% of the world's uranium reserves.",
        ],
    },

    "KGZ": {
        "name": "Kyrgyz Republic",
        "capital": "Bishkek",
        "population": "6.8 million",
        "area_km2": 199_951,
        "languages": ["Kyrgyz", "Russian"],
        "history": (
            "The Kyrgyz people trace their origins to nomadic tribes of the Yenisei River basin "
            "who migrated to the Tian Shan mountains around the 10th century. The region was "
            "conquered by Mongols in the 13th century and incorporated into the Russian Empire "
            "by the late 19th century. Soviet rule brought collectivisation and sedentarisation "
            "of nomads. After independence in 1991, Kyrgyzstan experienced two 'Tulip Revolutions' "
            "(2005, 2010) and has developed one of Central Asia's more open political systems."
        ),
        "currency": {
            "name": "Kyrgyzstani Som",
            "code": "KGS",
            "symbol": "с",
            "approx_usd_rate": 89,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 100,
            "monthly_transport": 15,
            "monthly_utilities": 40,
            "avg_monthly_salary_net": 300,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "Lake Issyk-Kul in Kyrgyzstan is the second-largest alpine lake in the world and never freezes.",
            "Kyrgyzstan's epic poem Manas — recited by akyns (bards) — is one of the world's longest oral epic poems.",
            "About 40% of Kyrgyzstanis still live in traditional yurts or use them seasonally.",
        ],
    },

    "TJK": {
        "name": "Tajikistan",
        "capital": "Dushanbe",
        "population": "10 million",
        "area_km2": 143_100,
        "languages": ["Tajik (Persian)"],
        "history": (
            "Tajikistan is home to one of the world's oldest civilisations, with the Sogdian "
            "culture flourishing along the Silk Road. The region was conquered by Alexander the "
            "Great, the Persians, and later the Arabs and Mongols. It became a Soviet republic "
            "in 1929, and independence in 1991 was followed by a devastating civil war (1992–97) "
            "that killed tens of thousands. President Emomali Rahmon has ruled since 1994, making "
            "it one of Central Asia's most authoritarian states."
        ),
        "currency": {
            "name": "Tajikistani Somoni",
            "code": "TJS",
            "symbol": "SM",
            "approx_usd_rate": 10.9,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 150,
            "monthly_groceries": 80,
            "monthly_transport": 10,
            "monthly_utilities": 25,
            "avg_monthly_salary_net": 150,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Over 90% of Tajikistan is covered by mountains; it's the most mountainous country in Central Asia.",
            "The Fedchenko Glacier in Tajikistan is the world's longest glacier outside polar regions at 77 km.",
            "Remittances from Tajik migrant workers (mainly in Russia) account for about 30–40% of GDP.",
        ],
    },

    "TKM": {
        "name": "Turkmenistan",
        "capital": "Ashgabat",
        "population": "6.1 million",
        "area_km2": 488_100,
        "languages": ["Turkmen"],
        "history": (
            "The land of modern Turkmenistan was inhabited by Iranian peoples and later conquered "
            "by Persians, Greeks, Parthians, and Mongols. Turkic tribes settled the region in "
            "the 10th–11th centuries. Russia annexed the territory in the 1880s. The Turkmen "
            "Soviet Republic was created in 1924, and independence was declared in 1991. The "
            "country is one of the world's most isolated states, governed by authoritarian "
            "presidents who have cultivated extreme personality cults while sitting atop vast "
            "natural gas reserves."
        ),
        "currency": {
            "name": "Turkmenistani Manat",
            "code": "TMT",
            "symbol": "T",
            "approx_usd_rate": 3.5,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 200,
            "monthly_groceries": 100,
            "monthly_transport": 10,
            "monthly_utilities": 15,
            "avg_monthly_salary_net": 300,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "The 'Door to Hell' in Derweze — a natural gas crater lit on fire by Soviet engineers in 1971 — has been burning ever since.",
            "Turkmenistan has the world's fourth-largest natural gas reserves.",
            "Ashgabat holds several Guinness World Records for its concentration of white marble buildings.",
        ],
    },

    "UZB": {
        "name": "Uzbekistan",
        "capital": "Tashkent",
        "population": "35 million",
        "area_km2": 448_978,
        "languages": ["Uzbek"],
        "history": (
            "Uzbekistan's cities — Samarkand, Bukhara, Khiva — were jewels of the Silk Road, "
            "centres of Islamic learning and trade. Timur (Tamerlane) made Samarkand the capital "
            "of a vast 14th-century empire. The Russian Empire absorbed the region in the 1860s-"
            "1880s. Soviet industrialisation and the Aral Sea irrigation disaster left a complex "
            "legacy. Since independence in 1991, Uzbekistan has gradually opened under President "
            "Shavkat Mirziyoyev, with economic liberalisation and increased regional engagement."
        ),
        "currency": {
            "name": "Uzbekistani Som",
            "code": "UZS",
            "symbol": "сўм",
            "approx_usd_rate": 12_700,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 250,
            "monthly_groceries": 100,
            "monthly_transport": 15,
            "monthly_utilities": 30,
            "avg_monthly_salary_net": 350,
            "meal_cheap_restaurant": 1.5,
        },
        "fun_facts": [
            "Uzbekistan's Samarkand is one of the world's oldest continuously inhabited cities.",
            "The country is a double-landlocked nation — surrounded only by other landlocked countries.",
            "Uzbekistan is one of the world's largest exporters of cotton and gold.",
        ],
    },

    # ── West Asia / Middle East ───────────────────────────────────────────────
    "ARE": {
        "name": "United Arab Emirates",
        "capital": "Abu Dhabi",
        "population": "10 million",
        "area_km2": 83_600,
        "languages": ["Arabic", "English (widely used)"],
        "history": (
            "The UAE's coastal communities were known to the British as the 'Trucial States' — "
            "sheikdoms that signed treaties suppressing piracy and the slave trade in the 19th "
            "century. A federation of seven emirates was formed at independence in 1971. "
            "The discovery and export of oil from the 1950s onwards financed a remarkable "
            "transformation of desert into gleaming cities. Under Crown Prince Mohammed bin "
            "Zayed, the UAE has diversified into finance, tourism, aviation, and tech, becoming "
            "the Middle East's most cosmopolitan hub."
        ),
        "currency": {
            "name": "UAE Dirham",
            "code": "AED",
            "symbol": "د.إ",
            "approx_usd_rate": 3.67,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 1_800,
            "monthly_groceries": 350,
            "monthly_transport": 100,
            "monthly_utilities": 200,
            "avg_monthly_salary_net": 2_500,
            "meal_cheap_restaurant": 6,
        },
        "fun_facts": [
            "Dubai's Burj Khalifa is the world's tallest building at 828 metres.",
            "About 88% of the UAE's population are foreign nationals (expatriates).",
            "The UAE has one of the world's highest per-capita carbon footprints.",
        ],
    },

    "ARM": {
        "name": "Armenia",
        "capital": "Yerevan",
        "population": "3 million",
        "area_km2": 29_743,
        "languages": ["Armenian"],
        "history": (
            "Armenia is home to one of the world's oldest civilisations and was the first nation "
            "to adopt Christianity as a state religion (301 CE). The Armenian Apostolic Church "
            "remains central to national identity. Between 1915 and 1923, the Ottoman government "
            "carried out the Armenian Genocide, killing an estimated 1–1.5 million Armenians. "
            "After a Soviet period and independence in 1991, Armenia fought two wars with "
            "Azerbaijan over Nagorno-Karabakh (1991–94 and 2020), losing the region in 2023."
        ),
        "currency": {
            "name": "Armenian Dram",
            "code": "AMD",
            "symbol": "֏",
            "approx_usd_rate": 400,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 150,
            "monthly_transport": 25,
            "monthly_utilities": 60,
            "avg_monthly_salary_net": 500,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Armenia was the world's first Christian nation, adopting the faith as state religion in 301 CE.",
            "The apricot is believed to have originated in Armenia — it's called 'Armenian plum' in many languages.",
            "Yerevan is one of the world's oldest continuously inhabited cities, founded in 782 BCE.",
        ],
    },

    "AZE": {
        "name": "Azerbaijan",
        "capital": "Baku",
        "population": "10.4 million",
        "area_km2": 86_600,
        "languages": ["Azerbaijani (Azeri)"],
        "history": (
            "Azerbaijan sits at the ancient crossroads of the Silk Road and was the world's first "
            "commercial oil producer — wells were drilled in Baku in 1846. The region was part "
            "of the Persian Empire, then the Russian Empire, and briefly an independent republic "
            "(1918–20) before Soviet incorporation. Since independence in 1991, oil revenues have "
            "funded dramatic modernisation of Baku. The country fought two wars over Nagorno-"
            "Karabakh with Armenia, ultimately regaining full control in 2023."
        ),
        "currency": {
            "name": "Azerbaijani Manat",
            "code": "AZN",
            "symbol": "₼",
            "approx_usd_rate": 1.7,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 350,
            "monthly_groceries": 150,
            "monthly_transport": 20,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 450,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Azerbaijan drilled the world's first industrial oil well in Baku in 1846.",
            "The country has more mud volcanoes than anywhere else on Earth — about 400.",
            "Baku's Old City (İçərişəhər) is a UNESCO World Heritage Site.",
        ],
    },

    "BHR": {
        "name": "Bahrain",
        "capital": "Manama",
        "population": "1.5 million",
        "area_km2": 765,
        "languages": ["Arabic"],
        "history": (
            "Bahrain's islands have been inhabited for over 5,000 years and were home to the "
            "ancient Dilmun civilisation, a major Bronze Age trading hub. The island was "
            "controlled successively by the Portuguese, Persians, and Omani Arabs before the "
            "Al Khalifa dynasty established rule in 1783. Bahrain became a British protectorate "
            "in 1820 and gained independence in 1971. The country was the first Gulf state to "
            "discover oil (1931) and has since diversified into finance and tourism."
        ),
        "currency": {
            "name": "Bahraini Dinar",
            "code": "BHD",
            "symbol": "BD",
            "approx_usd_rate": 0.376,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 900,
            "monthly_groceries": 300,
            "monthly_transport": 100,
            "monthly_utilities": 150,
            "avg_monthly_salary_net": 1_800,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "Bahrain was the first Gulf state to discover oil, in 1931.",
            "The country is connected to Saudi Arabia by the 25 km King Fahd Causeway.",
            "Bahrain's pearling industry was historically one of the world's finest, long before oil.",
        ],
    },

    "GEO": {
        "name": "Georgia",
        "capital": "Tbilisi",
        "population": "3.7 million",
        "area_km2": 69_700,
        "languages": ["Georgian"],
        "history": (
            "Georgia is one of the world's oldest wine-producing regions, with viticulture dating "
            "back 8,000 years. The Kingdom of Georgia reached its Golden Age under Queen Tamar "
            "(1184–1213). The country was absorbed into the Russian Empire in the 19th century "
            "and was briefly independent (1918–21) before Soviet annexation. Since independence "
            "in 1991, Georgia has pursued pro-Western reforms, but conflict with Russia over "
            "South Ossetia and Abkhazia continues to shape its geopolitics."
        ),
        "currency": {
            "name": "Georgian Lari",
            "code": "GEL",
            "symbol": "₾",
            "approx_usd_rate": 2.7,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 450,
            "monthly_groceries": 180,
            "monthly_transport": 25,
            "monthly_utilities": 70,
            "avg_monthly_salary_net": 600,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Georgia has been making wine for 8,000 years, the oldest winemaking tradition in the world.",
            "The Georgian script (Mkhedruli) is one of the world's 14 unique alphabets.",
            "Georgia has over 12,000 churches and monasteries — one of the highest concentrations in the world.",
        ],
    },

    "IRN": {
        "name": "Iran",
        "capital": "Tehran",
        "population": "87 million",
        "area_km2": 1_648_195,
        "languages": ["Persian (Farsi)"],
        "history": (
            "Persia — modern-day Iran — is home to one of the world's oldest and greatest "
            "civilisations, including the Achaemenid Empire (the world's first 'superpower'), "
            "the Sassanid Empire, and a rich tradition of poetry, science, and art. Arab conquest "
            "in the 7th century brought Islam, and Persia eventually adopted Shia Islam as a "
            "distinct identity. The 1979 Islamic Revolution overthrew the Shah and established "
            "an Islamic Republic under Ayatollah Khomeini. Iran has since faced international "
            "sanctions due to its nuclear programme."
        ),
        "currency": {
            "name": "Iranian Rial",
            "code": "IRR",
            "symbol": "﷼",
            "approx_usd_rate": 42_000,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 300,
            "monthly_groceries": 100,
            "monthly_transport": 20,
            "monthly_utilities": 20,
            "avg_monthly_salary_net": 250,
            "meal_cheap_restaurant": 2,
        },
        "fun_facts": [
            "Iran has 27 UNESCO World Heritage Sites, among the most in the world.",
            "Persia invented the world's first postal system under Cyrus the Great.",
            "Iran produces about 25% of the world's pistachios and is the largest saffron producer.",
        ],
    },

    "IRQ": {
        "name": "Iraq",
        "capital": "Baghdad",
        "population": "43 million",
        "area_km2": 438_317,
        "languages": ["Arabic", "Kurdish"],
        "history": (
            "Mesopotamia — modern Iraq — is the cradle of civilisation, where the Sumerians "
            "invented writing around 3100 BCE and the world's first cities arose. The region was "
            "controlled by Babylonians, Assyrians, Persians, and Ottomans. Iraq was carved out "
            "of the Ottoman Empire after WWI under British mandate and became independent in "
            "1932. Saddam Hussein's Ba'athist regime ruled from 1979 to 2003, when the US-led "
            "invasion toppled it. The country continues to rebuild after years of conflict, "
            "including ISIS occupation (2013–2017)."
        ),
        "currency": {
            "name": "Iraqi Dinar",
            "code": "IQD",
            "symbol": "ع.د",
            "approx_usd_rate": 1_310,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 350,
            "monthly_groceries": 200,
            "monthly_transport": 30,
            "monthly_utilities": 50,
            "avg_monthly_salary_net": 500,
            "meal_cheap_restaurant": 3,
        },
        "fun_facts": [
            "Iraq ('Mesopotamia') is where writing was invented by the Sumerians around 3100 BCE.",
            "Iraq holds the world's fifth-largest proven oil reserves.",
            "The Tigris and Euphrates rivers, which flow through Iraq, are central to multiple creation myths.",
        ],
    },

    "ISR": {
        "name": "Israel",
        "capital": "Jerusalem (disputed; Tel Aviv is the diplomatic capital for most countries)",
        "population": "9.8 million",
        "area_km2": 20_770,
        "languages": ["Hebrew", "Arabic"],
        "history": (
            "Israel's land has been central to the monotheistic religions of Judaism, Christianity, "
            "and Islam for millennia. After centuries of Ottoman rule, the British Mandate for "
            "Palestine was established after WWI, during which the Balfour Declaration promised "
            "a Jewish homeland. Israel declared independence in 1948, triggering a war with "
            "neighbouring Arab states. The country has fought multiple wars and continues in a "
            "complex conflict with Palestinians over statehood. Despite security challenges, "
            "Israel has built a highly innovative 'Start-up Nation' economy."
        ),
        "currency": {
            "name": "Israeli New Shekel",
            "code": "ILS",
            "symbol": "₪",
            "approx_usd_rate": 3.7,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 1_600,
            "monthly_groceries": 500,
            "monthly_transport": 100,
            "monthly_utilities": 180,
            "avg_monthly_salary_net": 3_500,
            "meal_cheap_restaurant": 10,
        },
        "fun_facts": [
            "Israel has the highest density of start-up companies per capita in the world.",
            "The Dead Sea is the world's saltiest sea (34% salinity) and the lowest point on Earth.",
            "Israel is the only country in the world whose population has grown by a factor of ten since independence.",
        ],
    },

    "JOR": {
        "name": "Jordan",
        "capital": "Amman",
        "population": "10.8 million",
        "area_km2": 89_342,
        "languages": ["Arabic"],
        "history": (
            "Jordan's land encompasses ancient civilisations — the Nabataeans built Petra, the "
            "'Rose City,' around the 4th century BCE. The region passed through Roman, Byzantine, "
            "and Ottoman hands before Britain created Transjordan after WWI. Independence came "
            "in 1946 and the Hashemite Kingdom of Jordan was established. Jordan has remained "
            "relatively stable under the Hashemite monarchy, hosting millions of Palestinian and "
            "Syrian refugees, and maintaining diplomatic relations with both Israel and Arab states."
        ),
        "currency": {
            "name": "Jordanian Dinar",
            "code": "JOD",
            "symbol": "JD",
            "approx_usd_rate": 0.71,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 450,
            "monthly_groceries": 200,
            "monthly_transport": 40,
            "monthly_utilities": 80,
            "avg_monthly_salary_net": 700,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Petra — the ancient Nabataean city carved into rose-red rock — is one of the New Seven Wonders of the World.",
            "Jordan hosts one of the world's highest per-capita refugee populations relative to its size.",
            "The Dead Sea coastline within Jordan is the lowest dry land point on Earth (−430 m).",
        ],
    },

    "KWT": {
        "name": "Kuwait",
        "capital": "Kuwait City",
        "population": "4.6 million",
        "area_km2": 17_818,
        "languages": ["Arabic"],
        "history": (
            "Kuwait was settled by Arabian tribes in the early 18th century and became a British "
            "protectorate in 1899 to resist Ottoman pressure. Oil was discovered in 1938, "
            "transforming a pearl-diving economy into one of the world's wealthiest per-capita "
            "states. Kuwait gained independence in 1961. Iraq's 1990 invasion and occupation "
            "ended with the Gulf War in 1991, during which a US-led coalition liberated the "
            "country. Kuwait remains a constitutional emirate with one of the world's largest "
            "sovereign wealth funds."
        ),
        "currency": {
            "name": "Kuwaiti Dinar",
            "code": "KWD",
            "symbol": "KD",
            "approx_usd_rate": 0.307,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 900,
            "monthly_groceries": 300,
            "monthly_transport": 100,
            "monthly_utilities": 80,
            "avg_monthly_salary_net": 2_200,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "The Kuwaiti Dinar is the world's most valuable currency unit.",
            "Kuwait has no income tax for individuals.",
            "Kuwait's oil reserves account for about 8% of the world's total proven reserves.",
        ],
    },

    "LBN": {
        "name": "Lebanon",
        "capital": "Beirut",
        "population": "5.5 million",
        "area_km2": 10_452,
        "languages": ["Arabic", "French", "English"],
        "history": (
            "Lebanon is home to the ancient Phoenician civilisation, which spread the alphabet "
            "across the Mediterranean. After Ottoman and then French mandate rule, Lebanon "
            "became independent in 1943. A fifteen-year civil war (1975–1990) devastated the "
            "country. A brief reconstruction period ended with continued political paralysis, "
            "Hezbollah's growing power, Syrian influence, and the devastating August 2020 "
            "Beirut port explosion. Lebanon entered one of the world's worst economic collapses "
            "in modern history, with hyperinflation and banking system failure from 2019."
        ),
        "currency": {
            "name": "Lebanese Pound",
            "code": "LBP",
            "symbol": "ل.ل",
            "approx_usd_rate": 89_500,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 200,
            "monthly_transport": 30,
            "monthly_utilities": 100,
            "avg_monthly_salary_net": 200,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "Lebanon has the world's highest concentration of banks per square kilometre.",
            "Beirut was historically called the 'Paris of the Middle East'.",
            "The Cedars of Lebanon were prized by the ancient Egyptians and Phoenicians for shipbuilding.",
        ],
    },

    "OMN": {
        "name": "Oman",
        "capital": "Muscat",
        "population": "4.9 million",
        "area_km2": 309_500,
        "languages": ["Arabic"],
        "history": (
            "Oman has a maritime tradition stretching back millennia and was once the hub of "
            "an Indian Ocean trading empire. The Al Busaid dynasty has ruled Oman since 1744 "
            "and also governed Zanzibar for over a century. Oman was a British protectorate "
            "from 1891 until 1971, when Sultan Qaboos bin Said came to power through a palace "
            "coup and initiated rapid modernisation using oil revenues. Oman is known for its "
            "balanced foreign policy and regional neutrality."
        ),
        "currency": {
            "name": "Omani Rial",
            "code": "OMR",
            "symbol": "﷼",
            "approx_usd_rate": 0.385,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 600,
            "monthly_groceries": 250,
            "monthly_transport": 80,
            "monthly_utilities": 100,
            "avg_monthly_salary_net": 1_200,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Oman is one of the oldest independent states in the Arab world.",
            "Dhow sailing vessels — built in Oman for thousands of years — were the backbone of ancient Indian Ocean trade.",
            "Oman's Wahiba Sands dune field has sand dunes that reach over 100 metres.",
        ],
    },

    "PSE": {
        "name": "West Bank & Gaza",
        "capital": "Ramallah (de facto West Bank administrative centre)",
        "population": "5.5 million",
        "area_km2": 6_020,
        "languages": ["Arabic"],
        "history": (
            "The Palestinian territories — the West Bank and the Gaza Strip — are part of historic "
            "Palestine, the birthplace of Judaism and Christianity. After the 1948 Arab-Israeli "
            "War, these areas were controlled by Jordan and Egypt respectively until Israel "
            "occupied both in the 1967 Six-Day War. The Palestinian Authority was established "
            "through the 1993 Oslo Accords, but a Hamas takeover of Gaza in 2007 created a "
            "political split. The ongoing conflict, blockade of Gaza, and West Bank settlement "
            "expansion remain deeply contested international issues."
        ),
        "currency": {
            "name": "Israeli New Shekel (and Jordanian Dinar in West Bank)",
            "code": "ILS",
            "symbol": "₪",
            "approx_usd_rate": 3.7,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 400,
            "monthly_groceries": 250,
            "monthly_transport": 30,
            "monthly_utilities": 100,
            "avg_monthly_salary_net": 600,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Palestine is the birthplace of the world's three major Abrahamic religions.",
            "Jericho, in the West Bank, is considered one of the oldest continuously inhabited cities on Earth.",
            "Gaza has one of the world's highest population densities.",
        ],
    },

    "QAT": {
        "name": "Qatar",
        "capital": "Doha",
        "population": "2.9 million",
        "area_km2": 11_586,
        "languages": ["Arabic"],
        "history": (
            "Qatar was a sparsely populated pearl-diving peninsula under Ottoman and then British "
            "influence before gaining independence in 1971. The discovery of massive natural gas "
            "reserves transformed Qatar into one of the world's wealthiest nations per capita. "
            "Emir Hamad bin Khalifa Al Thani (1995–2013) modernised the country rapidly, "
            "launching Al Jazeera and winning the 2022 FIFA World Cup hosting rights. Qatar plays "
            "an active diplomatic role in the region and manages a vast sovereign wealth fund."
        ),
        "currency": {
            "name": "Qatari Riyal",
            "code": "QAR",
            "symbol": "﷼",
            "approx_usd_rate": 3.64,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 1_400,
            "monthly_groceries": 350,
            "monthly_transport": 150,
            "monthly_utilities": 200,
            "avg_monthly_salary_net": 3_000,
            "meal_cheap_restaurant": 5,
        },
        "fun_facts": [
            "Qatar has the world's highest GDP per capita (PPP) among Middle Eastern countries.",
            "Qatar hosts the largest US military base in the Middle East — Al Udeid Air Base.",
            "Approximately 88% of Qatar's population are foreign nationals.",
        ],
    },

    "SAU": {
        "name": "Saudi Arabia",
        "capital": "Riyadh",
        "population": "36 million",
        "area_km2": 2_149_690,
        "languages": ["Arabic"],
        "history": (
            "The Arabian Peninsula is the birthplace of Islam. Muhammad ibn Abd al-Wahhab's "
            "18th-century religious reform movement allied with the Al Saud dynasty to establish "
            "the first Saudi state. Modern Saudi Arabia was unified by King Abdulaziz (Ibn Saud) "
            "in 1932. Oil, discovered in 1938, made the kingdom the world's largest exporter "
            "and a global power. Crown Prince Mohammed bin Salman's Vision 2030 reform agenda "
            "is diversifying the economy and cautiously liberalising society."
        ),
        "currency": {
            "name": "Saudi Riyal",
            "code": "SAR",
            "symbol": "﷼",
            "approx_usd_rate": 3.75,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 700,
            "monthly_groceries": 300,
            "monthly_transport": 100,
            "monthly_utilities": 100,
            "avg_monthly_salary_net": 1_500,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Saudi Arabia is the birthplace of Islam and home to Mecca and Medina — the two holiest cities in Islam.",
            "The country sits atop about 17% of the world's proven petroleum reserves.",
            "Saudi Arabia is building NEOM — a futuristic 170 km linear smart city in the Tabuk region.",
        ],
    },

    "SYR": {
        "name": "Syrian Arab Republic",
        "capital": "Damascus",
        "population": "21 million (pre-war; millions displaced)",
        "area_km2": 185_180,
        "languages": ["Arabic"],
        "history": (
            "Damascus is one of the world's oldest continuously inhabited cities, with roots "
            "stretching back over 10,000 years, and served as the capital of the Umayyad Caliphate. "
            "Syria was part of the Ottoman Empire and then a French mandate before independence "
            "in 1946. The Assad family has ruled since 1971. A 2011 Arab Spring-inspired uprising "
            "became a devastating civil war involving the government, rebel factions, ISIS, Kurdish "
            "forces, and foreign powers, displacing over half the population and killing hundreds "
            "of thousands. Following the fall of the Assad regime in late 2024, Syria entered a "
            "new transitional phase."
        ),
        "currency": {
            "name": "Syrian Pound",
            "code": "SYP",
            "symbol": "£S",
            "approx_usd_rate": 13_000,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 100,
            "monthly_groceries": 80,
            "monthly_transport": 10,
            "monthly_utilities": 20,
            "avg_monthly_salary_net": 50,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Damascus is one of the oldest continuously inhabited cities in the world.",
            "Syria's ancient ruins include Palmyra, Aleppo, and Apamea — all on the UNESCO World Heritage list.",
            "The Syrian civil war created the world's largest refugee crisis of the 21st century.",
        ],
    },

    "TUR": {
        "name": "Türkiye",
        "capital": "Ankara",
        "population": "85 million",
        "area_km2": 783_356,
        "languages": ["Turkish"],
        "history": (
            "Anatolia (Turkey) has been the cradle of civilisations for 10,000 years — from the "
            "Hittites and Phrygians to the Greek cities and the Byzantine Empire centred on "
            "Constantinople. The Ottoman Empire (1299–1923) dominated vast swathes of three "
            "continents. After WWI defeat, Mustafa Kemal Atatürk founded the modern secular "
            "Turkish Republic in 1923. Turkey joined NATO in 1952 and has been a EU membership "
            "candidate since 1987, while pursuing an increasingly independent foreign policy "
            "under President Recep Tayyip Erdoğan."
        ),
        "currency": {
            "name": "Turkish Lira",
            "code": "TRY",
            "symbol": "₺",
            "approx_usd_rate": 32,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 500,
            "monthly_groceries": 200,
            "monthly_transport": 35,
            "monthly_utilities": 100,
            "avg_monthly_salary_net": 700,
            "meal_cheap_restaurant": 4,
        },
        "fun_facts": [
            "Turkey is the only country in the world that straddles two continents — Europe and Asia.",
            "Istanbul is the world's only city on two continents.",
            "Turkey is the world's largest producer of hazelnuts, supplying about 70% of global output.",
        ],
    },

    "YEM": {
        "name": "Yemen",
        "capital": "Sanaa (contested; Aden is temporary seat of internationally recognised government)",
        "population": "33 million",
        "area_km2": 527_968,
        "languages": ["Arabic"],
        "history": (
            "Yemen was home to the ancient Sabaean Kingdom and the fabled Queen of Sheba, and "
            "was historically known as 'Arabia Felix' (Fortunate Arabia) for its fertile highlands "
            "and spice trade. North and South Yemen unified in 1990 after decades of British "
            "colonisation in the south and various monarchies in the north. A 2011 Arab Spring "
            "uprising led to President Saleh's removal, but civil war broke out in 2014–15 when "
            "Houthi forces took the capital. A Saudi-led coalition intervened in 2015, and the "
            "conflict has created one of the world's worst humanitarian crises."
        ),
        "currency": {
            "name": "Yemeni Rial",
            "code": "YER",
            "symbol": "﷼",
            "approx_usd_rate": 530,
        },
        "cost_of_living": {
            "monthly_rent_city_1br": 100,
            "monthly_groceries": 80,
            "monthly_transport": 10,
            "monthly_utilities": 15,
            "avg_monthly_salary_net": 50,
            "meal_cheap_restaurant": 1,
        },
        "fun_facts": [
            "Yemen's Socotra Island is so biologically unique it has been called the 'Galápagos of the Indian Ocean'.",
            "Sanaa's Old City is a UNESCO World Heritage Site featuring unique multi-storey tower houses.",
            "Coffee cultivation is believed to have originated in Yemen, where it was first consumed as a drink.",
        ],
    },
}


def get_profile(iso3: str) -> dict | None:
    """Return the country profile for the given ISO3 code, or None if not found."""
    return COUNTRY_PROFILES.get(iso3.upper())


def get_col_labels() -> dict[str, str]:
    """Human-readable labels for cost-of-living cost keys."""
    return {
        "monthly_rent_city_1br": "Rent – 1BR City Centre",
        "monthly_groceries": "Monthly Groceries",
        "monthly_transport": "Monthly Transport Pass",
        "monthly_utilities": "Monthly Utilities",
        "avg_monthly_salary_net": "Avg Net Monthly Salary",
        "meal_cheap_restaurant": "Cheap Restaurant Meal",
    }
