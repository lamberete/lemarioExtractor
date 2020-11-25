#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import sys
import subprocess
import json
import re

class Mode(Enum):
  PREFIX  = "31"
  SUFIX   = "32"
  INFIX   = "33"

user = "p682JghS3"
password = "aGfUdCiE434"
maxRaeResults = 200

# returns alphabetically next longer prefix
def longerPrefix(alphabet, prefix):
  return prefix + alphabet[0]

# returns alphabetically next same lenght or shorter prefix
def nextPrefix(alphabet, prefix):
  if (len(prefix) == 0):
    return prefix
  lastChar = prefix[-1] #prefix.decode('utf8')[-1].encode('utf8')
  if lastChar != alphabet[-1]:
    # prefix does not end with last leter of alphabet, so increase it
    nextChar = ""
    for i in range(len(alphabet)):
      if lastChar == alphabet[i]:
        nextChar = alphabet[i+1]
        return prefix[0:-1] + nextChar
  # prefix ends with the last letter of the alphabet, remove it
  # but also the previous one if it happens to be an space
  if len(prefix) > 2 and prefix[-2] == " ":
    base = nextPrefix(alphabet, prefix[0:-2])
    return base + " a" if len(base) > 0 else base
  return nextPrefix(alphabet, prefix[0:-1])

# fetches rae result for words with given prefix
def getRaeWords(prefix, mode):
  result = subprocess.run(["wget", "-O", "-", "-o", "/dev/null", "https://" + user + ":" + password + "@dle.rae.es/data/search?m=" + mode.value + "\&t=1000\&w=" + prefix], stdout=subprocess.PIPE)
  jsonResult = json.loads(result.stdout)
  return jsonResult['res']

# prints lema and id in a csv format
def printRaeWord(word):
  # remove markups from header
  p = re.compile('(<i>)?([^<.]*)\.?(</i>)?(<sup>.*</sup>)?([^<.]*).') #regex to return the lema, ignoring <i> markup and removing <sup> ones
  m = p.match(word['header'])
  lema = m.group(2) + m.group(5)
  # print lema and id
  print("\"{0}\", \"{1}\"".format(lema, word['id'], flush = True))

# extracts alphabetically rae lemario starting with a given prefix
def getLemario(alphabet, prefix, mode = Mode.PREFIX):
  # end condition (no prefix)
  while len(prefix) > 0:
    words = getRaeWords(prefix, mode)
    groups = int(words[-1]['grp'])+1 if len(words)>0 else 0
    print("{0}: {1}".format(prefix, groups), file=sys.stderr, flush=True)
    # send founded words (if any) to the output
    for word in words:
      printRaeWord(word)

    if groups >= maxRaeResults:
      # too many groups for this prefix, try with a longer one
      # duplicates will be removed in post processing
      prefix = longerPrefix(alphabet, prefix)
    else:
      prefix = nextPrefix(alphabet, prefix)


# lets rock'n'roll
getLemario("aábcdeéfghiíjklmnñoópqrstuúüvwxyz-", "a", Mode.PREFIX)
getLemario("AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ", "A", Mode.INFIX)
getLemario("aábcdeéfghiíjklmnñoópqrstuúüvwxyz", "a a", Mode.INFIX)
getLemario("èî‒", "è", Mode.INFIX)
