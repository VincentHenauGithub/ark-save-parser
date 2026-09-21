"""World actors: loot drops, boss arenas, mission managers and vehicles."""

class SupplyCrates:
    element_wall_horde: str = "/Game/Extinction/CoreBlueprints/HordeCrates/ElementWall_Horde.ElementWall_Horde_C"
    element_wall_horde_2: str = "/Game/Extinction/CoreBlueprints/HordeCrates/ElementWall_Horde_2.ElementWall_Horde_2_C"
    element_wall_horde_3: str = "/Game/Extinction/CoreBlueprints/HordeCrates/ElementWall_Horde_3.ElementWall_Horde_3_C"
    element_wall_horde_2_astraeos: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/HordeCrates/ElementWall_Horde_2_Astraeos.ElementWall_Horde_2_Astraeos_C"
    element_wall_horde_3_astraeos: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/HordeCrates/ElementWall_Horde_3_Astraeos.ElementWall_Horde_3_Astraeos_C"
    element_wall_horde_astraeos: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/HordeCrates/ElementWall_Horde_Astraeos.ElementWall_Horde_Astraeos_C"
    base_bp_instantaneous_den_logs_child2: str = "/Game/Mods/Ragnarok/Custom_Assets/Environment/BeaverDam/SupplyCrateBaseBP_Instantaneous_DenLogs_Child2.SupplyCrateBaseBP_Instantaneous_DenLogs_Child2_C"

    all_bps = [element_wall_horde, element_wall_horde_2, element_wall_horde_3, element_wall_horde_2_astraeos,
               element_wall_horde_3_astraeos, element_wall_horde_astraeos,
               base_bp_instantaneous_den_logs_child2]

class ArtifactCrates:
    artifact_crate_2_ab: str = "/Game/Aberration/CoreBlueprints/ItemLootSets/SupplyCrate/ArtifactCrate_2_AB.ArtifactCrate_2_AB_C"
    artifact_crate_3_ab: str = "/Game/Aberration/CoreBlueprints/ItemLootSets/SupplyCrate/ArtifactCrate_3_AB.ArtifactCrate_3_AB_C"
    artifact_crate_ab: str = "/Game/Aberration/CoreBlueprints/ItemLootSets/SupplyCrate/ArtifactCrate_AB.ArtifactCrate_AB_C"
    desert_kaiju_ex: str = "/Game/Extinction/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_Desert_Kaiju_EX.ArtifactCrate_Desert_Kaiju_EX_C"
    forest_kaiju_ex: str = "/Game/Extinction/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_ForestKaiju_EX.ArtifactCrate_ForestKaiju_EX_C"
    ice_kaiju_ex: str = "/Game/Extinction/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_IceKaiju_EX.ArtifactCrate_IceKaiju_EX_C"
    artifact_crate_1: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_1.ArtifactCrate_1_C"
    artifact_crate_10: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_10.ArtifactCrate_10_C"
    artifact_crate_11: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_11.ArtifactCrate_11_C"
    artifact_crate_2: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_2.ArtifactCrate_2_C"
    artifact_crate_3: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_3.ArtifactCrate_3_C"
    artifact_crate_4: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_4.ArtifactCrate_4_C"
    artifact_crate_5: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_5.ArtifactCrate_5_C"
    artifact_crate_6: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_6.ArtifactCrate_6_C"
    artifact_crate_7: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_7.ArtifactCrate_7_C"
    artifact_crate_8: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_8.ArtifactCrate_8_C"
    artifact_crate_9: str = "/Game/PrimalEarth/Structures/ArtifactCrates/ArtifactCrate_9.ArtifactCrate_9_C"
    artifact_crate_2_se: str = "/Game/ScorchedEarth/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_2_SE.ArtifactCrate_2_SE_C"
    artifact_crate_3_se: str = "/Game/ScorchedEarth/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_3_SE.ArtifactCrate_3_SE_C"
    artifact_crate_se: str = "/Game/ScorchedEarth/CoreBlueprints/ItemLootSets/SupplyCrates/ArtifactCrate_SE.ArtifactCrate_SE_C"

    all_bps = [artifact_crate_2_ab, artifact_crate_3_ab, artifact_crate_ab, desert_kaiju_ex, forest_kaiju_ex,
               ice_kaiju_ex, artifact_crate_1, artifact_crate_10, artifact_crate_11, artifact_crate_2,
               artifact_crate_3, artifact_crate_4, artifact_crate_5, artifact_crate_6, artifact_crate_7,
               artifact_crate_8, artifact_crate_9, artifact_crate_2_se, artifact_crate_3_se, artifact_crate_se]

