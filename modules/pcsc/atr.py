# Adapting script from https://pyscard.sourceforge.io/pyscard-framework.html#framework-samples
# Thanks to Ludovic rousseau, mailto:ludovic.rousseau@free.fr
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_error, print_msg, print_ok_raw, print_error_raw
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
from utils.check_root import is_root
from smartcard.CardMonitoring import CardMonitor
from time import sleep
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardMonitoring import CardObserver
from smartcard.scard import *
from smartcard.ATR import ATR
from smartcard.util import toHexString
from evdev import UInput, ecodes
import uinput
import re
from string import whitespace

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Display ATR",
                       "Description": "This module display the ATR (Answer To Reset) of inserted cards.",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?
        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to read the tag"),
            'verbose': Option.create(name="verbose", value=False, description="verbose mode"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)


    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        reader = self.args.get("reader", "usb")
        verbose = str(self.args.get("verbose", "False")).lower() == "true"
        self.display_atr(reader=reader, verbose=verbose)

    def display_atr(self, reader="usb", verbose=False):
        print_info("Scanning present readers...")
        cardmonitor = CardMonitor()
    
        selectobserver = ATRObserver(verbose)
        cardmonitor.addObserver(selectobserver)

        while True:
            try:
                sleep(0.1)
            except KeyboardInterrupt:
                print()
                print_error("Module Interrupted")
                cardmonitor.deleteObserver(selectobserver)
                return True


# Card Observer to check the atr
class ATRObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def __init__(self, verbose):
        self.observer = ConsoleCardConnectionObserver()
        self.reader_name = "Uknown"
        self.verbose = verbose

    def update(self, observable, actions):
        try:
            readers = self._list()
            self.reader_name = readers[0]
        except:
            print_error("Error retreiving the reader")
        try:
            (addedcards, removedcards) = actions
            for card in addedcards:
                print_info(f"Reader 0: {self.reader_name}")
                print_ok_raw(f"Card State: Card inserted")
                print("ATR: ", toHexString(card.atr))
                
                
                atr = ATR(card.atr)
                if(self.verbose):
                    atr.dump()
                
                print()
                print_info("Possible identified card (using _smartcard_list.txt)")
                self.search_in_txt('utildata/_smartcard_list.txt', toHexString(card.atr))
            for card in removedcards:
                print_info(f"Reader 0: {self.reader_name}")
                print_error_raw(f"Card State: Card removed")
                print("ATR: ", toHexString(card.atr))
        except Exception as e:
            pass

    def search_in_txt(self, file, atr):
        with open(file, 'r') as file:
            for line in file:
                if(self.wspace(line)):
                    continue
                if(re.compile(line.rstrip()).match(atr)):
                    print_ok_raw(line.rstrip())
                    self.get_info(file)

    def get_info(self, file):
        for line in file:
            if(self.wspace(line)):
                print_msg(line.rstrip(), "cyan")
            else:
                break

    def wspace(self, string):
        first_character = string[0]  # Get the first character in the line.
        return True if first_character in whitespace else False

    def _list(self):
        try:
            hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to establish context : ' +
                                SCardGetErrorMessage(hresult))
    
            try:
                hresult, readers = SCardListReaders(hcontext, [])
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to list readers: ' +
                                    SCardGetErrorMessage(hresult))
                return readers
            finally:
                hresult = SCardReleaseContext(hcontext)
                if hresult != SCARD_S_SUCCESS:
                    raise Exception('Failed to release context: ' +
                                    SCardGetErrorMessage(hresult))
        except:
            return []

