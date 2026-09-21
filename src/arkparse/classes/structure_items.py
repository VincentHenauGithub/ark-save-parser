"""Inventory items that place a structure, grouped by material and then by purpose."""

class Adobe:
    ceiling_door_xl: str = "/Game/PrimalEarth/Structures/Tileset/HatchframesXL/Doors/Items/PrimalItemStructure_Ceiling_Door_XL_Adobe.PrimalItemStructure_Ceiling_Door_XL_Adobe_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Adobe/PrimalItemStructure_TriCeiling_Adobe.PrimalItemStructure_TriCeiling_Adobe_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Adobe/PrimalItemStructure_TriFoundation_Adobe.PrimalItemStructure_TriFoundation_Adobe_C"
    ramp: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ramps/Adobe/PrimalItemStructure_Ramp_Adobe.PrimalItemStructure_Ramp_Adobe_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Adobe/PrimalItemStructure_TriRoof_Adobe.PrimalItemStructure_TriRoof_Adobe_C"
    large_wall: str = "/Game/PrimalEarth/StructuresPlus/Structures/Walls_L/Adobe/PrimalItemStructure_LargeWall_Adobe.PrimalItemStructure_LargeWall_Adobe_C"
    adobe_ceiling: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeCeiling.PrimalItemStructure_AdobeCeiling_C"
    adobe_ceiling_door_giant: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeCeilingDoorGiant.PrimalItemStructure_AdobeCeilingDoorGiant_C"
    adobe_door: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeDoor.PrimalItemStructure_AdobeDoor_C"
    adobe_fence_foundation: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeFenceFoundation.PrimalItemStructure_AdobeFenceFoundation_C"
    adobe_floor: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeFloor.PrimalItemStructure_AdobeFloor_C"
    adobe_frame_gate: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeFrameGate.PrimalItemStructure_AdobeFrameGate_C"
    adobe_gate_door: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeGateDoor.PrimalItemStructure_AdobeGateDoor_C"
    adobe_gate_door_large: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeGateDoor_Large.PrimalItemStructure_AdobeGateDoor_Large_C"
    adobe_gateframe_large: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeGateframe_Large.PrimalItemStructure_AdobeGateframe_Large_C"
    adobe_lader: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeLader.PrimalItemStructure_AdobeLader_C"
    adobe_pillar: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobePillar.PrimalItemStructure_AdobePillar_C"
    adobe_railing: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeRailing.PrimalItemStructure_AdobeRailing_C"
    adobe_wall: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeWall.PrimalItemStructure_AdobeWall_C"
    adobe_wall_sloped_left: str = "/Game/ScorchedEarth/Structures/Adobe/Blueprints/PrimalItemStructure_AdobeWall_Sloped_Left.PrimalItemStructure_AdobeWall_Sloped_Left_C"

    all_bps = [ceiling_door_xl, tri_ceiling, tri_foundation, ramp, tri_roof, large_wall, adobe_ceiling,
               adobe_ceiling_door_giant, adobe_door, adobe_fence_foundation, adobe_floor, adobe_frame_gate,
               adobe_gate_door, adobe_gate_door_large, adobe_gateframe_large, adobe_lader, adobe_pillar,
               adobe_railing, adobe_wall, adobe_wall_sloped_left]

class Greenhouse:
    greenhouse_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Greenhouse/PrimalItemStructure_GreenhouseCeiling.PrimalItemStructure_GreenhouseCeiling_C"
    greenhouse_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Greenhouse/PrimalItemStructure_GreenhouseDoor.PrimalItemStructure_GreenhouseDoor_C"
    greenhouse_roof: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Greenhouse/PrimalItemStructure_GreenhouseRoof.PrimalItemStructure_GreenhouseRoof_C"
    greenhouse_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Greenhouse/PrimalItemStructure_GreenhouseWall.PrimalItemStructure_GreenhouseWall_C"
    greenhouse_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Greenhouse/PrimalItemStructure_GreenhouseWall_Sloped_Left.PrimalItemStructure_GreenhouseWall_Sloped_Left_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Greenhouse/PrimalItemStructure_TriCeiling_Greenhouse.PrimalItemStructure_TriCeiling_Greenhouse_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Greenhouse/PrimalItemStructure_TriRoof_Greenhouse.PrimalItemStructure_TriRoof_Greenhouse_C"

    all_bps = [greenhouse_ceiling, greenhouse_door, greenhouse_roof, greenhouse_wall,
               greenhouse_wall_sloped_left, tri_ceiling, tri_roof]

class Stone:
    cliff_platform: str = "/Game/Aberration/Structures/CliffPlatforms/Stone_CliffPlatform/PrimalItemStructure_Stone_CliffPlatform.PrimalItemStructure_Stone_CliffPlatform_C"
    stone_pipe_intake: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_StonePipeIntake.PrimalItemStructure_StonePipeIntake_C"
    stone_pipe_tap: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_StonePipeTap.PrimalItemStructure_StonePipeTap_C"
    stone_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Stone/PrimalItemStructure_StoneWall_Sloped_Left.PrimalItemStructure_StoneWall_Sloped_Left_C"
    stone_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneCeiling.PrimalItemStructure_StoneCeiling_C"
    stone_ceiling_door_giant: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneCeilingDoorGiant.PrimalItemStructure_StoneCeilingDoorGiant_C"
    stone_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneDoor.PrimalItemStructure_StoneDoor_C"
    stone_fence_foundation: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneFenceFoundation.PrimalItemStructure_StoneFenceFoundation_C"
    stone_floor: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneFloor.PrimalItemStructure_StoneFloor_C"
    stone_gate: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneGate.PrimalItemStructure_StoneGate_C"
    stone_gate_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneGateLarge.PrimalItemStructure_StoneGateLarge_C"
    stone_gateframe: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneGateframe.PrimalItemStructure_StoneGateframe_C"
    stone_gateframe_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneGateframe_Large.PrimalItemStructure_StoneGateframe_Large_C"
    stone_pillar: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StonePillar.PrimalItemStructure_StonePillar_C"
    stone_railing: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneRailing.PrimalItemStructure_StoneRailing_C"
    stone_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Stone/PrimalItemStructure_StoneWall.PrimalItemStructure_StoneWall_C"
    tree_platform: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_TreePlatform_Stone.PrimalItemStructure_TreePlatform_Stone_C"
    stone_ladder: str = "/Game/PrimalEarth/Structures/Stone/Stone_Ladder/PrimalItemStructure_StoneLadder.PrimalItemStructure_StoneLadder_C"
    ceiling_door_xl: str = "/Game/PrimalEarth/Structures/Tileset/HatchframesXL/Doors/Items/PrimalItemStructure_Ceiling_Door_XL_Stone.PrimalItemStructure_Ceiling_Door_XL_Stone_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Stone/PrimalItemStructure_TriCeiling_Stone.PrimalItemStructure_TriCeiling_Stone_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Stone/PrimalItemStructure_TriFoundation_Stone.PrimalItemStructure_TriFoundation_Stone_C"
    ramp: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ramps/Stone/PrimalItemStructure_Ramp_Stone.PrimalItemStructure_Ramp_Stone_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Stone/PrimalItemStructure_TriRoof_Stone.PrimalItemStructure_TriRoof_Stone_C"
    large_wall: str = "/Game/PrimalEarth/StructuresPlus/Structures/Walls_L/Stone/PrimalItemStructure_LargeWall_Stone.PrimalItemStructure_LargeWall_Stone_C"

    all_bps = [cliff_platform, stone_pipe_intake, stone_pipe_tap, stone_wall_sloped_left, stone_ceiling,
               stone_ceiling_door_giant, stone_door, stone_fence_foundation, stone_floor, stone_gate,
               stone_gate_large, stone_gateframe, stone_gateframe_large, stone_pillar, stone_railing,
               stone_wall, tree_platform, stone_ladder, ceiling_door_xl, tri_ceiling, tri_foundation, ramp,
               tri_roof, large_wall]

