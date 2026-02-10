"""
Grade-Worthy Card Reference Database

This is compiled from market knowledge - sets and card types that are KNOWN to have
significant value when graded PSA 9/10 vs raw.

The key insight: You don't need to check every card. You need to know which CATEGORIES
of cards to set aside. This tells you what to look for.

Structure:
- HIGH_VALUE_SETS: Sets where virtually any card can be worth grading
- KEY_ROOKIES_BY_YEAR: Which rookie years to pay attention to
- ALWAYS_CHECK_PLAYERS: Players whose cards are almost always worth checking
- VALUABLE_INSERTS: Insert sets that carry premiums
- SET_TIERS: Categorization of sets by typical value
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

# ========================================
# TIER 1: ALWAYS CHECK THESE SETS
# Any card from these sets in good condition is potentially worth grading
# ========================================

TIER1_ALWAYS_GRADE = {
    # Basketball - The Big Sets
    "1986 Fleer Basketball": {"sport": "basketball", "year": 1986, "notes": "THE set. Jordan RC. Any card $100+ graded."},
    "1986 Fleer Stickers": {"sport": "basketball", "year": 1986, "notes": "Jordan sticker is huge"},
    "1996 Topps Chrome Basketball": {"sport": "basketball", "year": 1996, "notes": "Kobe RC year. Refractors are gold"},
    "1997 Topps Chrome Basketball": {"sport": "basketball", "year": 1997, "notes": "Duncan, TMac RCs"},
    "2003 Topps Chrome Basketball": {"sport": "basketball", "year": 2003, "notes": "LeBron RC year - ALL cards valuable"},
    "2003 Bowman Chrome Basketball": {"sport": "basketball", "year": 2003, "notes": "LeBron autos especially"},
    "2009 Topps Chrome Basketball": {"sport": "basketball", "year": 2009, "notes": "Curry, Harden RCs"},
    "2018 Prizm Basketball": {"sport": "basketball", "year": 2018, "notes": "Luka, Trae. Silver Prizms huge"},
    "2019 Prizm Basketball": {"sport": "basketball", "year": 2019, "notes": "Zion, Ja Morant"},
    "2020 Prizm Basketball": {"sport": "basketball", "year": 2020, "notes": "LaMelo, Edwards"},
    
    # Baseball - Key Sets
    "1952 Topps Baseball": {"sport": "baseball", "year": 1952, "notes": "Mantle year. ANY high number valuable"},
    "1989 Upper Deck Baseball": {"sport": "baseball", "year": 1989, "notes": "Griffey #1 is the key"},
    "1993 SP Baseball": {"sport": "baseball", "year": 1993, "notes": "Jeter RC foil - the one to find"},
    "2011 Topps Update Baseball": {"sport": "baseball", "year": 2011, "notes": "Trout RC - US175"},
    "2018 Topps Update Baseball": {"sport": "baseball", "year": 2018, "notes": "Ohtani, Soto, Acuna RCs"},
    
    # Football - Key Sets
    "2000 Playoff Contenders Football": {"sport": "football", "year": 2000, "notes": "Tom Brady auto RC - grail card"},
    "2000 Bowman Chrome Football": {"sport": "football", "year": 2000, "notes": "Brady RC"},
    "2017 Prizm Football": {"sport": "football", "year": 2017, "notes": "Mahomes year - silvers are huge"},
    "2020 Prizm Football": {"sport": "football", "year": 2020, "notes": "Burrow, Herbert year"},
    
    # Hockey
    "1979 O-Pee-Chee Hockey": {"sport": "hockey", "year": 1979, "notes": "Gretzky RC"},
    "1979 Topps Hockey": {"sport": "hockey", "year": 1979, "notes": "Gretzky RC - less valuable than OPC"},
    "2005 Upper Deck Young Guns Hockey": {"sport": "hockey", "year": 2005, "notes": "Crosby, Ovechkin"},
    "2015 Upper Deck Young Guns Hockey": {"sport": "hockey", "year": 2015, "notes": "McDavid"},
}

# ========================================
# TIER 2: CHECK THESE SETS FOR KEY CARDS
# Not every card is valuable, but RCs and stars are
# ========================================

TIER2_CHECK_KEYS = {
    # Basketball Chrome/Prizm Years
    "1996 Finest Basketball": {"sport": "basketball", "year": 1996, "key_cards": "Kobe RC, refractors"},
    "1996 Flair Showcase Basketball": {"sport": "basketball", "year": 1996, "key_cards": "Kobe Row 0,1,2"},
    "1997 Finest Basketball": {"sport": "basketball", "year": 1997, "key_cards": "Duncan, refractors"},
    "1998 Topps Chrome Basketball": {"sport": "basketball", "year": 1998, "key_cards": "Dirk, Pierce, Carter RCs"},
    "2007 Topps Chrome Basketball": {"sport": "basketball", "year": 2007, "key_cards": "Durant RC"},
    "2012 Prizm Basketball": {"sport": "basketball", "year": 2012, "key_cards": "First Prizm year! Kyrie, AD"},
    "2013 Prizm Basketball": {"sport": "basketball", "year": 2013, "key_cards": "Giannis RC!"},
    "2017 Donruss Optic Basketball": {"sport": "basketball", "year": 2017, "key_cards": "Same class as Prizm"},
    
    # Modern Football
    "2005 Topps Chrome Football": {"sport": "football", "year": 2005, "key_cards": "Aaron Rodgers RC"},
    "2012 Topps Chrome Football": {"sport": "football", "year": 2012, "key_cards": "Luck, RG3, Wilson"},
    "2018 Prizm Football": {"sport": "football", "year": 2018, "key_cards": "Josh Allen, Lamar, Baker"},
    "2021 Prizm Football": {"sport": "football", "year": 2021, "key_cards": "Trevor Lawrence, Mac Jones"},
    
    # Baseball Modern
    "2001 Bowman Chrome Baseball": {"sport": "baseball", "year": 2001, "key_cards": "Ichiro, Pujols"},
    "2019 Bowman Chrome Baseball": {"sport": "baseball", "year": 2019, "key_cards": "Wander Franco prospect"},
    "2020 Bowman Chrome Baseball": {"sport": "baseball", "year": 2020, "key_cards": "Jasson Dominguez"},
}

# ========================================
# PLAYERS TO ALWAYS CHECK
# If you see these names, look up the card
# ========================================

ALWAYS_CHECK_PLAYERS = {
    "basketball": [
        # Modern Superstars
        "Michael Jordan", "LeBron James", "Kobe Bryant", "Stephen Curry",
        "Luka Doncic", "Giannis Antetokounmpo", "Zion Williamson", "Ja Morant",
        "Victor Wembanyama", "Anthony Edwards", "Kevin Durant", "Shaquille O'Neal",
        "Magic Johnson", "Larry Bird", "Kareem Abdul-Jabbar", "Tim Duncan",
        "Allen Iverson", "Jason Kidd", "Vince Carter", "Tracy McGrady",
        # JUNK WAX ERA NBA (1986-1994) - HOFers & Stars
        "David Robinson", "Hakeem Olajuwon", "Charles Barkley", "John Stockton",
        "Karl Malone", "Patrick Ewing", "Scottie Pippen", "Clyde Drexler",
        "Gary Payton", "Dikembe Mutombo", "Alonzo Mourning", "Larry Johnson",
        "Derrick Coleman", "Tim Hardaway", "Reggie Miller", "Chris Mullin",
        "Dennis Rodman", "Dominique Wilkins", "Isiah Thomas", "Joe Dumars",
        "James Worthy", "Robert Parish", "Kevin McHale", "Drazen Petrovic",
        "Shawn Kemp", "Mitch Richmond", "Glen Rice", "Kevin Johnson",
        "Mark Price", "Dan Majerle", "Harold Miner", "Christian Laettner",
        "Anfernee Hardaway", "Jamal Mashburn", "Chris Webber", "Vin Baker",
        # More 80s-90s NBA
        "Bill Walton", "Moses Malone", "Julius Erving", "George Gervin",
        "Adrian Dantley", "Alex English", "Bernard King", "World B Free",
        "Sidney Moncrief", "Marques Johnson", "Jack Sikma", "Dennis Johnson",
        "Maurice Cheeks", "Andrew Toney", "Bobby Jones", "Caldwell Jones",
        "Buck Williams", "Otis Thorpe", "Charles Oakley", "Xavier McDaniel",
        "Terry Cummings", "Tom Chambers", "Detlef Schrempf", "Dale Ellis",
        "Ricky Pierce", "Rolando Blackman", "Derek Harper", "Fat Lever",
        "Lafayette Lever", "Michael Adams", "Muggsy Bogues", "Spud Webb",
        "Manute Bol", "Tree Rollins", "Mark Eaton", "Alvin Robertson",
        "Ron Harper", "Danny Manning", "Pervis Ellison", "J.R. Reid",
        "Sean Elliott", "Stacey King", "Lionel Simmons", "Dennis Scott",
        "Kendall Gill", "Steve Smith", "Billy Owens", "Doug Smith",
        "Terrell Brandon", "Nick Anderson", "Pooh Richardson", "Kenny Anderson",
        "Walt Williams", "Tom Gugliotta", "Clarence Weatherspoon", "Harold Ellis",
        "Latrell Sprewell", "Allan Houston", "Dino Radja", "Toni Kukoc",
        "Arvydas Sabonis", "Sarunas Marciulionis", "Vlade Divac", "Rik Smits",
        "Brad Daugherty", "Mark Jackson", "John Starks", "Anthony Mason",
        "Derek Fisher", "Eddie Jones", "Nick Van Exel", "Cedric Ceballos",
        "Juwan Howard", "Rasheed Wallace", "Jerry Stackhouse", "Joe Smith",
        "Antonio McDyess", "Kevin Garnett", "Damon Stoudamire", "Michael Finley",
        "Grant Hill", "Jason Williams", "Stephon Marbury", "Ray Allen",
        "Shareef Abdur-Rahim", "Antoine Walker", "Chauncey Billups", "Keith Van Horn",
    ],
    "baseball": [
        # Modern Stars
        "Mike Trout", "Shohei Ohtani", "Juan Soto", "Ronald Acuna Jr",
        "Derek Jeter", "Ken Griffey Jr", "Mickey Mantle", "Babe Ruth",
        "Jackie Robinson", "Willie Mays", "Nolan Ryan", "Cal Ripken Jr",
        "Hank Aaron", "Roberto Clemente", "Sandy Koufax", "Frank Thomas",
        # JUNK WAX ERA MLB (1986-1994) - HOFers & Stars
        "Barry Bonds", "Mark McGwire", "Jose Canseco", "Bo Jackson",
        "Greg Maddux", "Tom Glavine", "John Smoltz", "Randy Johnson",
        "Roger Clemens", "Kirby Puckett", "Ryne Sandberg", "Ozzie Smith",
        "Don Mattingly", "Darryl Strawberry", "Dwight Gooden", "Wade Boggs",
        "Tony Gwynn", "George Brett", "Robin Yount", "Paul Molitor",
        "Rickey Henderson", "Dave Winfield", "Andre Dawson", "Eric Davis",
        "Will Clark", "Kevin Mitchell", "Juan Gonzalez", "Ivan Rodriguez",
        "Sammy Sosa", "Jeff Bagwell", "Craig Biggio", "Larry Walker",
        "Chipper Jones", "Gary Sheffield", "Fred McGriff", "David Justice",
        "Matt Williams", "John Olerud", "Jim Abbott", "Ben McDonald",
        "Steve Avery", "Todd Van Poppel", "Brien Taylor", "Alex Rodriguez",
        "Manny Ramirez", "Jim Thome", "Edgar Martinez", "Mike Piazza",
        "Bernie Williams", "Moises Alou", "Albert Belle", "Kenny Lofton",
        "Travis Fryman", "Chuck Knoblauch", "Tim Salmon", "Carlos Baerga",
        # More 80s-90s MLB - Pitchers HOFers
        "Dennis Eckersley", "Lee Smith", "Goose Gossage", "Rollie Fingers",
        "Bruce Sutter", "Trevor Hoffman", "John Franco", "Jeff Reardon",
        "Dave Righetti", "Dan Quisenberry", "Orel Hershiser", "David Cone",
        "Bret Saberhagen", "Frank Viola", "Jack Morris", "Dave Stewart",
        "Mark Langston", "Teddy Higuera", "Danny Jackson", "Doug Drabek",
        "Bob Welch", "Kevin Brown", "Andy Benes", "Kevin Appier",
        "David Wells", "Jimmy Key", "Mike Mussina", "Pedro Martinez",
        "Curt Schilling", "Kevin Tapani", "Scott Erickson", "Pat Hentgen",
        # More 80s-90s MLB - Position Players
        "Harold Baines", "Carlton Fisk", "Gary Carter", "Benito Santiago",
        "Sandy Alomar Jr", "Charles Johnson", "Mike Scioscia", "Lance Parrish",
        "Alan Trammell", "Lou Whitaker", "Barry Larkin", "Cal Ripken",
        "Ozzie Guillen", "Tony Fernandez", "Shawon Dunston", "Gary Templeton",
        "Vince Coleman", "Willie McGee", "Lenny Dykstra", "Brett Butler",
        "Devon White", "Marquis Grissom", "Otis Nixon", "Lance Johnson",
        "Roberto Alomar", "Robby Alomar", "Delino DeShields", "Steve Sax",
        "Gregg Jefferies", "Kevin Seitzer", "Carney Lansford", "Terry Pendleton",
        "Howard Johnson", "Bobby Bonilla", "Kevin McReynolds", "Joe Carter",
        "Danny Tartabull", "Ruben Sierra", "Jesse Barfield", "Cory Snyder",
        "Pete Incaviglia", "Rob Deer", "Jay Buhner", "Greg Vaughn",
        "Phil Plantier", "Dean Palmer", "Ryan Klesko", "Cliff Floyd",
        "Raul Mondesi", "Shawn Green", "Todd Hundley", "Mike Lieberthal",
        "John Kruk", "Wally Joyner", "Tino Martinez", "Mo Vaughn",
        "Jim Edmonds", "Ray Lankford", "Brian Jordan", "Reggie Sanders",
        "Marquis Grissom", "Ellis Burks", "Ron Gant", "David Segui",
        "John Valentin", "Nomar Garciaparra", "Scott Rolen", "Sean Casey",
        "Todd Helton", "Carlos Delgado", "Vladimir Guerrero", "Andruw Jones",
    ],
    "football": [
        # Modern Stars
        "Patrick Mahomes", "Josh Allen", "Joe Burrow", "Justin Herbert",
        "Tom Brady", "Peyton Manning", "Aaron Rodgers", "Brett Favre",
        "Joe Montana", "Jerry Rice", "Barry Sanders", "Walter Payton",
        "Lawrence Taylor", "Dan Marino", "John Elway", "Emmitt Smith",
        # JUNK WAX ERA NFL (1989-1994) - HOFers & Stars
        "Troy Aikman", "Steve Young", "Michael Irvin", "Deion Sanders",
        "Reggie White", "Bruce Smith", "Derrick Thomas", "Junior Seau",
        "Cortez Kennedy", "Chris Doleman", "Rod Woodson", "Ronnie Lott",
        "Randall Cunningham", "Warren Moon", "Jim Kelly", "Thurman Thomas",
        "Andre Reed", "Tim Brown", "Andre Rison", "Sterling Sharpe",
        "Cris Carter", "Art Monk", "Gary Clark", "Henry Ellard",
        "Eric Dickerson", "Marcus Allen", "Neal Anderson", "Christian Okoye",
        "Bo Jackson", "Ickey Woods", "Eric Metcalf", "Herschel Walker",
        "Earnest Byner", "Kevin Mack", "Keith Byars", "Roger Craig",
        "Ricky Watters", "Jerome Bettis", "Natrone Means", "Marshall Faulk",
        "Garrison Hearst", "Ki-Jana Carter", "Carl Pickens", "Herman Moore",
        "Rob Moore", "Rocket Ismail", "Desmond Howard", "Raghib Ismail",
        "Drew Bledsoe", "Rick Mirer", "Heath Shuler", "Trent Dilfer",
        "Jeff George", "Dave Brown", "Steve Beuerlein", "Vinny Testaverde",
        # More 80s-90s NFL - HOFers & Pro Bowlers
        "Mike Singletary", "Richard Dent", "Dan Hampton", "Steve McMichael",
        "Kevin Greene", "Charles Haley", "Neil Smith", "Sean Jones",
        "Clyde Simmons", "Seth Joyner", "Andre Waters", "Eric Allen",
        "Darrell Green", "Albert Lewis", "Gill Byrd", "Hanford Dixon",
        "Frank Minnifield", "Bennie Blades", "Mark Carrier", "Steve Atwater",
        "Dennis Smith", "Joey Browner", "David Fulcher", "Tim McDonald",
        "LeRoy Butler", "Eugene Robinson", "Carnell Lake", "Darren Woodson",
        "Hardy Nickerson", "Bryan Cox", "Levon Kirkland", "Chad Brown",
        "Ken Norton Jr", "Wilber Marshall", "Carl Banks", "Pepper Johnson",
        "Pat Swilling", "Rickey Jackson", "Sam Mills", "Vaughan Johnson",
        "Anthony Munoz", "Gary Zimmerman", "Bruce Matthews", "Steve Wisniewski",
        "Randall McDaniel", "Will Shields", "Larry Allen", "Nate Newton",
        "Richmond Webb", "Tony Boselli", "Jonathan Ogden", "Willie Roaf",
        "John Randle", "Warren Sapp", "Dana Stubblefield", "Bryant Young",
        "Ted Washington", "Chester McGlockton", "Ray Childress", "Michael Dean Perry",
        # More 80s-90s NFL - Skill Players
        "Haywood Jeffires", "Anthony Miller", "Webster Slaughter", "Ernest Givins",
        "Drew Hill", "Mark Clayton", "Mark Duper", "Flipper Anderson",
        "Willie Anderson", "Irving Fryar", "Terance Mathis", "Quinn Early",
        "Eric Martin", "Mervyn Fernandez", "Mark Carrier", "Jeff Graham",
        "Alvin Harper", "Kevin Williams", "Jake Reed", "Yancey Thigpen",
        "Keenan McCardell", "Jimmy Smith", "Isaac Bruce", "Torry Holt",
        "Randy Moss", "Terrell Owens", "Marvin Harrison", "Keyshawn Johnson",
        "Eddie George", "Terrell Davis", "Jamal Anderson", "Robert Smith",
        "Curtis Martin", "Corey Dillon", "Fred Taylor", "Edgerrin James",
        "Warrick Dunn", "Dorsey Levens", "Terry Allen", "Errict Rhett",
        "Harvey Williams", "Leonard Russell", "Tommy Vardell", "Leroy Hoard",
        "Craig Heyward", "Merril Hoge", "Marion Butts", "Rodney Hampton",
        "Lewis Tillman", "Johnny Johnson", "Derek Loville", "Charlie Garner",
        # QBs
        "Boomer Esiason", "Phil Simms", "Bernie Kosar", "Mark Rypien",
        "Stan Humphries", "Neil O'Donnell", "Jim Harbaugh", "Erik Kramer",
        "Dave Krieg", "Chris Chandler", "Rich Gannon", "Elvis Grbac",
        "Trent Green", "Brad Johnson", "Kerry Collins", "Tony Banks",
        "Kordell Stewart", "Steve McNair", "Mark Brunell", "Jake Plummer",
    ],
    "hockey": [
        "Wayne Gretzky", "Connor McDavid", "Sidney Crosby", "Alex Ovechkin",
        "Mario Lemieux", "Bobby Orr", "Gordie Howe", "Patrick Roy",
        "Auston Matthews", "Nathan MacKinnon",
        # JUNK WAX ERA NHL (1990-1994) - HOFers
        "Eric Lindros", "Jaromir Jagr", "Pavel Bure", "Sergei Fedorov",
        "Peter Forsberg", "Paul Kariya", "Martin Brodeur", "Ed Belfour",
        "Dominik Hasek", "Brett Hull", "Mark Messier", "Steve Yzerman",
        "Joe Sakic", "Mats Sundin", "Teemu Selanne", "Keith Tkachuk",
        "Jeremy Roenick", "Mike Modano", "Pat LaFontaine", "Adam Oates",
        "Brian Leetch", "Ray Bourque", "Al MacInnis", "Chris Chelios",
        "Scott Stevens", "Nicklas Lidstrom", "Rob Blake", "Chris Pronger",
        # More 80s-90s NHL
        "Doug Gilmour", "Ron Francis", "Dale Hawerchuk", "Denis Savard",
        "Bernie Nicholls", "Pierre Turgeon", "Alexander Mogilny", "Joe Mullen",
        "Luc Robitaille", "Mike Gartner", "Dino Ciccarelli", "Kevin Stevens",
        "Rick Tocchet", "John LeClair", "Mark Recchi", "Dave Andreychuk",
        "Brendan Shanahan", "Owen Nolan", "Keith Primeau", "Rod Brind'Amour",
        "Eric Desjardins", "Sandis Ozolinsh", "Sergei Zubov", "Larry Murphy",
        "Phil Housley", "Gary Suter", "Mathieu Schneider", "Kevin Hatcher",
        "Alexei Zhitnik", "Glen Wesley", "Sylvain Lefebvre", "Uwe Krupp",
        "Curtis Joseph", "Mike Richter", "Felix Potvin", "John Vanbiesbrouck",
        "Tom Barrasso", "Grant Fuhr", "Andy Moog", "Bill Ranford",
        "Arturs Irbe", "Olaf Kolzig", "Nikolai Khabibulin", "Jim Carey",
        "Trevor Kidd", "Daren Puppa", "Tommy Salo", "Mike Vernon",
    ],
    "soccer": [
        "Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappe", "Erling Haaland",
        "Neymar", "Pele", "Maradona", "Jude Bellingham",
    ],
}

# ========================================
# VALUABLE INSERT/PARALLEL KEYWORDS
# If you see these words on a card, check value
# ========================================

VALUABLE_KEYWORDS = [
    # Prizm/Chrome Parallels
    "Silver Prizm", "Gold Prizm", "Green Prizm", "Red Prizm", "Blue Prizm",
    "Refractor", "Xfractor", "Gold Refractor", "Superfractor",
    "Shimmer", "Mojo", "Cracked Ice", "Snakeskin",
    "Auto", "Autograph", "Patch", "RPA", "Rookie Patch Auto",
    
    # Numbered Cards
    "/99", "/75", "/50", "/25", "/10", "/5", "/1",
    "Serial Numbered", "Short Print", "SP", "SSP",
    
    # Premium Inserts
    "Kaboom", "Downtown", "Color Blast", "Case Hit",
    "Net Marvels", "Rookie Ticket", "Contenders",
    
    # Set Names That Command Premium
    "National Treasures", "Flawless", "Immaculate", "Exquisite",
    "Noir", "One and One", "Eminence", "Impeccable",
]

# ========================================
# YEARS TO PAY ATTENTION TO (Rookie Years)
# ========================================

KEY_ROOKIE_YEARS = {
    "basketball": {
        1984: ["Michael Jordan", "Hakeem Olajuwon", "Charles Barkley"],
        1986: ["Michael Jordan (Fleer)"],
        1996: ["Kobe Bryant", "Allen Iverson", "Steve Nash", "Ray Allen"],
        1997: ["Tim Duncan", "Tracy McGrady"],
        1998: ["Dirk Nowitzki", "Vince Carter", "Paul Pierce"],
        2003: ["LeBron James", "Dwyane Wade", "Carmelo Anthony", "Chris Bosh"],
        2007: ["Kevin Durant"],
        2009: ["Stephen Curry", "James Harden", "Blake Griffin"],
        2012: ["Anthony Davis", "Kyrie Irving", "Damian Lillard"],
        2013: ["Giannis Antetokounmpo"],
        2017: ["Jayson Tatum", "Donovan Mitchell", "De'Aaron Fox"],
        2018: ["Luka Doncic", "Trae Young"],
        2019: ["Zion Williamson", "Ja Morant"],
        2020: ["LaMelo Ball", "Anthony Edwards"],
        2023: ["Victor Wembanyama"],
    },
    "football": {
        1998: ["Peyton Manning", "Randy Moss"],
        2000: ["Tom Brady"],
        2005: ["Aaron Rodgers"],
        2012: ["Andrew Luck", "Russell Wilson", "RG3"],
        2017: ["Patrick Mahomes", "Deshaun Watson"],
        2018: ["Josh Allen", "Lamar Jackson", "Baker Mayfield"],
        2020: ["Joe Burrow", "Justin Herbert", "Tua"],
        2021: ["Trevor Lawrence", "Mac Jones", "Justin Fields"],
    },
    "baseball": {
        1989: ["Ken Griffey Jr"],
        1993: ["Derek Jeter"],
        2001: ["Ichiro", "Albert Pujols"],
        2011: ["Mike Trout"],
        2018: ["Shohei Ohtani", "Juan Soto", "Ronald Acuna Jr"],
    },
}


def create_reference_database(db_path="data/reference.db"):
    """Create a searchable reference database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        # Sets table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS valuable_sets (
                id INTEGER PRIMARY KEY,
                set_name TEXT UNIQUE,
                sport TEXT,
                year INTEGER,
                tier INTEGER,
                notes TEXT,
                key_cards TEXT
            )
        ''')
        
        # Insert tier 1 sets
        for set_name, info in TIER1_ALWAYS_GRADE.items():
            conn.execute('''
                INSERT OR REPLACE INTO valuable_sets (set_name, sport, year, tier, notes)
                VALUES (?, ?, ?, 1, ?)
            ''', (set_name, info['sport'], info['year'], info.get('notes', '')))
            
        # Insert tier 2 sets
        for set_name, info in TIER2_CHECK_KEYS.items():
            conn.execute('''
                INSERT OR REPLACE INTO valuable_sets (set_name, sport, year, tier, key_cards)
                VALUES (?, ?, ?, 2, ?)
            ''', (set_name, info['sport'], info['year'], info.get('key_cards', '')))
            
        # Players table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS key_players (
                id INTEGER PRIMARY KEY,
                player_name TEXT,
                sport TEXT,
                UNIQUE(player_name, sport)
            )
        ''')
        
        for sport, players in ALWAYS_CHECK_PLAYERS.items():
            for player in players:
                conn.execute('''
                    INSERT OR IGNORE INTO key_players (player_name, sport)
                    VALUES (?, ?)
                ''', (player, sport))
                
        # Keywords table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS valuable_keywords (
                id INTEGER PRIMARY KEY,
                keyword TEXT UNIQUE
            )
        ''')
        
        for keyword in VALUABLE_KEYWORDS:
            conn.execute('INSERT OR IGNORE INTO valuable_keywords (keyword) VALUES (?)', (keyword,))
            
        conn.commit()
        
    print(f"Reference database created: {db_path}")
    print(f"  - {len(TIER1_ALWAYS_GRADE)} tier 1 sets (always check)")
    print(f"  - {len(TIER2_CHECK_KEYS)} tier 2 sets (check key cards)")
    print(f"  - {sum(len(p) for p in ALWAYS_CHECK_PLAYERS.values())} key players")
    print(f"  - {len(VALUABLE_KEYWORDS)} valuable keywords")


def export_quick_reference(output_path="data/QUICK_REFERENCE.txt"):
    """Export a simple text file you can reference while sorting."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("PSA GRADING QUICK REFERENCE - CARDS TO SET ASIDE\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("TIER 1 - ALWAYS CHECK THESE SETS (virtually any card is worth grading)\n")
        f.write("-" * 70 + "\n")
        for set_name, info in sorted(TIER1_ALWAYS_GRADE.items(), key=lambda x: (x[1]['sport'], x[1]['year'])):
            f.write(f"  [{info['sport'].upper()[:4]}] {set_name}\n")
            f.write(f"          {info.get('notes', '')}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("TIER 2 - CHECK KEY ROOKIES IN THESE SETS\n")
        f.write("-" * 70 + "\n")
        for set_name, info in sorted(TIER2_CHECK_KEYS.items(), key=lambda x: (x[1]['sport'], x[1]['year'])):
            f.write(f"  [{info['sport'].upper()[:4]}] {set_name}\n")
            f.write(f"          Key: {info.get('key_cards', '')}\n")
            
        f.write("\n" + "=" * 70 + "\n")
        f.write("PLAYERS - ALWAYS LOOK UP CARDS OF THESE NAMES\n")
        f.write("-" * 70 + "\n")
        for sport, players in ALWAYS_CHECK_PLAYERS.items():
            f.write(f"\n  {sport.upper()}:\n")
            for i in range(0, len(players), 4):
                chunk = players[i:i+4]
                f.write(f"    {', '.join(chunk)}\n")
                
        f.write("\n" + "=" * 70 + "\n")
        f.write("KEYWORDS - If you see these on a card, CHECK VALUE\n")
        f.write("-" * 70 + "\n")
        for i in range(0, len(VALUABLE_KEYWORDS), 5):
            chunk = VALUABLE_KEYWORDS[i:i+5]
            f.write(f"  {', '.join(chunk)}\n")
            
        f.write("\n" + "=" * 70 + "\n")
        f.write("KEY ROOKIE YEARS - Cards from these years command huge premiums\n")
        f.write("-" * 70 + "\n")
        for sport, years in KEY_ROOKIE_YEARS.items():
            f.write(f"\n  {sport.upper()}:\n")
            for year, names in sorted(years.items()):
                f.write(f"    {year}: {', '.join(names)}\n")
                
        f.write("\n" + "=" * 70 + "\n")
        f.write("REMEMBER: Grading costs $27.99. Only grade if condition is PSA 8+\n")
        f.write("         and graded value is at least $100+\n")
        f.write("=" * 70 + "\n")
        
    print(f"\nQuick reference exported to: {output_path}")


if __name__ == "__main__":
    create_reference_database()
    export_quick_reference()
