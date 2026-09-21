from .consumables import Consumables
from .placed_structures import PlacedStructures
from .structure_items import StructureItems
from .dinos import Dinos
from .dino_components import DinoComponents
from .resources import Resources
from .player import Player
from .equipment import Equipment
from .dyes import Dyes
from .skins import Skins
from .trophies import Trophies
from .items import Items
from .world import World

class Structures:
    placed : PlacedStructures = PlacedStructures()
    items : StructureItems = StructureItems()

    all_bps = placed.all_bps + items.all_bps

class Classes:
    consumables: Consumables = Consumables()
    structures: Structures = Structures()
    dinos: Dinos = Dinos()
    dino_components: DinoComponents = DinoComponents()
    resources: Resources = Resources()
    player: Player = Player()
    equipment: Equipment = Equipment()
    dyes: Dyes = Dyes()
    skins: Skins = Skins()
    trophies: Trophies = Trophies()
    items: Items = Items()
    world: World = World()

    all_bps = consumables.all_bps + structures.all_bps + dinos.all_bps + dino_components.all_bps + \
        resources.all_bps + player.all_bps + equipment.all_bps + dyes.all_bps + skins.all_bps + \
        trophies.all_bps + items.all_bps + world.all_bps