class Metal:
    cliff_platform: str = "/Game/Aberration/Structures/CliffPlatforms/Metal_CliffPlatform/PrimalItemStructure_Metal_CliffPlatform.PrimalItemStructure_Metal_CliffPlatform_C"
    ocean_platform: str = "/Game/Genesis/Structures/OceanPlatform/OceanPlatform_Wood/PrimalItemStructure_Metal_OceanPlatform.PrimalItemStructure_Metal_OceanPlatform_C"
    metal_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalCeiling.PrimalItemStructure_MetalCeiling_C"
    metal_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalDoor.PrimalItemStructure_MetalDoor_C"
    metal_fence_foundation: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalFenceFoundation.PrimalItemStructure_MetalFenceFoundation_C"
    metal_floor: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalFloor.PrimalItemStructure_MetalFloor_C"
    metal_gate: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalGate.PrimalItemStructure_MetalGate_C"
    metal_gate_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalGate_Large.PrimalItemStructure_MetalGate_Large_C"
    metal_gateframe: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalGateframe.PrimalItemStructure_MetalGateframe_C"
    metal_gateframe_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalGateframe_Large.PrimalItemStructure_MetalGateframe_Large_C"
    metal_ladder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalLadder.PrimalItemStructure_MetalLadder_C"
    metal_pillar: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalPillar.PrimalItemStructure_MetalPillar_C"
    metal_railing: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalRailing.PrimalItemStructure_MetalRailing_C"
    metal_sign: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalSign.PrimalItemStructure_MetalSign_C"
    metal_sign_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalSign_Large.PrimalItemStructure_MetalSign_Large_C"
    metal_spike_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalSpikeWall.PrimalItemStructure_MetalSpikeWall_C"
    metal_trapdoor_giant: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalTrapdoorGiant.PrimalItemStructure_MetalTrapdoorGiant_C"
    metal_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Metal/PrimalItemStructure_MetalWall.PrimalItemStructure_MetalWall_C"
    metal_pipe_intake: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_MetalPipeIntake.PrimalItemStructure_MetalPipeIntake_C"
    metal_pipe_tap: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_MetalPipeTap.PrimalItemStructure_MetalPipeTap_C"
    water_tank_metal: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_WaterTankMetal.PrimalItemStructure_WaterTankMetal_C"
    metal_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Metal/PrimalItemStructure_MetalWall_Sloped_Left.PrimalItemStructure_MetalWall_Sloped_Left_C"
    tree_platform: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_TreePlatform_Metal.PrimalItemStructure_TreePlatform_Metal_C"
    ceiling_door_xl: str = "/Game/PrimalEarth/Structures/Tileset/HatchframesXL/Doors/Items/PrimalItemStructure_Ceiling_Door_XL_Metal.PrimalItemStructure_Ceiling_Door_XL_Metal_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Metal/PrimalItemStructure_TriCeiling_Metal.PrimalItemStructure_TriCeiling_Metal_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Metal/PrimalItemStructure_TriFoundation_Metal.PrimalItemStructure_TriFoundation_Metal_C"
    ramp: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ramps/Metal/PrimalItemStructure_Ramp_Metal.PrimalItemStructure_Ramp_Metal_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Metal/PrimalItemStructure_TriRoof_Metal.PrimalItemStructure_TriRoof_Metal_C"
    large_wall: str = "/Game/PrimalEarth/StructuresPlus/Structures/Walls_L/Metal/PrimalItemStructure_LargeWall_Metal.PrimalItemStructure_LargeWall_Metal_C"

    all_bps = [cliff_platform, ocean_platform, metal_ceiling, metal_door, metal_fence_foundation, metal_floor,
               metal_gate, metal_gate_large, metal_gateframe, metal_gateframe_large, metal_ladder,
               metal_pillar, metal_railing, metal_sign, metal_sign_large, metal_spike_wall,
               metal_trapdoor_giant, metal_wall, metal_pipe_intake, metal_pipe_tap, water_tank_metal,
               metal_wall_sloped_left, tree_platform, ceiling_door_xl, tri_ceiling, tri_foundation, ramp,
               tri_roof, large_wall]

