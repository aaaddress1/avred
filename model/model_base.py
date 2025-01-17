from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional
import logging
import pickle
from dataclasses import dataclass
from enum import Enum
import datetime

from model.model_data import Match
from model.model_verification import Verification, Appraisal
from model.model_code import AsmInstruction, Section


class ScanInfo():
    def __init__(self, scannerName: str, scanSpeed: ScanSpeed):
        self.scannerName: str = scannerName
        self.scanSpeed: ScanSpeed = scanSpeed
        self.scanTime = datetime.datetime.now()

        self.scannerPipe: str = ''
        self.scanDuration: int = 0
        self.sections: List[Section] = []
        self.chunksTested: int = 0
        self.matchesAdded: int = 0


    def __str__(self):
        s = ''
        s += "{} {} {} {} {} {}".format(
            self.scannerName, self.scannerPipe, self.scanTime,
            "", self.chunksTested, self.matchesAdded
        )
        return s


class ScanSpeed(Enum):
    Unknown = 0
    Fast = 1
    Normal = 2
    Slow = 3
    Complete = 4


class Outcome():
    def __init__(self, fileInfo: FileInfo):
        self.fileInfo: FileInfo = fileInfo
        self.matches: List[Match] = []
        self.verification: Verification = None
        self.outflankPatches: List[OutflankPatch] = []

        self.isDetected: bool = False
        self.isScanned: bool = False
        #self.isMinimized: bool = False
        self.isVerified: bool = False
        self.isAugmented: bool = False
        self.isOutflanked: bool = False

        self.sections: List[Section] = []
        self.regions: List[Section] = []
        self.scanInfo: ScanInfo = ScanInfo("", ScanSpeed.Unknown)
        self.appraisal: Appraisal = Appraisal.Unknown


    @staticmethod
    def nullOutcome(fileInfo: FileInfo):
        return Outcome(fileInfo)
    

    def saveToFile(self, filepath: str):
        filenameOutcome = filepath + '.outcome'
        logging.info("Saving results to: {}".format(filenameOutcome))
        with open(filenameOutcome, 'wb') as handle:
            pickle.dump(self, handle)


    def __str__(self):
        s = ''
        if self.fileInfo is not None:
            s += str(self.fileInfo)
        s += '\n'
        s += "Status: scanned:{} verified:{} augmented:{} outflanked: {}".format(
            self.isScanned, self.isVerified, self.isAugmented, self.isOutflanked
        )
        s += "ScanInfo: {}\n".format(self.scanInfo)
        s += "Matches: \n"
        for match in self.matches:
            s += str(match)
        s += "\nVerification: \n"
        s += str(self.verification)
        s += "\n"    
        return s
    

class OutflankPatch():
    def __init__(self, 
                 matchIdx: int, 
                 offset: int, 
                 replaceBytes: bytes,
                 asmOne: AsmInstruction,
                 asmTwo: AsmInstruction,
                 info: str, 
                 considerations: str
    ):
        self.matchIdx = matchIdx
        self.offset = offset
        self.replaceBytes = replaceBytes

        self.asmOne = asmOne
        self.asmTwo = asmTwo

        self.info = info
        self.considerations = considerations


    def __str__(self):
        s = ''
        s += "Patch at Offset: {}  Bytes: {}\n".format(self.offset, self.replaceBytes)
        s += "  {}\n".format(self.info)
        s += "  {}\n".format(self.considerations)
        return s


class FileInfo():
    def __init__(self, name, size, hash, time, ident):
        self.name = name
        self.size = size
        self.hash = hash
        self.date = time
        self.ident = ident

    def __str__(self):
        s = ''
        s += "{} size: {}  ident: {}".format(self.name, self.size, self.ident)
        return s


@dataclass
class Scanner:
    """Interface to the AV scanner"""
    scanner_path: str = ""
    scanner_name: str = ""

    def scannerDetectsBytes(self, data: bytes, filename: str):
        pass