class DroppedItems:
    generic_fertilized_egg_rock_drake: str = "/Game/Aberration/Dinos/RockDrake/DroppedItemGeneric_FertilizedEgg_RockDrake.DroppedItemGeneric_FertilizedEgg_RockDrake_C"
    generic_fertilized_egg_rock_drake_no_physics: str = "/Game/Aberration/Dinos/RockDrake/DroppedItemGeneric_FertilizedEgg_RockDrake_NoPhysics.DroppedItemGeneric_FertilizedEgg_RockDrake_NoPhysics_C"
    gacha_pod: str = "/Game/Extinction/Dinos/Gacha/DroppedItem_GachaPod.DroppedItem_GachaPod_C"
    generic_fertilized_egg_no_physics_cherufe: str = "/Game/Genesis/Dinos/Cherufe/DroppedItemGeneric_FertilizedEgg_NoPhysicsCherufe.DroppedItemGeneric_FertilizedEgg_NoPhysicsCherufe_C"
    generic: str = "/Game/PrimalEarth/Test/DroppedItemGeneric.DroppedItemGeneric_C"
    generic_fertilized_egg_no_physics_wyvern: str = "/Game/PrimalEarth/Test/DroppedItemGeneric_FertilizedEgg_NoPhysicsWyvern.DroppedItemGeneric_FertilizedEgg_NoPhysicsWyvern_C"
    generic_fertilized_egg_wyvern: str = "/Game/PrimalEarth/Test/DroppedItemGeneric_FertilizedEgg_Wyvern.DroppedItemGeneric_FertilizedEgg_Wyvern_C"
    generic_unfertilized_egg: str = "/Game/PrimalEarth/Test/DroppedItemGeneric_UnfertilizedEgg.DroppedItemGeneric_UnfertilizedEgg_C"

    all_bps = [generic_fertilized_egg_rock_drake, generic_fertilized_egg_rock_drake_no_physics, gacha_pod,
               generic_fertilized_egg_no_physics_cherufe, generic, generic_fertilized_egg_no_physics_wyvern,
               generic_fertilized_egg_wyvern, generic_unfertilized_egg]

class Nests:
    gigantoraptor: str = "/Game/ASA/Dinos/Gigantoraptor/Nest/GigantoraptorNest.GigantoraptorNest_C"
    rock_drake: str = "/Game/Aberration/Dinos/RockDrake/RockDrakeNest.RockDrakeNest_C"
    cherufe: str = "/Game/Genesis/Dinos/Cherufe/CherufeNest.CherufeNest_C"
    wyvern: str = "/Game/ScorchedEarth/Dinos/Wyvern/WyvernNest.WyvernNest_C"

    all_bps = [gigantoraptor, rock_drake, cherufe, wyvern]

