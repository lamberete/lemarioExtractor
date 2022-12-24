#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum
import argparse
import datetime
import json
import re
import random
import requests
import sys
import time

class Mode(Enum):
  PREFIX  = "31"
  SUFIX   = "32"
  INFIX   = "33"

class LemarioExtractor:
  # constructor: mandatory alphabet and optional mode and initial search term
  def __init__ (self, alphabet, mode = Mode.PREFIX, initialSearch = None, stopSearch = None):
    self.__maxResults = LemarioExtractor.getMaxResults()
    self.__alphabet = alphabet
    self.__mode = mode
    self.__search = initialSearch if initialSearch != None else alphabet[0]
    self.__stop = stopSearch
    self.__infixes = {}
    # By default, all char pairs are valid infixes
    for char in self.__alphabet:
      self.__infixes.update({char: self.__alphabet})

  # overwrite current mode
  def setMode(self, mode):
    self.__mode = mode

  # updates search term to alphabetically next longer one
  def __longerSearch(self):
    self.__search += self.__infixes[self.__search[-1]][0]

  # updates search term to alphabetically next same lenght or shorter one
  def __nextSearch(self):
    if len(self.__search) == 0:
      # nothing to do for an empty search term
      return
    try:
      alphabet = self.__infixes[self.__search[-2]]
    except:
      alphabet = self.__alphabet
    if self.__search[-1] != alphabet[-1]:
      # replace last letter from search as it is not the last valid one
      nextLetter = alphabet[alphabet.find(self.__search[-1]) + 1]
      self.__search = self.__search[0:-1] + nextLetter
    elif len(self.__search) > 2 and self.__search[-2] == " ":
      # last infix for the special case of searches with spaces
      # remove char and space, call nextPrefix recursively and add back the space if needed
      self.__search = self.__search[0:-2]
      self.__nextSearch()
      if len(self.__search) > 0:
        # now add the space and the first letter
        self.__search += " " + self.__alphabet[0]
    else:
      # search term ends with the last letter of the alphabet, remove it and call nextPrefix recursively
      self.__search = self.__search[0:-1]
      self.__nextSearch()

  # fetches rae result for words with current search and mode
  def __getRaeLemasApp(search, mode):
    url = "http://193.145.222.39/data/search?w={0}&m={1}".format(search, mode.value)
    numErrors = 0
    while True:
      try:
        result = requests.get(url, auth=(user, password))
        jsonResults = json.loads(result.text)['res']
        break
      except Exception as e:
        numErrors += 1
        print("Error parsing response: {}".format(str(e)), file=sys.stderr, flush=True)
        if numErrors < 10:
          time.sleep(numErrors * (0.5 + random.random()/2))
        else:
          print("Sorry, too much errors... exiting.", file=sys.stderr, flush=True)
          sys.exit()
    # convert results into lema-id pair
    lemas = []
    #regex to return the lema, ignoring <i> markup and removing <sup> ones
    p = re.compile('(?:<i>)?([^<.]*)\.?(?:</i>)?(?:<sup>.*</sup>)?([^<.]*)\.?') 
    for res in jsonResults:
      # remove markups from header
      m = p.match(res['header'])
      lema = m.group(1) + m.group(2)
      # compose simple lema entry
      lemas.append({"lema": lema, "id": res['id']})

    # log this search result
    print("{0}: {1} - {2} - ({3})".format(search, len(lemas), result.elapsed, numErrors), file=searches, flush=True)
    return lemas

  # prints given lemas and ids in a csv format
  def __printRaeLemas(self, lemas):
    for lema in lemas:
      print("\"{0}\", \"{1}\"".format(lema['lema'], lema['id']), file=lemario)

  # extracts alphabetically rae lemario starting with a given prefix
  def getLemario(self):
    # loop until no search term
    while len(self.__search) > 0 and self.__search != self.__stop:
      lemas = LemarioExtractor.__getRaeLemasApp(self.__search, self.__mode)
      # send founded words (if any) to the output
      self.__printRaeLemas(lemas)
      # TODO: Add a warning/abort condition if search term exceeds a set lenght
      if len(lemas) >= self.__maxResults:
        # too many results for this searchTerm, try with a longer one
        # (duplicates will be removed in post processing)
        self.__longerSearch()
      else:
        self.__nextSearch()
  
  def getMaxResults():
    # max results can be find by searching words startring with a
    return len(LemarioExtractor.__getRaeLemasApp("a", Mode.PREFIX))

  def removeInvalidInfixes(self):
    for first in self.__alphabet:
      for second in self.__alphabet:
        lemas = LemarioExtractor.__getRaeLemasApp(first + second, Mode.INFIX)
        if len(lemas) < self.__maxResults:
          # We already found all lemas for this infix, add it to results and to skip dict
          self.__printRaeLemas(lemas)
          self.__infixes.update({first: self.__infixes[first].replace(second, '')})
      #print("Valid infixes for {}: {}".format(first, self.__infixes[first]))

# lets rock'n'roll
def main():
  print("START: {}".format(str(datetime.datetime.now().isoformat())), flush=True)
  # Get lowercase standard lemas
  lowerExtractor = LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz-")
  lowerExtractor.removeInvalidInfixes() # this is an expensive operation, only worth for this case
  print("lower: {}".format(str(datetime.datetime.now().isoformat())), flush=True)
  lowerExtractor.getLemario()
  # Get lemas that include capital letters
  upperExtractor = LemarioExtractor("AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ", Mode.INFIX)
  print("upper: {}".format(str(datetime.datetime.now().isoformat())), flush=True)
  upperExtractor.getLemario()
  # Get lemas that include spaces
  spaceExtractor = LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz", Mode.INFIX, "a a")
  print("space: {}".format(str(datetime.datetime.now().isoformat())), flush=True)
  spaceExtractor.getLemario()
  # Get lemas that include rare chars
  rareExtractor = LemarioExtractor("àèìòùâêîôûäëïö‒", Mode.INFIX)
  print("rare: {}".format(str(datetime.datetime.now().isoformat())), flush=True)  
  rareExtractor.getLemario()
  print("END: {}".format(str(datetime.datetime.now().isoformat())), flush=True)
  

if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description='Searches dle.rae.es for existing lemas')
  parser.add_argument('user', help='username to connect to dle.rae.es')
  parser.add_argument('password', help='password to connect to dle.rae.es')
  parser.add_argument('-l', '--lemario', metavar='FILE', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='file to append lemas founded, defaults to <stdin>')
  parser.add_argument('-s', '--searches', metavar='FILE', nargs='?', type=argparse.FileType('w'), default=sys.stderr, help='file to append searches made, defaults to <stderr>')
  args = parser.parse_args()

  #TODO: convert this global vars in main method parameters and LemarioExtractor attributes
  user = args.user
  password = args.password
  lemario = args.lemario
  searches = args.searches

  main()
