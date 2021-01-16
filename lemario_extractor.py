#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum
import argparse
import json
import re
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
    self.alphabet = alphabet
    self.mode = mode
    self.search = initialSearch if initialSearch != None else alphabet[0]
    self.stop = stopSearch

  # overwrite current alphabet and initial search term
  def setAlphabet(self, alphabet, initialSearch = None, stopSearch = None):
    self.alphabet = alphabet
    self.search = initialSearch if initialSearch != None else alphabet[0]
    self.stop = stopSearch

  # overwrite current mode
  def setMode(self, mode):
    self.mode = mode

  # updates search term to alphabetically next longer one
  def __longerSearch(self):
    self.search += self.alphabet[0]

  # updates search term to alphabetically next same lenght or shorter one
  def __nextSearch(self):
    if (len(self.search) == 0):
      # nothing to do for an empty search term
      pass
    elif self.search[-1] != self.alphabet[-1]:
      # search does not end with last letter of alphabet, increase it
      nextLetter = self.alphabet[self.alphabet.find(self.search[-1]) + 1]
      self.search = self.search[0:-1] + nextLetter
    # TODO: consider doing this in a fancier way, maybe in a dedicated method
    elif len(self.search) > 2 and self.search[-2] == " ":
      # search term ends with last letter of alphabet but also the previous one happens to be an space, 
      # remove both, call nextPrefix recursively and add back the space if needed
      self.search = self.search[0:-2]
      self.__nextSearch()
      if len(self.search) > 0:
        # now add the space and the first letter
        self.search += " " + self.alphabet[0]
    else:
      # search term ends with the last letter of the alphabet, remove it and call nextPrefix recursively
      self.search = self.search[0:-1]
      self.__nextSearch()

  # fetches rae result for words with current search and mode
  def __getRaeLemasApp(self, user, password):
    maxResults = 40
    maxGroups = 200
    url = "https://dle.rae.es/data/search?w={0}&m={1}".format(self.search, self.mode.value, user, password)
    numErrors = 0
    while True:
      try:
        result = requests.get(url, auth=(user, password))
        jsonResults = json.loads(result.text)['res']
        break;
      except:
        numErrors += 1
        #print("Error parsing response: {0}".format(result.text), file=sys.stderr, flush=True)
        if numErrors < 10:
          time.sleep(1)
        else:
          sys.exit()
    numResults = len(jsonResults)
    lastGroup = int(jsonResults[-1]['grp'])+1 if len(jsonResults)>0 else 0
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
    print("{0}: {1} - {2} - ({3})".format(self.search, numResults, result.elapsed, numErrors), file=searches, flush=True)
    return lemas, numResults >= maxResults

  # prints given lemas and ids in a csv format
  def __printRaeLemas(self, lemas):
    for lema in lemas:
      print("\"{0}\", \"{1}\"".format(lema['lema'], lema['id']), file=lemario)

  # extracts alphabetically rae lemario starting with a given prefix
  def getLemario(self):
    # loop until no search term
    while len(self.search) > 0 and self.search != self.stop:
      lemas, max = self.__getRaeLemasApp(user, password)
      # send founded words (if any) to the output
      self.__printRaeLemas(lemas)
      # TODO: Add a warning/abort condition if search term exceeds a set lenght
      if max:
        # too many groups for this searchTerm, try with a longer one
        # (duplicates will be removed in post processing)
        self.__longerSearch()
      else:
        self.__nextSearch()


# lets rock'n'roll
def main():
  # Get lowercase standard lemas
  LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz-").getLemario()
  # Get lemas that include capital letters
  LemarioExtractor("AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ", Mode.INFIX).getLemario()
  # Get lemas that include spaces
  LemarioExtractor("aábcdeéfghiíjklmnñoópqrstuúüvwxyz", Mode.INFIX, "a a").getLemario()
  # Get lemas that include rare chars
  LemarioExtractor("àèìòùâêîôûäëïö‒", Mode.INFIX).getLemario()


if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description='Searches dle.rae.es for existing lemas')
  parser.add_argument('user', help='username to connect to dle.rae.es')
  parser.add_argument('password', help='password to connect to dle.rae.es')
  parser.add_argument('-l', '--lemario', metavar='FILE', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='file to append lemas founded, defaults to <stdin>')
  parser.add_argument('-s', '--searches', metavar='FILE', nargs='?', type=argparse.FileType('w'), default=sys.stderr, help='file to append searches made, defaults to <stderr>')
  #TODO: add alphabet, mode, initialSearch and stopSearch to command line, skip main 

  args = parser.parse_args()

  #TODO: convert this global vars in main method parameters and LemarioExtractor attributes
  user = args.user
  password = args.password
  lemario = args.lemario
  searches = args.searches

  main()
