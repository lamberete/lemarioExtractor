33
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

class LemarioExtractor:
  def __init__ (self, alphabet, mode = Mode.PREFIX, initialSearch = None):
    self.alphabet = alphabet
    self.mode = mode
    self.search = initialSearch if initialSearch != None else alphabet[0]

  # updates search term to alphabetically next longer one
  def longerPrefix(self):
    self.search += self.alphabet[0]

  # updates search term to alphabetically next same lenght or shorter one
  def nextPrefix(self):
    if (len(self.search) == 0):
      # nothing to do for an empty search term
      pass
    elif self.search[-1] != self.alphabet[-1]:
      # search does not end with last letter of alphabet, increase it
      nextLetter = self.alphabet[self.alphabet.find(self.search[-1]) + 1]
      self.search = self.search[0:-1] + nextLetter
    elif len(self.search) > 2 and self.search[-2] == " ":
      # search term ends with last letter of alphabet but also the previous one happens to be an space, 
      # remove both, call nextPrefix recursively and add back the space if needed
      # TODO: consider doing this in a fancier way, maybe in a dedicated method
      self.search = self.search[0:-2]
      self.nextPrefix()
      if len(self.search) > 0:
        # now add the space and the first letter
        self.search += " " + self.alphabet[0]
    else:
      # search term ends with the last letter of the alphabet, remove it and call nextPrefix recursively
      self.search = self.search[0:-1]
      self.nextPrefix()

  # fetches rae result for words with current search and mode
  def getRaeWords(self):
    maxGroups = 200
    # TODO: use natively with urllib
    result = subprocess.run(["wget", "-O", "-", "-o", "/dev/null", "https://" + user + ":" + password + "@dle.rae.es/data/search?m=" + self.mode.value + "\&t=1000\&w=" + self.search], stdout=subprocess.PIPE)
    jsonResult = json.loads(result.stdout)['res']
    lastGroup = int(jsonResult[-1]['grp'])+1 if len(jsonResult)>0 else 0
    print("{0}: {1}".format(self.search, lastGroup), file=sys.stderr, flush=True)
    return jsonResult, lastGroup >= maxGroups

  # prints lema and id in a csv format
  def printRaeWord(self, word):
    # remove markups from header
    p = re.compile('(<i>)?([^<.]*)\.?(</i>)?(<sup>.*</sup>)?([^<.]*).') #regex to return the lema, ignoring <i> markup and removing <sup> ones
    m = p.match(word['header'])
    lema = m.group(2) + m.group(5)
    # print lema and id
    print("\"{0}\", \"{1}\"".format(lema, word['id'], flush = True))

  # extracts alphabetically rae lemario starting with a given prefix
  def getLemario(self):
    # loop until no search term
    while len(self.search) > 0:
      words, max = self.getRaeWords()
      # send founded words (if any) to the output
      for word in words:
        self.printRaeWord(word)
      if max:
        # too many groups for this prefix, try with a longer one
        # duplicates will be removed in post processing
        self.longerPrefix()
      else:
        self.nextPrefix()
      # TODO: Add a warning/abort condition if search term exceeds a set lenght

# lets rock'n'roll
def main():
  LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz-").getLemario()
  LemarioExtractor("AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ", Mode.INFIX).getLemario()
  LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz", Mode.INFIX, "a a").getLemario()
  LemarioExtractor("èî‒", Mode.INFIX).getLemario()


if __name__ == "__main__":
  # execute only if run as a script
  main()
