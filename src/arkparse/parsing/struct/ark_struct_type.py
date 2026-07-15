from enum import Enum
from typing import Optional

from .ark_color import ArkColor
from .ark_linear_color import ArkLinearColor
from .ark_quat import ArkQuat
from .ark_rotator import ArkRotator
from .ark_tribe_rank_group import ArkTribeRankGroup
from .ark_vector import ArkVector
from .ark_vector2d import ArkVector2D
from .ark_unique_net_id_repl import ArkUniqueNetIdRepl
from .ark_vector_bool_pair import ArkVectorBoolPair
from .ark_tracked_actor_id_category_pair_with_bool import ArkTrackedActorIdCategoryPairWithBool
from .ark_my_persistent_buff_datas import ArkMyPersistentBuffDatas
from .ark_item_net_id import ArkItemNetId
from .ark_int_point import ArkIntPoint
from .ark_dino_ancestor_entry import ArkDinoAncestorEntry
from .ark_custom_item_data import ArkCustomItemData
from .ark_server_custom_folder import ArkServerCustomFolder
from .ark_crafting_resource_requirement import ArkCraftingResourceRequirement
from .ark_player_death_reason import ArkPlayerDeathReason
from .ark_primal_saddle_structure import ArkPrimalSaddleStructure
from .ark_gene_trait_struct import ArkGeneTraitStruct
from .ark_gacha_resource_struct import ArkGachaResourceStruct
from .ark_gigantoraptor_bonded_struct import ArkGigantoraptorBondedStruct
from .ark_painting_key_value import ArkPaintingKeyValue
from .ark_tracked_actor_id_category_pair import ArkTrackedActorIdCategoryPair
from .ark_dino_order_id import ArkDinoOrderID
from .ark_tribe_alliance import ArkTribeAlliance
from .ark_tribe_rank_group import ArkTribeRankGroup
from .ark_milestone_tree_level_and_index import ArkMilestoneTreeLevelAndIndex
from .ark_patrol_group_saved_data import ArkPatrolGroupSavedData

class ArkStructType(Enum):
    LinearColor = "LinearColor"
    Quat = "Quat"
    Vector = "Vector"
    Vector2D = "Vector2D"
    Rotator = "Rotator"
    UniqueNetIdRepl = "UniqueNetIdRepl"
    Color = "Color"
    VectorBoolPair = "VectorBoolPair"
    ArkTrackedActorIdCategoryPairWithBool = "TrackedActorIDCategoryPairWithBool"
    ArkTrackedActorIdCategoryPair = "TrackedActorIDCategoryPair"
    MyPersistentBuffDatas = "MyPersistentBuffDatas"
    ItemNetId = "ItemNetID"
    ArkDinoAncestor = "DinoAncestorsEntry"
    ArkIntPoint = "IntPoint"
    ArkCustomItemData = "CustomItemData"
    ArkServerCustomFolder = "ServerCustomFolder"
    ArkCraftingResourceRequirement = "CraftingResourceRequirement"
    ArkPlayerDeathReason = "PlayerDeathReason"
    ArkPrimalSaddleStructure = "PrimalSaddleStructure"
    ArkGeneTraitStruct = "GeneTraitStruct"
    GachaResourceStruct = "Gacha_ResourceStruct"
    GigantoraptorBondedStruct = "GigantoraptorBonded_Struct"
    ArkPaintingKeyValue = "PaintingKeyValue"
    ArkDinoOrderID = "DinoOrderID"
    ArkTribeAlliance = "TribeAlliance"
    ArkTribeRankGroup = "TribeRankGroup"
    ArkMilestoneTreeLevelAndIndex = "MilestoneTreeLevelAndIndex"
    ArkPatrolGroupSavedData = "Struct_PatrolGroupSavedData"

    # Static constructor mapping for ArkStructType
    

    def __new__(cls, type_name: str):
        # Create a new Enum member
        obj = object.__new__(cls)
        obj._value_ = type_name
        obj.type_name = type_name
        return obj

    def __init__(self, type_name: str):
        # Access `_constructors` via the class name directly
        _constructors = {
            "LinearColor": lambda data: ArkLinearColor(data),
            "Quat": lambda data: ArkQuat(data),
            "Vector": lambda data: ArkVector(data),
            "Vector2D": lambda data: ArkVector2D(data),
            "Rotator": lambda data: ArkRotator(data),
            "UniqueNetIdRepl": lambda data: ArkUniqueNetIdRepl(data),
            "Color": lambda data: ArkColor(data),
            "VectorBoolPair": lambda data: ArkVectorBoolPair(data),
            "ArkTrackedActorIdCategoryPairWithBool": lambda data: ArkTrackedActorIdCategoryPairWithBool(data),
            "ArkTrackedActorIdCategoryPair": lambda data: ArkTrackedActorIdCategoryPair(data),
            "MyPersistentBuffDatas": lambda data: ArkMyPersistentBuffDatas(data),
            "ItemNetID": lambda data: ArkItemNetId(data),
            "DinoAncestorsEntry": lambda data: ArkDinoAncestorEntry(data),
            "IntPoint": lambda data: ArkIntPoint(data),
            "CustomItemData": lambda data: ArkCustomItemData(data),
            "ServerCustomFolder": lambda data: ArkServerCustomFolder(data),
            "CraftingResourceRequirement": lambda data: ArkCraftingResourceRequirement(data),
            "PlayerDeathReason": lambda data: ArkPlayerDeathReason(data),
            "PrimalSaddleStructure": lambda data: ArkPrimalSaddleStructure(data),
            "GeneTraitStruct": lambda data: ArkGeneTraitStruct(data),
            "Gacha_ResourceStruct": lambda data: ArkGachaResourceStruct(data),
            "GigantoraptorBonded_Struct": lambda data: ArkGigantoraptorBondedStruct(data),
            "PaintingKeyValue": lambda data: ArkPaintingKeyValue(data),
            "DinoOrderID": lambda data: ArkDinoOrderID(data),
            "TribeAlliance": lambda data: ArkTribeAlliance(data),
            "TribeRankGroup": lambda data: ArkTribeRankGroup(data),
            "MilestoneTreeLevelAndIndex": lambda data: ArkMilestoneTreeLevelAndIndex(data),
            "Struct_PatrolGroupSavedData": lambda data: ArkPatrolGroupSavedData(data),
        }
        self.constructor = _constructors.get(type_name)

    @classmethod
    def from_type_name(cls, type_name: str) -> Optional['ArkStructType']:
        """Retrieve the ArkStructType by its type name."""
        return cls._value2member_map_.get(type_name)
    
    def to_dict(self):
        return {
            "type_name": self.type_name,
            "constructor": str(self.constructor),  # or the details you want from the constructor
        }