class Wood:
    cliff_platform: str = "/Game/Aberration/Structures/CliffPlatforms/Wood_CliffPlatform/PrimalItemStructure_Wood_CliffPlatform.PrimalItemStructure_Wood_CliffPlatform_C"
    wood_elevator_platform_large: str = "/Game/Aberration/Structures/PrimitiveElevator/PrimalItemStructure_WoodElevatorPlatform_Large.PrimalItemStructure_WoodElevatorPlatform_Large_C"
    wood_elevator_platform_medium: str = "/Game/Aberration/Structures/PrimitiveElevator/PrimalItemStructure_WoodElevatorPlatform_Medium.PrimalItemStructure_WoodElevatorPlatform_Medium_C"
    wood_elevator_platform_small: str = "/Game/Aberration/Structures/PrimitiveElevator/PrimalItemStructure_WoodElevatorPlatform_Small.PrimalItemStructure_WoodElevatorPlatform_Small_C"
    wood_elevator_top_switch: str = "/Game/Aberration/Structures/PrimitiveElevator/PrimalItemStructure_WoodElevatorTopSwitch.PrimalItemStructure_WoodElevatorTopSwitch_C"
    wood_elevator_track: str = "/Game/Aberration/Structures/PrimitiveElevator/PrimalItemStructure_WoodElevatorTrack.PrimalItemStructure_WoodElevatorTrack_C"
    ocean_platform: str = "/Game/Genesis/Structures/OceanPlatform/OceanPlatform_Wood/PrimalItemStructure_Wood_OceanPlatform.PrimalItemStructure_Wood_OceanPlatform_C"
    train_track_auto: str = "/Game/Packs/Frontier/Structures/TrainTracks/Auto/Wood/PrimalItemStructure_TrainTrack_Auto_Wood.PrimalItemStructure_TrainTrack_Auto_Wood_C"
    wood_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Wood/PrimalItemStructure_WoodWall_Sloped_Left.PrimalItemStructure_WoodWall_Sloped_Left_C"
    furniture_wood_bench: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_Furniture_WoodBench.PrimalItemStructure_Furniture_WoodBench_C"
    furniture_wood_chair: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_Furniture_WoodChair.PrimalItemStructure_Furniture_WoodChair_C"
    furniture_wood_table: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_Furniture_WoodTable.PrimalItemStructure_Furniture_WoodTable_C"
    tree_platform: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_TreePlatform_Wood.PrimalItemStructure_TreePlatform_Wood_C"
    wood_cage: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodCage.PrimalItemStructure_WoodCage_C"
    wood_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodCeiling.PrimalItemStructure_WoodCeiling_C"
    wood_ceiling_door_giant: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodCeilingDoorGiant.PrimalItemStructure_WoodCeilingDoorGiant_C"
    wood_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodDoor.PrimalItemStructure_WoodDoor_C"
    wood_fence_foundation: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodFenceFoundation.PrimalItemStructure_WoodFenceFoundation_C"
    wood_floor: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodFloor.PrimalItemStructure_WoodFloor_C"
    wood_gate: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodGate.PrimalItemStructure_WoodGate_C"
    wood_gate_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodGate_Large.PrimalItemStructure_WoodGate_Large_C"
    wood_gateframe: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodGateframe.PrimalItemStructure_WoodGateframe_C"
    wood_gateframe_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodGateframe_Large.PrimalItemStructure_WoodGateframe_Large_C"
    wood_ladder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodLadder.PrimalItemStructure_WoodLadder_C"
    wood_pillar: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodPillar.PrimalItemStructure_WoodPillar_C"
    wood_railing: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodRailing.PrimalItemStructure_WoodRailing_C"
    wood_sign: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodSign.PrimalItemStructure_WoodSign_C"
    wood_sign_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodSign_Large.PrimalItemStructure_WoodSign_Large_C"
    wood_spike_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodSpikeWall.PrimalItemStructure_WoodSpikeWall_C"
    wood_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WoodWall.PrimalItemStructure_WoodWall_C"
    ceiling_door_xl: str = "/Game/PrimalEarth/Structures/Tileset/HatchframesXL/Doors/Items/PrimalItemStructure_Ceiling_Door_XL_Wood.PrimalItemStructure_Ceiling_Door_XL_Wood_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Wood/PrimalItemStructure_TriCeiling_Wood.PrimalItemStructure_TriCeiling_Wood_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Wood/PrimalItemStructure_TriFoundation_Wood.PrimalItemStructure_TriFoundation_Wood_C"
    ramp: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ramps/Wood/PrimalItemStructure_Ramp_Wood.PrimalItemStructure_Ramp_Wood_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Wood/PrimalItemStructure_TriRoof_Wood.PrimalItemStructure_TriRoof_Wood_C"
    large_wall: str = "/Game/PrimalEarth/StructuresPlus/Structures/Walls_L/Wood/PrimalItemStructure_LargeWall_Wood.PrimalItemStructure_LargeWall_Wood_C"

    all_bps = [cliff_platform, wood_elevator_platform_large, wood_elevator_platform_medium,
               wood_elevator_platform_small, wood_elevator_top_switch, wood_elevator_track, ocean_platform,
               train_track_auto, wood_wall_sloped_left, furniture_wood_bench, furniture_wood_chair,
               furniture_wood_table, tree_platform, wood_cage, wood_ceiling, wood_ceiling_door_giant,
               wood_door, wood_fence_foundation, wood_floor, wood_gate, wood_gate_large, wood_gateframe,
               wood_gateframe_large, wood_ladder, wood_pillar, wood_railing, wood_sign, wood_sign_large,
               wood_spike_wall, wood_wall, ceiling_door_xl, tri_ceiling, tri_foundation, ramp, tri_roof,
               large_wall]

class Thatch:
    thatch_roof: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Thatch/PrimalItemStructure_ThatchRoof.PrimalItemStructure_ThatchRoof_C"
    thatch_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Roofs/Thatch/PrimalItemStructure_ThatchWall_Sloped_Left.PrimalItemStructure_ThatchWall_Sloped_Left_C"
    thatch_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Thatch/PrimalItemStructure_ThatchCeiling.PrimalItemStructure_ThatchCeiling_C"
    thatch_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Thatch/PrimalItemStructure_ThatchDoor.PrimalItemStructure_ThatchDoor_C"
    thatch_floor: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Thatch/PrimalItemStructure_ThatchFloor.PrimalItemStructure_ThatchFloor_C"
    thatch_pillar: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Thatch/PrimalItemStructure_ThatchPillar.PrimalItemStructure_ThatchPillar_C"
    thatch_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Thatch/PrimalItemStructure_ThatchWall.PrimalItemStructure_ThatchWall_C"
    ladder: str = "/Game/PrimalEarth/Structures/Thatch/PrimalItemStructure_Ladder_Thatch.PrimalItemStructure_Ladder_Thatch_C"
    railing: str = "/Game/PrimalEarth/Structures/Tileset/Railings/Thatch/PrimalItemStructure_Railing_Thatch.PrimalItemStructure_Railing_Thatch_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Thatch/PrimalItemStructure_TriCeiling_Thatch.PrimalItemStructure_TriCeiling_Thatch_C"
    fence_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/FenceSupports/Thatch/PrimalItemStructure_FenceFoundation_Thatch.PrimalItemStructure_FenceFoundation_Thatch_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Thatch/PrimalItemStructure_TriFoundation_Thatch.PrimalItemStructure_TriFoundation_Thatch_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Thatch/PrimalItemStructure_TriRoof_Thatch.PrimalItemStructure_TriRoof_Thatch_C"

    all_bps = [thatch_roof, thatch_wall_sloped_left, thatch_ceiling, thatch_door, thatch_floor, thatch_pillar,
               thatch_wall, ladder, railing, tri_ceiling, fence_foundation, tri_foundation, tri_roof]

