import fastf1
import os

fastf1.Cache.enable_cache('cache/')

session = fastf1.get_session(2024, 1, 'R')
session.load()

print(session.results[['DriverNumber', 'Abbreviation', 'TeamName', 'Position', 'Points']])