class BossArenas:
    rag_wyv_boss: str = "/Game/ASA/Dinos/IceWyvern/Boss/BossArenaManager_RagWyvBoss.BossArenaManager_RagWyvBoss_C"
    rockwell: str = "/Game/Aberration/Boss/Rockwell/BossArenaManager_Rockwell.BossArenaManager_Rockwell_C"
    desert: str = "/Game/Extinction/CoreBlueprints/Tribute/BossArenaManager_Desert.BossArenaManager_Desert_C"
    boss_arena_manager_fz: str = "/Game/Extinction/CoreBlueprints/Tribute/BossArenaManager_FZ.BossArenaManager_FZ_C"
    forest: str = "/Game/Extinction/CoreBlueprints/Tribute/BossArenaManager_Forest.BossArenaManager_Forest_C"
    snow: str = "/Game/Extinction/CoreBlueprints/Tribute/BossArenaManager_Snow.BossArenaManager_Snow_C"
    eel_boss_fight: str = "/Game/Genesis/Missions/EelBossFight/BossArenaManager_EelBossFight.BossArenaManager_EelBossFight_C"
    cyclops: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/BossArenaManager_Cyclops.BossArenaManager_Cyclops_C"
    medusa: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/BossArenaManager_Medusa.BossArenaManager_Medusa_C"
    dragon: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_Dragon.BossArenaManager_Dragon_C"
    end_boss: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_EndBoss.BossArenaManager_EndBoss_C"
    gorilla: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_Gorilla.BossArenaManager_Gorilla_C"
    manticore: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_Manticore.BossArenaManager_Manticore_C"
    spider: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_Spider.BossArenaManager_Spider_C"
    two_bosses_spider_gorilla: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_TwoBosses_SpiderGorilla.BossArenaManager_TwoBosses_SpiderGorilla_C"
    two_bosses_spider_gorilla_hard: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_TwoBosses_SpiderGorillaHard.BossArenaManager_TwoBosses_SpiderGorillaHard_C"
    two_bosses_spider_gorilla_medium: str = "/Game/PrimalEarth/CoreBlueprints/BossTribute/BossArenaManager_TwoBosses_SpiderGorillaMedium.BossArenaManager_TwoBosses_SpiderGorillaMedium_C"

    all_bps = [rag_wyv_boss, rockwell, desert, boss_arena_manager_fz, forest, snow, eel_boss_fight, cyclops,
               medusa, dragon, end_boss, gorilla, manticore, spider, two_bosses_spider_gorilla,
               two_bosses_spider_gorilla_hard, two_bosses_spider_gorilla_medium]

class Missions:
    gen_outpost_base: str = "/Game/Genesis/Missions/Ocean/Outpost/Manager/MissionManager_Gen_Outpost_Base.MissionManager_Gen_Outpost_Base_C"
    npc_zone_manager_patrols: str = "/Game/LostColony/CoreBlueprints/Patrols/NPCZoneManager_Patrols.NPCZoneManager_Patrols_C"
    lc_bossfight: str = "/Game/LostColony/Missions/Bossfight/MissionDispatcher_LC_Bossfight.MissionDispatcher_LC_Bossfight_C"
    lc_overworld_base: str = "/Game/LostColony/Missions/Overworld/Manager/MissionManager_LC_Overworld_Base.MissionManager_LC_Overworld_Base_C"
    npc_zone_manager_blueprint_cave: str = "/Game/PrimalEarth/CoreBlueprints/NPCZoneManagerBlueprint_Cave.NPCZoneManagerBlueprint_Cave_C"
    npc_zone_manager_blueprint_land: str = "/Game/PrimalEarth/CoreBlueprints/NPCZoneManagerBlueprint_Land.NPCZoneManagerBlueprint_Land_C"
    npc_zone_manager_blueprint_land_world_boss: str = "/Game/PrimalEarth/CoreBlueprints/NPCZoneManagerBlueprint_Land_WorldBoss.NPCZoneManagerBlueprint_Land_WorldBoss_C"
    npc_zone_manager_blueprint_water: str = "/Game/PrimalEarth/CoreBlueprints/NPCZoneManagerBlueprint_Water.NPCZoneManagerBlueprint_Water_C"

    all_bps = [gen_outpost_base, npc_zone_manager_patrols, lc_bossfight, lc_overworld_base,
               npc_zone_manager_blueprint_cave, npc_zone_manager_blueprint_land,
               npc_zone_manager_blueprint_land_world_boss, npc_zone_manager_blueprint_water]

