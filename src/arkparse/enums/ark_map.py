from enum import Enum

class ArkMap(Enum):
    ABERRATION = 0
    CRYSTAL_ISLES = 1
    EXTINCTION = 2
    GENESIS = 3
    ISLAND = 4
    RAGNAROK = 5
    SCORCHED_EARTH = 6
    VALGUERO = 7
    THE_CENTER = 8
    THE_ISLAND = 9
    ASTRAEOS = 10
    SVARTALFHEIM = 11
    CLUB_ARK = 12
    LOST_COLONY = 13
    GENESIS1 = 14

    def to_file_name(self) -> str:
        """
        Converts the enum value to a file name.
        :return: The file name of the map.
        """
        return self.name.replace('_', ' ').title().replace(' ', '')