class Tek:
    tek_bridge: str = "/Game/Extinction/Structures/TekBridge/PrimalItemStructure_TekBridge.PrimalItemStructure_TekBridge_C"
    tek_alarm: str = "/Game/Genesis/Structures/TekAlarm/PrimalItemStructure_TekAlarm.PrimalItemStructure_TekAlarm_C"
    tek_jump_pad: str = "/Game/Genesis/Structures/TekJumpPad/PrimalItemStructure_TekJumpPad.PrimalItemStructure_TekJumpPad_C"
    crop_plot: str = "/Game/Genesis2/Structures/CropPlotTek/PrimalItemStructure_CropPlot_Tek.PrimalItemStructure_CropPlot_Tek_C"
    lost_colony_tek_bunker: str = "/Game/LostColony/Structures/TekBunker/Items/PrimalItemStructure_LostColony_TekBunker.PrimalItemStructure_LostColony_TekBunker_C"
    chem_bench: str = "/Game/Packs/Wasteland/Structures/TekChemBench/PrimalItemStructure_ChemBench_Tek.PrimalItemStructure_ChemBench_Tek_C"
    tek_cloning_chamber: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_TekCloningChamber.PrimalItemStructure_TekCloningChamber_C"
    bed: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Bed_Tek.PrimalItemStructure_Bed_Tek_C"
    tek_generator: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekGenerator.PrimalItemStructure_TekGenerator_C"
    tek_light: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekLight.PrimalItemStructure_TekLight_C"
    tek_replicator: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekReplicator.PrimalItemStructure_TekReplicator_C"
    tek_shield: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekShield.PrimalItemStructure_TekShield_C"
    tek_teleporter_mini: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekTeleporterMini.PrimalItemStructure_TekTeleporterMini_C"
    tek_transmitter: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekTransmitter.PrimalItemStructure_TekTransmitter_C"
    tek_trough: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TekTrough.PrimalItemStructure_TekTrough_C"
    turret_tek: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretTek.PrimalItemStructure_TurretTek_C"
    tek_ceiling: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekCeiling.PrimalItemStructure_TekCeiling_C"
    tek_ceiling_door_giant: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekCeilingDoor_Giant.PrimalItemStructure_TekCeilingDoor_Giant_C"
    tek_door: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekDoor.PrimalItemStructure_TekDoor_C"
    tek_fence_foundation: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekFenceFoundation.PrimalItemStructure_TekFenceFoundation_C"
    tek_floor: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekFloor.PrimalItemStructure_TekFloor_C"
    tek_gate: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekGate.PrimalItemStructure_TekGate_C"
    tek_gate_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekGate_Large.PrimalItemStructure_TekGate_Large_C"
    tek_gateframe: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekGateframe.PrimalItemStructure_TekGateframe_C"
    tek_gateframe_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekGateframe_Large.PrimalItemStructure_TekGateframe_Large_C"
    tek_ladder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekLadder.PrimalItemStructure_TekLadder_C"
    tek_pillar: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekPillar.PrimalItemStructure_TekPillar_C"
    tek_railing: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekRailing.PrimalItemStructure_TekRailing_C"
    tek_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekWall.PrimalItemStructure_TekWall_C"
    tek_wall_sloped_left: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Tek/PrimalItemStructure_TekWall_Sloped_Left.PrimalItemStructure_TekWall_Sloped_Left_C"
    ceiling_door_xl: str = "/Game/PrimalEarth/Structures/Tileset/HatchframesXL/Doors/Items/PrimalItemStructure_Ceiling_Door_XL_Tek.PrimalItemStructure_Ceiling_Door_XL_Tek_C"
    tri_ceiling: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ceilings/Triangle/Tek/PrimalItemStructure_TriCeiling_Tek.PrimalItemStructure_TriCeiling_Tek_C"
    tri_foundation: str = "/Game/PrimalEarth/StructuresPlus/Structures/Foundations/Triangle/Tek/PrimalItemStructure_TriFoundation_Tek.PrimalItemStructure_TriFoundation_Tek_C"
    ramp: str = "/Game/PrimalEarth/StructuresPlus/Structures/Ramps/Tek/PrimalItemStructure_Ramp_Tek.PrimalItemStructure_Ramp_Tek_C"
    tri_roof: str = "/Game/PrimalEarth/StructuresPlus/Structures/Roofs_Tri/Tek/PrimalItemStructure_TriRoof_Tek.PrimalItemStructure_TriRoof_Tek_C"
    large_wall: str = "/Game/PrimalEarth/StructuresPlus/Structures/Walls_L/Tek/PrimalItemStructure_LargeWall_Tek.PrimalItemStructure_LargeWall_Tek_C"

    all_bps = [tek_bridge, tek_alarm, tek_jump_pad, crop_plot, lost_colony_tek_bunker, chem_bench,
               tek_cloning_chamber, bed, tek_generator, tek_light, tek_replicator, tek_shield,
               tek_teleporter_mini, tek_transmitter, tek_trough, turret_tek, tek_ceiling,
               tek_ceiling_door_giant, tek_door, tek_fence_foundation, tek_floor, tek_gate, tek_gate_large,
               tek_gateframe, tek_gateframe_large, tek_ladder, tek_pillar, tek_railing, tek_wall,
               tek_wall_sloped_left, ceiling_door_xl, tri_ceiling, tri_foundation, ramp, tri_roof, large_wall]

class Turrets:
    anti_flyer_turret: str = "/Game/Packs/Wasteland/Structures/AntiFlyerTurret/PrimalItemStructure_AntiFlyerTurret.PrimalItemStructure_AntiFlyerTurret_C"
    heavy_turret: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_HeavyTurret.PrimalItemStructure_HeavyTurret_C"
    structure_turret: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Turret.PrimalItemStructure_Turret_C"
    turret_ballista: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretBallista.PrimalItemStructure_TurretBallista_C"
    turret_catapult: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretCatapult.PrimalItemStructure_TurretCatapult_C"
    turret_minigun: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretMinigun.PrimalItemStructure_TurretMinigun_C"
    turret_plant: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretPlant.PrimalItemStructure_TurretPlant_C"
    turret_rocket: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TurretRocket.PrimalItemStructure_TurretRocket_C"

    all_bps = [anti_flyer_turret, heavy_turret, structure_turret, turret_ballista, turret_catapult,
               turret_minigun, turret_plant, turret_rocket]