class DayCycles:
    aberration: str = "/Game/Aberration/CoreBlueprints/AberrationDayCycle.AberrationDayCycle_C"
    extinction: str = "/Game/Extinction/CoreBlueprints/ExtinctionDayCycle.ExtinctionDayCycle_C"
    manager_genesis: str = "/Game/Genesis/CoreBlueprints/Environment/DayCycleManager_Genesis.DayCycleManager_Genesis_C"
    lc_day_cycle: str = "/Game/LostColony/CoreBlueprints/Weather/LC_DayCycle.LC_DayCycle_C"
    manager_astraeos: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/DayCycleManager_Astraeos.DayCycleManager_Astraeos_C"
    rag: str = "/Game/Mods/Ragnarok/Custom_Assets/Weather/Systems/Rag_DayCycle.Rag_DayCycle_C"
    manager: str = "/Game/PrimalEarth/CoreBlueprints/DCM/DayCycleManager.DayCycleManager_C"
    scorched_earth: str = "/Game/ScorchedEarth/CoreBlueprints/Core/ScorchedEarthDayCycle.ScorchedEarthDayCycle_C"

    all_bps = [aberration, extinction, manager_genesis, lc_day_cycle, manager_astraeos, rag, manager,
               scorched_earth]

class Vehicles:
    portable_rope_ladder_zeppelin: str = "/Game/Packs/Steampunk/Dinos/Zeppelin/PortableRope_Ladder_Zeppelin.PortableRope_Ladder_Zeppelin_C"
    portable_rope_ladder_zeppelin_back: str = "/Game/Packs/Steampunk/Dinos/Zeppelin/PortableRope_Ladder_Zeppelin_Back.PortableRope_Ladder_Zeppelin_Back_C"
    car_vehicle_bp: str = "/Game/Packs/Wasteland/Vehicles/Car/Car_Vehicle_BP.Car_Vehicle_BP_C"
    motor_raft_bp: str = "/Game/PrimalEarth/Items/Raft/MotorRaft_BP.MotorRaft_BP_C"
    raft_bp: str = "/Game/PrimalEarth/Items/Raft/Raft_BP.Raft_BP_C"
    brig_ship_player_following_bp_miniboss: str = "/Game/Water/Vessels/Brig/BrigShipPlayerFollowingBP_Miniboss.BrigShipPlayerFollowingBP_Miniboss_C"

    all_bps = [portable_rope_ladder_zeppelin, portable_rope_ladder_zeppelin_back, car_vehicle_bp,
               motor_raft_bp, raft_bp, brig_ship_player_following_bp_miniboss]

class Misc:
    hero_poison_plant: str = "/Game/Genesis/Environment/Bog/Vegetation/Foliage/PoisonPlant/BP_HeroPoisonPlant.BP_HeroPoisonPlant_C"
    gas_vein_base_bp_lc: str = "/Game/LostColony/Environment/Resources/GasVein_Base_BP_LC.GasVein_Base_BP_LC_C"

    all_bps = [hero_poison_plant, gas_vein_base_bp_lc]

class World:
    supply_crates: SupplyCrates = SupplyCrates()
    artifact_crates: ArtifactCrates = ArtifactCrates()
    dropped_items: DroppedItems = DroppedItems()
    nests: Nests = Nests()
    boss_arenas: BossArenas = BossArenas()
    missions: Missions = Missions()
    day_cycles: DayCycles = DayCycles()
    vehicles: Vehicles = Vehicles()
    misc: Misc = Misc()

    all_bps = supply_crates.all_bps + artifact_crates.all_bps + dropped_items.all_bps + nests.all_bps + \
        boss_arenas.all_bps + missions.all_bps + day_cycles.all_bps + vehicles.all_bps + \
        misc.all_bps
