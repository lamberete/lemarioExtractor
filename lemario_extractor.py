#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import sys
import subprocess
import json
import re

class Mode(Enum):
  LOWER   = 0  # some
  CAPITAL = 1  # Example
  UPPER   = 2  # WORDS

user = "p682JghS3"
password = "aGfUdCiE434"

alphabet = ["-", "‒", "a", "á", "b", "c", "d", "e", "é", "f", "g", 
  "h", "i", "í", "j", "k", "l", "m", "n", "ñ", "o", "ó", "p", "q", 
  "r", "s", "t", "u", "ú", "ü", "v", "w", "x", "y", "z"]
maxRaeResults = 200

# returns alphabetically next longer prefix
def longerPrefix(prefix):
  return prefix + alphabet[0]

# returns alphabetically next same lenght or shorter prefix
def nextPrefix(prefix):
  if (len(prefix) == 0):
    return prefix
  lastChar = prefix[-1] #prefix.decode('utf8')[-1].encode('utf8')
  if lastChar != alphabet[-1]:
    # prefix does not end with last leter of alphabet, so increase it
    nextChar = ""
    for i in range(len(alphabet)):
      if lastChar == alphabet[i]:
        nextChar = alphabet[i+1]
        return prefix[0:-1] + nextChar #.decode('utf8')[0:-1].encode('utf8') + nextChar
  # prefix ends with the last letter of the alphabet, remove it
  # but also the previous one if it happens to be an space
  if len(prefix) > 2 and prefix[-2] == " ":
    base = nextPrefix(prefix[0:-2])
    return base + " a" if len(base) > 0 else base
  return nextPrefix(prefix[0:-1])

# fetches rae result for words with given prefix
def getRaeWords(prefix):
  # use mode 31 (prefix) unless it contains an space, then use 33 (infix)
  mode = "31" if prefix.find(" ") < 0 else "33"
  result = subprocess.run(["wget", "-O", "-", "-o", "/dev/null", "https://" + user + ":" + password + "@dle.rae.es/data/search?m=" + mode + "\&t=1000\&w=" + prefix], stdout=subprocess.PIPE)
  jsonResult = json.loads(result.stdout)
  return jsonResult['res']

# checks if the prefix(word) exists among the received words taking into account html tags 
def getRaeWord(prefix, words):
  for i in words:
    val = i['header']
    firstTag = val.find('<')
    if (firstTag > 0):
      # keep text before first tag
      val = val[0:firstTag-1]
    elif (firstTag == 0):
      # keep text within first tag
      endTag = val.find('<', firstTag+1)
      val = val[firstTag+1:endTag-1]
    if val == prefix:
      return i
  return None

# prints lema and id in a csv format
def printRaeWord(word):
  # remove markups from header
  p = re.compile('(<i>)?([^<.]*)\.?(</i>)?(<sup>.*</sup>)?([^<.]*).') #regex to return the lema, ignoring <i> markup and removing <sup> ones
  m = p.match(word['header'])
  lema = m.group(2) + m.group(5)
  # print lema and id
  print("\"{0}\", \"{1}\"".format(lema, word['id'], flush = True))

# extracts alphabetically rae lemario starting with a given prefix
def getLemario(prefix = alphabet[0], mode = Mode.LOWER):
  # end condition (no prefix)
  while len(prefix) > 0:
    # Modify prefix according to mode
    if mode != Mode.LOWER and prefix[0] == prefix[0].upper():
      # if this prefix can't be capitalized, skip it when not in LOWER mode
      prefix = nextPrefix(prefix)
      continue
    if mode == Mode.CAPITAL:
      prefix = prefix.capitalize()
    elif mode == Mode.UPPER:
      prefix = prefix.upper()
    words = getRaeWords(prefix)
    groups = int(words[-1]['grp']) if len(words)>0 else 0
    print("{0}: {1}".format(prefix, groups), file=sys.stderr, flush=True)
    # get back to lower case to avoid errors on next/longerPrefix methods
    prefix = prefix.lower()
    # send founded words (if any) to the output
    for word in words:
      printRaeWord(word)

    if groups >= maxRaeResults-1:
      # too many groups for this prefix, try with a longer one
      # duplicates will be removed in post processing
      prefix = longerPrefix(prefix)
    else:
      prefix = nextPrefix(prefix)

# lets rock'n'roll
getLemario(mode=Mode.LOWER)
getLemario(mode=Mode.CAPITAL)
#getLemario(mode=Mode.UPPER)
getLemario(prefix="a a")