class Water:
    large: str = "/Game/Packs/Frontier/Structures/WaterReservoir/PrimalItemStructure_WaterTank_Large.PrimalItemStructure_WaterTank_Large_C"
    structure_water_tank: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_WaterTank.PrimalItemStructure_WaterTank_C"

    all_bps = [large, structure_water_tank]

class Crafting:
    steam_forge: str = "/Game/Packs/Steampunk/Structures/MegaForge/PrimalItemStructure_SteamForge.PrimalItemStructure_SteamForge_C"
    anvil_bench: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_AnvilBench.PrimalItemStructure_AnvilBench_C"
    structure_campfire: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Campfire.PrimalItemStructure_Campfire_C"
    chem_bench: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_ChemBench.PrimalItemStructure_ChemBench_C"
    compost_bin: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_CompostBin.PrimalItemStructure_CompostBin_C"
    structure_cooking_pot: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_CookingPot.PrimalItemStructure_CookingPot_C"
    structure_fabricator: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Fabricator.PrimalItemStructure_Fabricator_C"
    structure_forge: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Forge.PrimalItemStructure_Forge_C"
    structure_grill: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Grill.PrimalItemStructure_Grill_C"
    industrial_cooking_pot: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_IndustrialCookingPot.PrimalItemStructure_IndustrialCookingPot_C"
    industrial_forge: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_IndustrialForge.PrimalItemStructure_IndustrialForge_C"
    mortar_and_pestle: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_MortarAndPestle.PrimalItemStructure_MortarAndPestle_C"

    all_bps = [steam_forge, anvil_bench, structure_campfire, chem_bench, compost_bin, structure_cooking_pot,
               structure_fabricator, structure_forge, structure_grill, industrial_cooking_pot,
               industrial_forge, mortar_and_pestle]

class Taxidermy:
    taxidermy_base_small: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItemStructure_TaxidermyBase_Small.PrimalItemStructure_TaxidermyBase_Small_C"

    all_bps = [taxidermy_base_small]

class Flags:
    ice_wyvern: str = "/Game/ASA/Dinos/IceWyvern/Boss/Flag/PrimalItemStructure_Flag_IceWyvern.PrimalItemStructure_Flag_IceWyvern_C"
    val_megaraptor: str = "/Game/ASA/Dinos/Megaraptor/Boss/Flag/PrimalItemStructure_Flag_ValMegaraptor.PrimalItemStructure_Flag_ValMegaraptor_C"
    rockwell: str = "/Game/Aberration/CoreBlueprints/Items/Trophies/PrimalItemStructure_Flag_Rockwell.PrimalItemStructure_Flag_Rockwell_C"
    king_kaiju: str = "/Game/Extinction/CoreBlueprints/Trophies/PrimalItemStructure_Flag_KingKaiju.PrimalItemStructure_Flag_KingKaiju_C"
    king_kaiju_mecha: str = "/Game/Extinction/CoreBlueprints/Trophies/PrimalItemStructure_Flag_KingKaijuMecha.PrimalItemStructure_Flag_KingKaijuMecha_C"
    lost_king: str = "/Game/LostColony/Structures/BossFlagLostKing/PrimalItemStructure_Flag_LostKing.PrimalItemStructure_Flag_LostKing_C"
    lost_queen: str = "/Game/LostColony/Structures/BossFlagLostQueen/PrimalItemStructure_Flag_LostQueen.PrimalItemStructure_Flag_LostQueen_C"
    kraken: str = "/Game/Mods/Astraeos/Assets/Structures/KrakenBossFlag/PrimalItemStructure_Flag_Kraken.PrimalItemStructure_Flag_Kraken_C"
    structure_flag: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Flag.PrimalItemStructure_Flag_C"
    dragon: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Flag_Dragon.PrimalItemStructure_Flag_Dragon_C"
    gorilla: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Flag_Gorilla.PrimalItemStructure_Flag_Gorilla_C"
    spider: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Flag_Spider.PrimalItemStructure_Flag_Spider_C"
    manticore: str = "/Game/ScorchedEarth/Structures/ManticoreFlag/PrimalItemStructure_Flag_Manticore.PrimalItemStructure_Flag_Manticore_C"

    all_bps = [ice_wyvern, val_megaraptor, rockwell, king_kaiju, king_kaiju_mecha, lost_king, lost_queen,
               kraken, structure_flag, dragon, gorilla, spider, manticore]

class Signs:
    hanging_sign: str = "/Game/Packs/Frontier/Structures/HangingSign/PrimalItemStructure_HangingSign.PrimalItemStructure_HangingSign_C"

    all_bps = [hanging_sign]

class Lights:
    lc_lights: str = "/Game/LostColony/Structures/Lights/PrimalItemStructure_LC_Lights.PrimalItemStructure_LC_Lights_C"
    oil_lamp: str = "/Game/Packs/Frontier/Structures/OilLamp/PrimalItemStructure_OilLamp.PrimalItemStructure_OilLamp_C"
    spot_light: str = "/Game/Packs/Steampunk/Structures/SpotLight/PrimalItemStructure_SpotLight.PrimalItemStructure_SpotLight_C"
    steam_lights: str = "/Game/Packs/Steampunk/Structures/SteamLights/PrimalItemStructure_SteamLights.PrimalItemStructure_SteamLights_C"
    tof_lights: str = "/Game/Packs/TidesOfFortune/Structures/Lights/PrimalItemStructure_ToF_Lights.PrimalItemStructure_ToF_Lights_C"
    wasteland_lights: str = "/Game/Packs/Wasteland/Structures/Lights/PrimalItemStructure_WastelandLights.PrimalItemStructure_WastelandLights_C"
    xmas_lights_ww: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_XmasLights_WW.PrimalItemStructure_XmasLights_WW_C"
    lamppost: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Lamppost.PrimalItemStructure_Lamppost_C"
    lamppost_omni: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_LamppostOmni.PrimalItemStructure_LamppostOmni_C"
    standing_torch: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_StandingTorch.PrimalItemStructure_StandingTorch_C"
    wall_torch: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_WallTorch.PrimalItemStructure_WallTorch_C"

    all_bps = [lc_lights, oil_lamp, spot_light, steam_lights, tof_lights, wasteland_lights, xmas_lights_ww,
               lamppost, lamppost_omni, standing_torch, wall_torch]

