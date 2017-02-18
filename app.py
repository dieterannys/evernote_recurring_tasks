from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.ttypes as NoteStoreTypes
from time import sleep
import datetime
import math

from config_sandbox import *


def updated():
    global last_updatecount
    syncstate = noteStore.getSyncState()
    updatecount = syncstate.updateCount
    updated = (updatecount > last_updatecount)
    last_updatecount = updatecount
    return updated


def get_filtered_notes(filter):
    results = list()

    nFilter = NoteStoreTypes.NoteFilter()
    # reminderOrder, reminderTime, reminderDoneTime
    nFilter.words = filter
    rSpec = NoteStoreTypes.NotesMetadataResultSpec()
    rSpec.includeTitle = True
    rSpec.includeAttributes = True
    rSpec.includeTagGuids = True

    notesMetadataList = noteStore.findNotesMetadata(nFilter, 0, 50, rSpec)

    for note in notesMetadataList.notes:
        tags = list()
        try:
            for tagguid in note.tagGuids:
                tag = noteStore.getTag(tagguid)
                tags.append(tag.name)
        except:
            pass
        results.append({'title': note.title, 'guid': note.guid, 'donetime': note.attributes.reminderDoneTime,
                        'duetime': note.attributes.reminderTime, 'reminder': note.attributes.reminderOrder, 'tags': tags})
    
    return results



'''
returns recurring task info from title as {from, amount, unit}
from: where to offset from, last duedate or checked date
'''
def parse_rec(notetitle):
    result = dict()
    recpart = notetitle.split("[rec:")
    recpart = recpart[1].split("]")
    recpart = recpart[0]
    if recpart[0] == "+":
        result["from"] = "donetime"
        recpart = recpart[1:]
    else:
        result["from"] = "duetime"
    result["amount"] = int(recpart[:-1])
    result["unit"] = recpart[-1:]
    return result


# returns timestamp as [y, m, d, h, m]
def timestamp_to_formatted(timestamp):
    result = TIMESTAMP_BASE + datetime.timedelta(milliseconds=timestamp)
    return result


# returns [y ,m, d, h, m] as timestamp
def formatted_to_timestamp(f):
    t = f - TIMESTAMP_BASE
    t = int(t.total_seconds() * 1000)
    return t


def apply_changes():
    for note in get_filtered_notes("any: *[rec:*] tag:autoclean"):
        if note["donetime"] != None and ("[rec:" in note["title"]):
            rec_info = parse_rec(note["title"])
            if rec_info["from"] == "duetime":
                duetime = note["duetime"]
            else:
                duetime = note["donetime"]

            duetime = timestamp_to_formatted(duetime)
            if rec_info["unit"] == "d":
                # duetime[2] += rec_info["amount"]
                duetime += datetime.timedelta(days=rec_info["amount"])
            elif rec_info["unit"] == "w":
                # duetime[2] += 7 * rec_info["amount"]
                duetime += datetime.timedelta(days=7 * rec_info["amount"])
            elif rec_info["unit"] == "m":
                # duetime[1] += rec_info["amount"]
                year = int(math.floor((duetime.month + rec_info["amount"]) / 12) + duetime.year)
                month = int((duetime.month + rec_info["amount"]) % 12)
                day = duetime.day
                hour = duetime.hour
                minute = duetime.minute
                duetime = datetime.datetime(year, month, day, hour, minute)
            elif rec_info["unit"] == "y":
                # duetime[0] += rec_info["amount"]
                year = duetime.year + rec_info["amount"]
                month = duetime.month
                day = duetime.day
                hour = duetime.hour
                minute = duetime.minute
                duetime = datetime.datetime(year, month, day, hour, minute)
                pass
            duetime = formatted_to_timestamp(duetime)

            note_changed = noteStore.getNote(DEV_TOKEN, note["guid"], False, False, False, False)

            note_changed.attributes.reminderDoneTime = 0
            note_changed.attributes.reminderTime = duetime

            noteStore.updateNote(DEV_TOKEN, note_changed)

            print("%s - note \"%s\": unchecked and set to %s %s after %s" % (
            datetime.datetime.now(), note["title"], rec_info["amount"], rec_info["unit"], rec_info["from"]))
        
        if "autoclean" in note["tags"]:
            note_changed = noteStore.getNote(DEV_TOKEN, note["guid"], True, False, False, False)
            htmlfeed = note_changed.content
            if ('<en-todo checked="true" />' not in htmlfeed):
                print("%s - note \"%s\": no todos to clean" % (datetime.datetime.now(), note["title"])) 
                continue
            htmlfeed = htmlfeed.split("<div>")
            htmlfeed = [h for h in htmlfeed if ('<en-todo checked="true" />' not in h)]
            htmlfeed = ("<div>").join(htmlfeed)
            note_changed.content = htmlfeed
            noteStore.updateNote(DEV_TOKEN, note_changed)

            print("%s - note \"%s\": checked todos cleaned" % (datetime.datetime.now(), note["title"]))            


def run_routine():
    global last_updatecount
    if updated():
        print("%s - account updated since last check" % datetime.datetime.now())
        apply_changes()
        last_updatecount += 1
    else:
        print("%s - no updates since last check" % datetime.datetime.now())


TIMESTAMP_BASE = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
last_updatecount = 0

client = EvernoteClient(token=DEV_TOKEN, sandbox=sandbox)
noteStore = client.get_note_store()

if __name__ == "__main__":
    while True:
        run_routine()
        sleep(POLLING_INTERVAL)

