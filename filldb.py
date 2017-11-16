"""Fills DB with content from the sql file."""
from app import db
from random import randint

db.drop_all()
db.create_all()

with open('trackr_mini_dump.sql') as infile:
    s = infile.readlines()
    for row in s:
        if "schedule" in row and randint(0, 10) == 0: pass

        if "NULL" not in row and row.strip() is not "":
            try:
                db.engine.execute(row)
            except:
                pass