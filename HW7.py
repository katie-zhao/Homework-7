
# Your name: Katherine Zhao
# Your student id:
# Your email:
# List who you have worked with on this project: Syndey Finkelstein

import unittest
import sqlite3
import json
import os

def read_data(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path)
    file_data = f.read()
    f.close()
    json_data = json.loads(file_data)
    return json_data

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def make_positions_table(data, cur, conn):
    positions = []
    for player in data['squad']:
        position = player['position']
        if position not in positions:
            positions.append(position)
    cur.execute("CREATE TABLE IF NOT EXISTS Positions (id INTEGER PRIMARY KEY, position TEXT UNIQUE)")
    for i in range(len(positions)):
        cur.execute("INSERT OR IGNORE INTO Positions (id, position) VALUES (?,?)",(i, positions[i]))
    conn.commit()

## [TASK 1]: 25 points
# Finish the function make_players_table

#     This function takes 3 arguments: JSON data,
#         the database cursor, and the database connection object

#     It iterates through the JSON data to get a list of players in the squad
#     and loads them into a database table called 'Players'
#     with the following columns:
#         id ((datatype: int; Primary key) - note this comes from the JSON
#         name (datatype: text)
#         position_id (datatype: integer)
#         birthyear (datatype: int)
#         nationality (datatype: text)
#     To find the position_id for each player, you will have to look up 
#     the position in the Positions table we 
#     created for you -- see make_positions_table above for details.

def make_players_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Players (id INTEGER PRIMARY KEY, name TEXT, position_id INTEGER, birthyear INTEGER, nationality TEXT)")
    for player in data["squad"]:
        id = player["id"]
        name = player["name"]

        #to access Positions database do I have to create another cursor?
        position = player["position"]
        cur.execute("SELECT id FROM Positions WHERE position = ?", (position, ))
        position_id = int(cur.fetchone()[0])

        birthyear = int(player["dateOfBirth"].split("-")[0])
        nationality = player["nationality"]
        cur.execute("INSERT OR IGNORE INTO Players (id, name, position_id, birthyear, nationality) VALUES (?,?,?,?,?)", (id, name, position_id, birthyear, nationality))
    conn.commit()


## [TASK 2]: 10 points
# Finish the function nationality_search

    # This function takes 3 arguments as input: a list of countries,
    # the database cursor, and database connection object. 
 
    # It selects all the players from any of the countries in the list
    # and returns a list of tuples. Each tuple contains:
        # the player's name, their position_id, and their nationality.

def nationality_search(countries, cur, conn): 
    list_of_tups = []
    for country in countries:
        cur.execute("SELECT name, position_id, nationality FROM Players WHERE nationality = ?", (country, ))
        for row in cur:
            list_of_tups.append(row)
    return list_of_tups
    pass

## [TASK 3]: 10 points
# finish the function birthyear_nationality_search

#     This function takes 4 arguments as input: 
#     an age in years (int), 
#     a country (string), the database cursor, 
#     and the database connection object.

#     It selects all the players from the country passed to the function 
#     that were born BEFORE (2023 minus the year passed)
#     for example: if we pass 19 for the year, it should return 
#     players with birthdates BEFORE 2004
#     This function returns a list of tuples each containing 
#     the player’s name, nationality, and birth year. 


def birthyear_nationality_search(age, country, cur, conn):
    list_of_tups = []
    year = 2023 - age
    cur.execute("SELECT name, nationality, birthyear FROM Players WHERE birthyear < ? AND nationality = ?", (year, country))
    for row in cur:
        list_of_tups.append(row)
    return list_of_tups

    pass

## [TASK 4]: 15 points
# finish the function position_birth_search

    # This function takes 4 arguments as input: 
    # a position (string), 
    # age (int), the database cursor,
    # and the database connection object. 

    # It selects all the players who play the position
    #  passed to the function and
    # that were born AFTER (2023 minus the year passed)
    # for example: if we pass 19 for the year, it should return 
    # players with birth years AFTER 2004
    # This function returns a list of tuples each containing 
    # the player’s name, position, and birth year. 
    # HINT: You'll have to use JOIN for this task.

def position_birth_search(position, age, cur, conn):
        list_of_tups = []
        year = 2023 - age
        cur.execute('''SELECT Players.name, Positions.position, Players.birthyear 
                    FROM Players JOIN Positions ON Players.position_id = Positions.id
                    WHERE Players.birthyear > ? AND Positions.position = ?''', (year, position))
        for row in cur:
           list_of_tups.append(row)
        return list_of_tups


# [EXTRA CREDIT]
# You’ll make 3 new functions, make_winners_table(), make_seasons_table(),
# and winners_since_search(), 
# and then write at least 2 meaningful test cases for each of them. 

#     The first function takes 3 arguments: JSON data, 
#     the database cursor, and the database connection object.
#     It makes a table with 2 columns:
#         id (datatype: int; Primary key) -- note this comes from the JSON
#         name (datatype: text) -- note: use the full, not short, name
#     hint: look at how we made the Positions table above for an example


def make_winners_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Winners (id INTEGER PRIMARY KEY, name TEXT)")
    winners_list = []
    for game in data["seasons"]:
        if type(game["winner"]) == dict:
            if game["winner"]["name"] not in winners_list:
                winners_list.append(game["winner"]["name"])
    for i in range(len(winners_list)):
        winner_id = i
        name = winners_list[i]

        cur.execute("INSERT OR IGNORE INTO Winners (id, name) VALUES (?,?)", (winner_id, name))
    conn.commit()
    pass

