from enum import Enum


DET_FUNCTIONS = (
    'ddr', 'ddo', 'ngp'
)

SG_FUNCTIONS = (
    'dr', 'mr', 'fcra', 'fcfg', 'fceg', 'fcflg', 'fca', 'fcr', 'fctg'
)

ALLOWED_FUNCTIONS = (
    'ddr', 'mr', 'fctg', 'ddo', 'ngp', 'fcra', 'fcfg', 'fceg', 'fcflg', 'fca', 'fcr',
)

class Functions(Enum):
    pass