class Storage:
    balloon: str = "/Game/Extinction/Structures/ItemBalloon/PrimalItemStructure_StorageBox_Balloon.PrimalItemStructure_StorageBox_Balloon_C"
    ammo_container: str = "/Game/Genesis2/Structures/AmmoBox/PrimalItemStructure_AmmoContainer.PrimalItemStructure_AmmoContainer_C"
    barrel: str = "/Game/Packs/Frontier/Structures/BarrelStorage/PrimalItemStructure_StorageBox_Barrel.PrimalItemStructure_StorageBox_Barrel_C"
    christmas_gift_ww: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_StorageBox_ChristmasGift_WW.PrimalItemStructure_StorageBox_ChristmasGift_WW_C"
    ice_box: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_IceBox.PrimalItemStructure_IceBox_C"
    huge: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_StorageBox_Huge.PrimalItemStructure_StorageBox_Huge_C"
    large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_StorageBox_Large.PrimalItemStructure_StorageBox_Large_C"
    small: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_StorageBox_Small.PrimalItemStructure_StorageBox_Small_C"
    decor_box: str = "/Game/PrimalEarth/Structures/DecorBox/PrimalItemStructure_DecorBox.PrimalItemStructure_DecorBox_C"
    structure_dedicated_storage: str = "/Game/PrimalEarth/StructuresPlus/Misc/DedicatedStorage/PrimalItemStructure_DedicatedStorage.PrimalItemStructure_DedicatedStorage_C"

    all_bps = [balloon, ammo_container, barrel, christmas_gift_ww, ice_box, huge, large, small, decor_box,
               structure_dedicated_storage]

class Furniture:
    structure_furniture_rug: str = "/Game/Aberration/CoreBlueprints/Items/Structures/PrimalItemStructure_Furniture_Rug.PrimalItemStructure_Furniture_Rug_C"
    poker_table_sh: str = "/Game/Packs/Frontier/Minigames/Poker/Table/PrimalItemStructure_PokerTableSH.PrimalItemStructure_PokerTableSH_C"
    fancy_chair: str = "/Game/Packs/Frontier/Structures/FancyArmchair/PrimalItemStructure_FancyChair.PrimalItemStructure_FancyChair_C"
    fancy_couch: str = "/Game/Packs/Frontier/Structures/FancyCouch/PrimalItemStructure_Furniture_FancyCouch.PrimalItemStructure_Furniture_FancyCouch_C"
    saloon_chair: str = "/Game/Packs/Frontier/Structures/SaloonChair/PrimalItemStructure_Furniture_SaloonChair.PrimalItemStructure_Furniture_SaloonChair_C"
    saloon_stool: str = "/Game/Packs/Frontier/Structures/SaloonStool/PrimalItemStructure_SaloonStool.PrimalItemStructure_SaloonStool_C"
    saloon_table: str = "/Game/Packs/Frontier/Structures/SaloonTable/PrimalItemStructure_Furniture_SaloonTable.PrimalItemStructure_Furniture_SaloonTable_C"
    tinkering_desk: str = "/Game/Packs/Steampunk/Structures/TinkeringDesk/PrimalItemStructure_TinkeringDesk.PrimalItemStructure_TinkeringDesk_C"
    modern: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Bed_Modern.PrimalItemStructure_Bed_Modern_C"
    simple: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Bed_Simple.PrimalItemStructure_Bed_Simple_C"
    gravestone: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_Furniture_Gravestone.PrimalItemStructure_Furniture_Gravestone_C"

    all_bps = [structure_furniture_rug, poker_table_sh, fancy_chair, fancy_couch, saloon_chair, saloon_stool,
               saloon_table, tinkering_desk, modern, simple, gravestone]

class Plants:
    plant_pot: str = "/Game/Packs/Frontier/Structures/PlantPot/PrimalItemStructure_PlantPot.PrimalItemStructure_PlantPot_C"
    large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_CropPlot_Large.PrimalItemStructure_CropPlot_Large_C"
    medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_CropPlot_Medium.PrimalItemStructure_CropPlot_Medium_C"
    small: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_CropPlot_Small.PrimalItemStructure_CropPlot_Small_C"
    plant_species_y_trap: str = "/Game/ScorchedEarth/WeaponPlantSpeciesY/PrimalItemStructure_PlantSpeciesYTrap.PrimalItemStructure_PlantSpeciesYTrap_C"

    all_bps = [plant_pot, large, medium, small, plant_species_y_trap]

class Ships:
    shipyard_large: str = "/Game/Packs/TidesOfFortune/Structures/Shipyard/PrimalItemStructure_Shipyard_Large.PrimalItemStructure_Shipyard_Large_C"

    all_bps = [shipyard_large]