#     The second function takes the same 3 arguments: JSON data, 
#     the database cursor, and the database connection object. 
#     It iterates through the JSON data to get info 
#     about previous Premier League seasons (don't include the current one)
#     and loads all of the seasons into a database table 
#     called ‘Seasons' with the following columns:
#         id (datatype: int; Primary key) - note this comes from the JSON
#         winner_id (datatype: text)
#         end_year (datatype: int)
#     NOTE: Skip seasons with no winner!

#     To find the winner_id for each season, you will have to 
#     look up the winner's name in the Winners table
#     see make_winners_table above for details

def make_seasons_table(data, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Seasons (id INTEGER PRIMARY KEY, winner_id TEXT, end_year INTEGER)")
    for game in data["seasons"]:
        if type(game["winner"]) == dict:

            id = game["id"]

            name = game["winner"]["name"]
            cur.execute("SELECT id FROM Winners WHERE name = ?", (name, )) #is this what we're supposed to do??
            winner_id = cur.fetchone()[0]


            end_year = game["endDate"].split("-")[0]

            cur.execute("INSERT OR IGNORE INTO Seasons (id, winner_id, end_year) VALUES (?,?,?)", (id, winner_id, end_year))
            conn.commit()

        else:
            continue
    pass

    
#     The third function takes in a year (string), the database cursor, 
#     and the database connection object. It returns a dictionary of how many 
#     times each team has won the Premier League since the passed year.
#     In the dict, each winning team's (full) name is a key,
#     and the value associated with each team is the number of times
#     they have won since the year passed, including the season that ended
#     the passed year. 

def winners_since_search(year, cur, conn):
    cur.execute('''SELECT Winners.name, Seasons.end_year 
                    FROM Winners JOIN Seasons ON Winners.id = Seasons.winner_id
                    AND Seasons.end_year > ?''', (year, ))
    new_dict = {}
    for row in cur:
        if row[0] in new_dict.keys():
            new_dict[row[0]] += 1
        else:
            new_dict[row[0]] = 1
    return new_dict

    pass


class TestAllMethods(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.conn = sqlite3.connect(path+'/'+'Football.db')
        self.cur = self.conn.cursor()
        self.conn2 = sqlite3.connect(path+'/'+'Football_seasons.db')
        self.cur2 = self.conn2.cursor()

    def test_players_table(self):
        self.cur.execute('SELECT * from Players')
        players_list = self.cur.fetchall()

        self.assertEqual(len(players_list), 30)
        self.assertEqual(len(players_list[0]),5)
        self.assertIs(type(players_list[0][0]), int)
        self.assertIs(type(players_list[0][1]), str)
        self.assertIs(type(players_list[0][2]), int)
        self.assertIs(type(players_list[0][3]), int)
        self.assertIs(type(players_list[0][4]), str)

    def test_nationality_search(self):
        x = sorted(nationality_search(['England'], self.cur, self.conn))
        self.assertEqual(len(x), 11)
        self.assertEqual(len(x[0]), 3)
        self.assertEqual(x[0][0], "Aaron Wan-Bissaka")

        y = sorted(nationality_search(['Brazil'], self.cur, self.conn))
        self.assertEqual(len(y), 3)
        self.assertEqual(y[2],('Fred', 2, 'Brazil'))
        self.assertEqual(y[0][1], 3)

    def test_birthyear_nationality_search(self):

        a = birthyear_nationality_search(24, 'England', self.cur, self.conn)
        self.assertEqual(len(a), 7)
        self.assertEqual(a[0][1], 'England')
        self.assertEqual(a[3][2], 1992)
        self.assertEqual(len(a[1]), 3)

    def test_type_speed_defense_search(self):
        b = sorted(position_birth_search('Goalkeeper', 35, self.cur, self.conn))
        self.assertEqual(len(b), 2)
        self.assertEqual(type(b[0][0]), str)
        self.assertEqual(type(b[1][1]), str)
        self.assertEqual(len(b[1]), 3) 
        self.assertEqual(b[1], ('Jack Butland', 'Goalkeeper', 1993)) 

        c = sorted(position_birth_search("Defence", 23, self.cur, self.conn))
        self.assertEqual(len(c), 1)
        self.assertEqual(c, [('Teden Mengi', 'Defence', 2002)])
    
    # test extra credit
    def test_make_winners_table(self):
        self.cur2.execute('SELECT * from Winners')
        winners_list = self.cur2.fetchall()
        self.assertEqual(len(winners_list), 7)
        self.assertEqual(type(winners_list[0][1]), str)
        self.assertEqual(type(winners_list[3][0]), int)

        pass

    def test_make_seasons_table(self):
        self.cur2.execute('SELECT * from Seasons')
        seasons_list = self.cur2.fetchall()
        self.assertEqual(len(seasons_list[1]), 3)
        self.assertEqual(type(seasons_list[1][2]), int)


        pass

    def test_winners_since_search(self):
        dict = winners_since_search("2007", self.cur2, self.conn)
        self.assertEqual(len(dict), 5)
        self.assertEqual(dict["Manchester City FC"], 5)

        pass


def main():

    #### FEEL FREE TO USE THIS SPACE TO TEST OUT YOUR FUNCTIONS

    json_data = read_data('football.json')
    cur, conn = open_database('Football.db')
    make_positions_table(json_data, cur, conn)
    make_players_table(json_data, cur, conn)
    conn.close()


    seasons_json_data = read_data('football_PL.json')
    cur2, conn2 = open_database('Football_seasons.db')
    make_winners_table(seasons_json_data, cur2, conn2)
    make_seasons_table(seasons_json_data, cur2, conn2)
    conn2.close()


if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)