class Misc:
    dark_altar: str = "/Game/ASA/Dinos/DarkPegasus/Taming/PrimalItemStructure_DarkAltar.PrimalItemStructure_DarkAltar_C"
    gas_collector: str = "/Game/Aberration/Structures/GasCollector/PrimalItemStructure_GasCollector.PrimalItemStructure_GasCollector_C"
    portable_ladder: str = "/Game/Aberration/Structures/PortableRopeLadder/PrimalItemStructure_PortableLadder.PrimalItemStructure_PortableLadder_C"
    cryo_fridge: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItemStructure_CryoFridge.PrimalItemStructure_CryoFridge_C"
    dino_leash: str = "/Game/Extinction/Structures/DinoLeash/PrimalItemStructure_DinoLeash.PrimalItemStructure_DinoLeash_C"
    pressure_plate: str = "/Game/Genesis/Structures/TekAlarm/PrimalItemStructure_PressurePlate.PrimalItemStructure_PressurePlate_C"
    egg_incubator: str = "/Game/Genesis2/Structures/EggIncubator/PrimalItemStructure_EggIncubator.PrimalItemStructure_EggIncubator_C"
    lost_colony_bloodforge: str = "/Game/LostColony/Structures/Bloodforge/Item/PrimalItemStructure_LostColony_Bloodforge.PrimalItemStructure_LostColony_Bloodforge_C"
    lost_colony_cryo_hospital: str = "/Game/LostColony/Structures/CryoHospital/Item/PrimalItemStructure_LostColony_CryoHospital.PrimalItemStructure_LostColony_CryoHospital_C"
    lost_colony_medical_stand: str = "/Game/LostColony/Structures/MedicalStand/Item/PrimalItemStructure_LostColony_MedicalStand.PrimalItemStructure_LostColony_MedicalStand_C"
    lost_colony_shoulder_pet_display_stand: str = "/Game/LostColony/Structures/ShoulderPetDisplayStand/Item/PrimalItemStructure_LostColony_ShoulderPetDisplayStand.PrimalItemStructure_LostColony_ShoulderPetDisplayStand_C"
    lost_colony_warbench: str = "/Game/LostColony/Structures/Warbench/Item/PrimalItemStructure_LostColony_Warbench.PrimalItemStructure_LostColony_Warbench_C"
    coffin: str = "/Game/Packs/Frontier/Structures/Coffin/PrimalItemStructure_Coffin.PrimalItemStructure_Coffin_C"
    drawing_sheet: str = "/Game/Packs/Frontier/Structures/DrawingSheet/PrimalItemStructure_DrawingSheet.PrimalItemStructure_DrawingSheet_C"
    saloon_piano: str = "/Game/Packs/Frontier/Structures/SaloonPiano/PrimalItemStructure_SaloonPiano.PrimalItemStructure_SaloonPiano_C"
    wall_scaffolding: str = "/Game/Packs/Frontier/Structures/Scaffolding/PrimalItemStructure_Wall_Scaffolding.PrimalItemStructure_Wall_Scaffolding_C"
    shootable_bottle: str = "/Game/Packs/Frontier/Structures/ShootableBottle/PrimalItemStructure_ShootableBottle.PrimalItemStructure_ShootableBottle_C"
    town_bell: str = "/Game/Packs/Frontier/Structures/TownBell/PrimalItemStructure_TownBell.PrimalItemStructure_TownBell_C"
    treasure_cache_asa: str = "/Game/Packs/Frontier/Structures/TreasureCache/PrimalItemStructure_TreasureCache_ASA.PrimalItemStructure_TreasureCache_ASA_C"
    windmill: str = "/Game/Packs/Frontier/Structures/Windmill/PrimalItemStructure_Windmill.PrimalItemStructure_Windmill_C"
    steampunk_clock: str = "/Game/Packs/Steampunk/Structures/Clock/PrimalItemStructure_SteampunkClock.PrimalItemStructure_SteampunkClock_C"
    embryo_incubator: str = "/Game/Packs/Steampunk/Structures/EmbryoIncubator/PrimalItemStructure_EmbryoIncubator.PrimalItemStructure_EmbryoIncubator_C"
    gene_infuser: str = "/Game/Packs/Steampunk/Structures/GeneInfuser/PrimalItemStructure_GeneInfuser.PrimalItemStructure_GeneInfuser_C"
    industrial_preservin_bin: str = "/Game/Packs/Steampunk/Structures/IndustrialPreservingBin/PrimalItemStructure_IndustrialPreservinBin.PrimalItemStructure_IndustrialPreservinBin_C"
    library_storage: str = "/Game/Packs/Steampunk/Structures/LibraryStorage/PrimalItemStructure_LibraryStorage.PrimalItemStructure_LibraryStorage_C"
    linked_storage: str = "/Game/Packs/Steampunk/Structures/LinkedStorage/PrimalItemStructure_LinkedStorage.PrimalItemStructure_LinkedStorage_C"
    tesla_coil: str = "/Game/Packs/Steampunk/Structures/TeslaCoil/PrimalItemStructure_TeslaCoil.PrimalItemStructure_TeslaCoil_C"
    bounty_board: str = "/Game/Packs/TidesOfFortune/Structures/BountyBoard/PrimalItemStructure_BountyBoard.PrimalItemStructure_BountyBoard_C"
    cargo_ledger_tof: str = "/Game/Packs/TidesOfFortune/Structures/CargoLedger/PrimalItemStructure_CargoLedger_ToF.PrimalItemStructure_CargoLedger_ToF_C"
    fishtank_tof: str = "/Game/Packs/TidesOfFortune/Structures/Fishtank/Item/PrimalItemStructure_Fishtank_ToF.PrimalItemStructure_Fishtank_ToF_C"
    market: str = "/Game/Packs/TidesOfFortune/Structures/Market/PrimalItemStructure_Market.PrimalItemStructure_Market_C"
    bio_grinder: str = "/Game/Packs/Wasteland/Structures/BioGrinder/PrimalItemStructure_BioGrinder.PrimalItemStructure_BioGrinder_C"
    garage: str = "/Game/Packs/Wasteland/Structures/Garage/PrimalItemStructure_Garage.PrimalItemStructure_Garage_C"
    tribe_tower: str = "/Game/Packs/Wasteland/Structures/TribeTower/PrimalItemStructure_TribeTower.PrimalItemStructure_TribeTower_C"
    elevator_platform_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_ElevatorPlatformLarge.PrimalItemStructure_ElevatorPlatformLarge_C"
    elevator_platform_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_ElevatorPlatformMedium.PrimalItemStructure_ElevatorPlatformMedium_C"
    elevator_platform_small: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_ElevatorPlatformSmall.PrimalItemStructure_ElevatorPlatformSmall_C"
    elevator_track_base: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_ElevatorTrackBase.PrimalItemStructure_ElevatorTrackBase_C"
    reverse_vacuum_comparment: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_ReverseVacuumComparment.PrimalItemStructure_ReverseVacuumComparment_C"
    underwater_base: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/BuildingBases/PrimalItemStructure_UnderwaterBase.PrimalItemStructure_UnderwaterBase_C"
    christmas_tree: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_ChristmasTree.PrimalItemStructure_ChristmasTree_C"
    snowman: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_Snowman.PrimalItemStructure_Snowman_C"
    stocking: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_Stocking.PrimalItemStructure_Stocking_C"
    wreath: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Christmas/PrimalItemStructure_Wreath.PrimalItemStructure_Wreath_C"
    easter_egg: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Halloween/PrimalItemStructure_EasterEgg.PrimalItemStructure_EasterEgg_C"
    hw_grave: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Halloween/PrimalItemStructure_HW_Grave.PrimalItemStructure_HW_Grave_C"
    pumpkin: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Halloween/PrimalItemStructure_Pumpkin.PrimalItemStructure_Pumpkin_C"
    scarecrow: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Halloween/PrimalItemStructure_Scarecrow.PrimalItemStructure_Scarecrow_C"
    training_dummy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Halloween/PrimalItemStructure_TrainingDummy.PrimalItemStructure_TrainingDummy_C"
    air_conditioner: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_AirConditioner.PrimalItemStructure_AirConditioner_C"
    bear_trap: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_BearTrap.PrimalItemStructure_BearTrap_C"
    bear_trap_large: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_BearTrap_Large.PrimalItemStructure_BearTrap_Large_C"
    beer_barrel: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_BeerBarrel.PrimalItemStructure_BeerBarrel_C"
    cannon: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Cannon.PrimalItemStructure_Cannon_C"
    feeding_trough: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_FeedingTrough.PrimalItemStructure_FeedingTrough_C"
    fireplace: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Fireplace.PrimalItemStructure_Fireplace_C"
    grinder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Grinder.PrimalItemStructure_Grinder_C"
    keypad: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_Keypad.PrimalItemStructure_Keypad_C"
    painting_canvas: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_PaintingCanvas.PrimalItemStructure_PaintingCanvas_C"
    preserving_bin: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_PreservingBin.PrimalItemStructure_PreservingBin_C"
    sea_mine: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_SeaMine.PrimalItemStructure_SeaMine_C"
    sleeping_bag_hide: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_SleepingBag_Hide.PrimalItemStructure_SleepingBag_Hide_C"
    trophy_base: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TrophyBase.PrimalItemStructure_TrophyBase_C"
    trophy_wall: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Misc/PrimalItemStructure_TrophyWall.PrimalItemStructure_TrophyWall_C"
    power_generator: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_PowerGenerator.PrimalItemStructure_PowerGenerator_C"
    toilet: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_Toilet.PrimalItemStructure_Toilet_C"
    tree_tap: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Pipes/PrimalItemStructure_TreeTap.PrimalItemStructure_TreeTap_C"
    fish_basket: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_FishBasket.PrimalItemStructure_FishBasket_C"
    rope_ladder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_RopeLadder.PrimalItemStructure_RopeLadder_C"
    war_map: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_WarMap.PrimalItemStructure_WarMap_C"
    wardrums: str = "/Game/PrimalEarth/CoreBlueprints/Items/Structures/Wooden/PrimalItemStructure_Wardrums.PrimalItemStructure_Wardrums_C"
    bee_hive: str = "/Game/PrimalEarth/Structures/BeeHive/PrimalItemStructure_BeeHive.PrimalItemStructure_BeeHive_C"
    display_case: str = "/Game/PrimalEarth/Structures/DisplayCase/PrimalItemStructure_DisplayCase.PrimalItemStructure_DisplayCase_C"
    birthday_cake: str = "/Game/PrimalEarth/Structures/PopOutCake/PrimalItemStructure_BirthdayCake.PrimalItemStructure_BirthdayCake_C"
    wreath_flower: str = "/Game/PrimalEarth/Structures/Skins/Easter/PrimalItemStructure_Wreath_Flower.PrimalItemStructure_Wreath_Flower_C"
    fish_mount_coel: str = "/Game/PrimalEarth/Structures/Skins/SummerBash/PrimalItemStructure_FishMount_Coel.PrimalItemStructure_FishMount_Coel_C"
    fish_mount_piranha: str = "/Game/PrimalEarth/Structures/Skins/SummerBash/PrimalItemStructure_FishMount_Piranha.PrimalItemStructure_FishMount_Piranha_C"
    fish_mount_salmon: str = "/Game/PrimalEarth/Structures/Skins/SummerBash/PrimalItemStructure_FishMount_Salmon.PrimalItemStructure_FishMount_Salmon_C"
    shark_jaws_trophy: str = "/Game/PrimalEarth/Structures/Skins/SummerBash/PrimalItemStructure_SharkJawsTrophy.PrimalItemStructure_SharkJawsTrophy_C"
    mirror: str = "/Game/ScorchedEarth/Structures/DesertFurnitureSet/Mirror/PrimalItemStructure_Mirror.PrimalItemStructure_Mirror_C"
    vessel: str = "/Game/ScorchedEarth/Structures/DesertFurnitureSet/Vessel/PrimalItemStructure_Vessel.PrimalItemStructure_Vessel_C"
    oil_pump: str = "/Game/ScorchedEarth/Structures/OilPump/PrimalItemStructure_oilPump.PrimalItemStructure_oilPump_C"
    tent: str = "/Game/ScorchedEarth/Structures/Tent/PrimalItemStructure_Tent.PrimalItemStructure_Tent_C"
    water_well: str = "/Game/ScorchedEarth/Structures/WaterWell/PrimalItemStructure_WaterWell.PrimalItemStructure_WaterWell_C"
    wind_turbine: str = "/Game/ScorchedEarth/Structures/WindTurbine/PrimalItemStructure_WindTurbine.PrimalItemStructure_WindTurbine_C"

    all_bps = [dark_altar, gas_collector, portable_ladder, cryo_fridge, dino_leash, pressure_plate,
               egg_incubator, lost_colony_bloodforge, lost_colony_cryo_hospital, lost_colony_medical_stand,
               lost_colony_shoulder_pet_display_stand, lost_colony_warbench, coffin, drawing_sheet,
               saloon_piano, wall_scaffolding, shootable_bottle, town_bell, treasure_cache_asa, windmill,
               steampunk_clock, embryo_incubator, gene_infuser, industrial_preservin_bin, library_storage,
               linked_storage, tesla_coil, bounty_board, cargo_ledger_tof, fishtank_tof, market, bio_grinder,
               garage, tribe_tower, elevator_platform_large, elevator_platform_medium,
               elevator_platform_small, elevator_track_base, reverse_vacuum_comparment, underwater_base,
               christmas_tree, snowman, stocking, wreath, easter_egg, hw_grave, pumpkin, scarecrow,
               training_dummy, air_conditioner, bear_trap, bear_trap_large, beer_barrel, cannon,
               feeding_trough, fireplace, grinder, keypad, painting_canvas, preserving_bin, sea_mine,
               sleeping_bag_hide, trophy_base, trophy_wall, power_generator, toilet, tree_tap, fish_basket,
               rope_ladder, war_map, wardrums, bee_hive, display_case, birthday_cake, wreath_flower,
               fish_mount_coel, fish_mount_piranha, fish_mount_salmon, shark_jaws_trophy, mirror, vessel,
               oil_pump, tent, water_well, wind_turbine]

class StructureItems:
    adobe: Adobe = Adobe()
    greenhouse: Greenhouse = Greenhouse()
    stone: Stone = Stone()
    metal: Metal = Metal()
    wood: Wood = Wood()
    thatch: Thatch = Thatch()
    tek: Tek = Tek()
    turrets: Turrets = Turrets()
    water: Water = Water()
    crafting: Crafting = Crafting()
    taxidermy: Taxidermy = Taxidermy()
    flags: Flags = Flags()
    signs: Signs = Signs()
    lights: Lights = Lights()
    storage: Storage = Storage()
    furniture: Furniture = Furniture()
    plants: Plants = Plants()
    ships: Ships = Ships()
    misc: Misc = Misc()

    all_bps = adobe.all_bps + greenhouse.all_bps + stone.all_bps + metal.all_bps + wood.all_bps + \
        thatch.all_bps + tek.all_bps + turrets.all_bps + water.all_bps + crafting.all_bps + \
        taxidermy.all_bps + flags.all_bps + signs.all_bps + lights.all_bps + storage.all_bps + \
        furniture.all_bps + plants.all_bps + ships.all_bps + misc.all_bps
