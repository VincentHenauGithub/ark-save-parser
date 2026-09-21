"""Remaining inventory items, container inventories and buffs."""

class ItemTraits:
    armor_ammo_on_hit: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_AmmoOnHit.PrimalItem_ItemTrait_Armor_AmmoOnHit_C"
    armor_ammo_on_hit_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_AmmoOnHit_Lesser.PrimalItem_ItemTrait_Armor_AmmoOnHit_Lesser_C"
    armor_ammo_on_hit_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_AmmoOnHit_Moderate.PrimalItem_ItemTrait_Armor_AmmoOnHit_Moderate_C"
    armor_increased_incoming_healing: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing.PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing_C"
    armor_increased_incoming_healing_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing_Lesser.PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing_Lesser_C"
    armor_increased_incoming_healing_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing_Moderate.PrimalItem_ItemTrait_Armor_IncreasedIncomingHealing_Moderate_C"
    armor_marathon: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Marathon.PrimalItem_ItemTrait_Armor_Marathon_C"
    armor_marathon_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Marathon_Lesser.PrimalItem_ItemTrait_Armor_Marathon_Lesser_C"
    armor_marathon_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Marathon_Moderate.PrimalItem_ItemTrait_Armor_Marathon_Moderate_C"
    armor_mobile: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Mobile.PrimalItem_ItemTrait_Armor_Mobile_C"
    armor_mobile_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Mobile_Lesser.PrimalItem_ItemTrait_Armor_Mobile_Lesser_C"
    armor_mobile_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_Mobile_Moderate.PrimalItem_ItemTrait_Armor_Mobile_Moderate_C"
    armor_reduced_debuff_duration: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_ReducedDebuffDuration.PrimalItem_ItemTrait_Armor_ReducedDebuffDuration_C"
    armor_reduced_debuff_duration_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_ReducedDebuffDuration_Lesser.PrimalItem_ItemTrait_Armor_ReducedDebuffDuration_Lesser_C"
    armor_reduced_debuff_duration_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Armor_ReducedDebuffDuration_Moderate.PrimalItem_ItemTrait_Armor_ReducedDebuffDuration_Moderate_C"
    gun_cannibalizing: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Cannibalizing.PrimalItem_ItemTrait_Gun_Cannibalizing_C"
    gun_cannibalizing_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Cannibalizing_Lesser.PrimalItem_ItemTrait_Gun_Cannibalizing_Lesser_C"
    gun_cannibalizing_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Cannibalizing_Moderate.PrimalItem_ItemTrait_Gun_Cannibalizing_Moderate_C"
    gun_focusing: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Focusing.PrimalItem_ItemTrait_Gun_Focusing_C"
    gun_focusing_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Focusing_Lesser.PrimalItem_ItemTrait_Gun_Focusing_Lesser_C"
    gun_focusing_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Focusing_Moderate.PrimalItem_ItemTrait_Gun_Focusing_Moderate_C"
    gun_reduced_damage_on_hit: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_ReducedDamageOnHit.PrimalItem_ItemTrait_Gun_ReducedDamageOnHit_C"
    gun_reduced_damage_on_hit_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_ReducedDamageOnHit_Lesser.PrimalItem_ItemTrait_Gun_ReducedDamageOnHit_Lesser_C"
    gun_reduced_damage_on_hit_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_ReducedDamageOnHit_Moderate.PrimalItem_ItemTrait_Gun_ReducedDamageOnHit_Moderate_C"
    gun_ricochet: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Ricochet.PrimalItem_ItemTrait_Gun_Ricochet_C"
    gun_ricochet_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Ricochet_Lesser.PrimalItem_ItemTrait_Gun_Ricochet_Lesser_C"
    gun_ricochet_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Ricochet_Moderate.PrimalItem_ItemTrait_Gun_Ricochet_Moderate_C"
    gun_tracker: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Tracker.PrimalItem_ItemTrait_Gun_Tracker_C"
    gun_tracker_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Tracker_Lesser.PrimalItem_ItemTrait_Gun_Tracker_Lesser_C"
    gun_tracker_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Gun_Tracker_Moderate.PrimalItem_ItemTrait_Gun_Tracker_Moderate_C"
    melee_heal_on_damage: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_HealOnDamage.PrimalItem_ItemTrait_Melee_HealOnDamage_C"
    melee_heal_on_damage_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_HealOnDamage_Lesser.PrimalItem_ItemTrait_Melee_HealOnDamage_Lesser_C"
    melee_heal_on_damage_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_HealOnDamage_Moderate.PrimalItem_ItemTrait_Melee_HealOnDamage_Moderate_C"
    melee_increased_damage_from_behind: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind.PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind_C"
    melee_increased_damage_from_behind_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind_Lesser.PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind_Lesser_C"
    melee_increased_damage_from_behind_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind_Moderate.PrimalItem_ItemTrait_Melee_IncreasedDamageFromBehind_Moderate_C"
    melee_increased_damage_to_non_living: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving.PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving_C"
    melee_increased_damage_to_non_living_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving_Lesser.PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving_Lesser_C"
    melee_increased_damage_to_non_living_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving_Moderate.PrimalItem_ItemTrait_Melee_IncreasedDamageToNonLiving_Moderate_C"
    melee_increased_speed_and_damage_taken: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken.PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken_C"
    melee_increased_speed_and_damage_taken_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken_Lesser.PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken_Lesser_C"
    melee_increased_speed_and_damage_taken_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken_Moderate.PrimalItem_ItemTrait_Melee_IncreasedSpeedAndDamageTaken_Moderate_C"
    melee_shield_on_hit: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_ShieldOnHit.PrimalItem_ItemTrait_Melee_ShieldOnHit_C"
    melee_shield_on_hit_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_ShieldOnHit_Lesser.PrimalItem_ItemTrait_Melee_ShieldOnHit_Lesser_C"
    melee_shield_on_hit_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Melee_ShieldOnHit_Moderate.PrimalItem_ItemTrait_Melee_ShieldOnHit_Moderate_C"
    projectile_antigrav: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_Antigrav.PrimalItem_ItemTrait_Projectile_Antigrav_C"
    projectile_antigrav_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_Antigrav_Lesser.PrimalItem_ItemTrait_Projectile_Antigrav_Lesser_C"
    projectile_antigrav_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_Antigrav_Moderate.PrimalItem_ItemTrait_Projectile_Antigrav_Moderate_C"
    projectile_extra_damage_to_vulnerable: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable.PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable_C"
    projectile_extra_damage_to_vulnerable_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable_Lesser.PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable_Lesser_C"
    projectile_extra_damage_to_vulnerable_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable_Moderate.PrimalItem_ItemTrait_Projectile_ExtraDamageToVulnerable_Moderate_C"
    projectile_increased_damage_to_alpha: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha.PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha_C"
    projectile_increased_damage_to_alpha_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha_Lesser.PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha_Lesser_C"
    projectile_increased_damage_to_alpha_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha_Moderate.PrimalItem_ItemTrait_Projectile_IncreasedDamageToAlpha_Moderate_C"
    projectile_increased_first_hit_damage: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage.PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage_C"
    projectile_increased_first_hit_damage_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage_Lesser.PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage_Lesser_C"
    projectile_increased_first_hit_damage_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage_Moderate.PrimalItem_ItemTrait_Projectile_IncreasedFirstHitDamage_Moderate_C"
    projectile_second_projectile: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_SecondProjectile.PrimalItem_ItemTrait_Projectile_SecondProjectile_C"
    projectile_second_projectile_lesser: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_SecondProjectile_Lesser.PrimalItem_ItemTrait_Projectile_SecondProjectile_Lesser_C"
    projectile_second_projectile_moderate: str = "/Game/Packs/Wasteland/CoreBlueprints/ItemTraits/Items/PrimalItem_ItemTrait_Projectile_SecondProjectile_Moderate.PrimalItem_ItemTrait_Projectile_SecondProjectile_Moderate_C"

    all_bps = [armor_ammo_on_hit, armor_ammo_on_hit_lesser, armor_ammo_on_hit_moderate,
               armor_increased_incoming_healing, armor_increased_incoming_healing_lesser,
               armor_increased_incoming_healing_moderate, armor_marathon, armor_marathon_lesser,
               armor_marathon_moderate, armor_mobile, armor_mobile_lesser, armor_mobile_moderate,
               armor_reduced_debuff_duration, armor_reduced_debuff_duration_lesser,
               armor_reduced_debuff_duration_moderate, gun_cannibalizing, gun_cannibalizing_lesser,
               gun_cannibalizing_moderate, gun_focusing, gun_focusing_lesser, gun_focusing_moderate,
               gun_reduced_damage_on_hit, gun_reduced_damage_on_hit_lesser,
               gun_reduced_damage_on_hit_moderate, gun_ricochet, gun_ricochet_lesser, gun_ricochet_moderate,
               gun_tracker, gun_tracker_lesser, gun_tracker_moderate, melee_heal_on_damage,
               melee_heal_on_damage_lesser, melee_heal_on_damage_moderate, melee_increased_damage_from_behind,
               melee_increased_damage_from_behind_lesser, melee_increased_damage_from_behind_moderate,
               melee_increased_damage_to_non_living, melee_increased_damage_to_non_living_lesser,
               melee_increased_damage_to_non_living_moderate, melee_increased_speed_and_damage_taken,
               melee_increased_speed_and_damage_taken_lesser, melee_increased_speed_and_damage_taken_moderate,
               melee_shield_on_hit, melee_shield_on_hit_lesser, melee_shield_on_hit_moderate,
               projectile_antigrav, projectile_antigrav_lesser, projectile_antigrav_moderate,
               projectile_extra_damage_to_vulnerable, projectile_extra_damage_to_vulnerable_lesser,
               projectile_extra_damage_to_vulnerable_moderate, projectile_increased_damage_to_alpha,
               projectile_increased_damage_to_alpha_lesser, projectile_increased_damage_to_alpha_moderate,
               projectile_increased_first_hit_damage, projectile_increased_first_hit_damage_lesser,
               projectile_increased_first_hit_damage_moderate, projectile_second_projectile,
               projectile_second_projectile_lesser, projectile_second_projectile_moderate]

class BossTributes:
    rag_wyv_boss_easy: str = "/Game/ASA/Dinos/IceWyvern/Boss/PrimalItem_BossTribute_RagWyvBoss_Easy.PrimalItem_BossTribute_RagWyvBoss_Easy_C"
    rag_wyv_boss_hard: str = "/Game/ASA/Dinos/IceWyvern/Boss/PrimalItem_BossTribute_RagWyvBoss_Hard.PrimalItem_BossTribute_RagWyvBoss_Hard_C"
    rag_wyv_boss_medium: str = "/Game/ASA/Dinos/IceWyvern/Boss/PrimalItem_BossTribute_RagWyvBoss_Medium.PrimalItem_BossTribute_RagWyvBoss_Medium_C"
    aberration_easy: str = "/Game/Aberration/CoreBlueprints/Items/PrimalItem_BossTribute_Aberration_Easy.PrimalItem_BossTribute_Aberration_Easy_C"
    aberration_hard: str = "/Game/Aberration/CoreBlueprints/Items/PrimalItem_BossTribute_Aberration_Hard.PrimalItem_BossTribute_Aberration_Hard_C"
    aberration_medium: str = "/Game/Aberration/CoreBlueprints/Items/PrimalItem_BossTribute_Aberration_Medium.PrimalItem_BossTribute_Aberration_Medium_C"
    desert_kaiju: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_DesertKaiju.PrimalItem_BossTribute_DesertKaiju_C"
    forest_kaiju: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_ForestKaiju.PrimalItem_BossTribute_ForestKaiju_C"
    ice_kaiju: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_IceKaiju.PrimalItem_BossTribute_IceKaiju_C"
    king_kaiju_easy: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_KingKaijuEasy.PrimalItem_BossTribute_KingKaijuEasy_C"
    king_kaiju_hard: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_KingKaijuHard.PrimalItem_BossTribute_KingKaijuHard_C"
    king_kaiju_medium: str = "/Game/Extinction/CoreBlueprints/Items/Tribute/PrimalItem_BossTribute_KingKaijuMedium.PrimalItem_BossTribute_KingKaijuMedium_C"
    final_battle_easy: str = "/Game/LostColony/CoreBlueprints/Items/PrimalItem_BossTribute_FinalBattle_Easy.PrimalItem_BossTribute_FinalBattle_Easy_C"
    final_battle_easy_hard: str = "/Game/LostColony/CoreBlueprints/Items/PrimalItem_BossTribute_FinalBattle_Easy_Hard.PrimalItem_BossTribute_FinalBattle_Easy_Hard_C"
    final_battle_easy_medium: str = "/Game/LostColony/CoreBlueprints/Items/PrimalItem_BossTribute_FinalBattle_Easy_Medium.PrimalItem_BossTribute_FinalBattle_Easy_Medium_C"
    boars: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Boars.PrimalItem_BossTribute_Boars_C"
    cyclops_easy: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Cyclops_Easy.PrimalItem_BossTribute_Cyclops_Easy_C"
    cyclops_hard: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Cyclops_Hard.PrimalItem_BossTribute_Cyclops_Hard_C"
    cyclops_medium: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Cyclops_Medium.PrimalItem_BossTribute_Cyclops_Medium_C"
    medusa_easy: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Medusa_Easy.PrimalItem_BossTribute_Medusa_Easy_C"
    medusa_hard: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Medusa_Hard.PrimalItem_BossTribute_Medusa_Hard_C"
    medusa_medium: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/BossTribute/PrimalItem_BossTribute_Medusa_Medium.PrimalItem_BossTribute_Medusa_Medium_C"
    dragon_easy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Dragon_Easy.PrimalItem_BossTribute_Dragon_Easy_C"
    dragon_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Dragon_Hard.PrimalItem_BossTribute_Dragon_Hard_C"
    dragon_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Dragon_Medium.PrimalItem_BossTribute_Dragon_Medium_C"
    gorilla_easy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Gorilla_Easy.PrimalItem_BossTribute_Gorilla_Easy_C"
    gorilla_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Gorilla_Hard.PrimalItem_BossTribute_Gorilla_Hard_C"
    gorilla_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Gorilla_Medium.PrimalItem_BossTribute_Gorilla_Medium_C"
    manticore_easy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Manticore_Easy.PrimalItem_BossTribute_Manticore_Easy_C"
    manticore_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Manticore_Hard.PrimalItem_BossTribute_Manticore_Hard_C"
    manticore_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Manticore_Medium.PrimalItem_BossTribute_Manticore_Medium_C"
    spider_easy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Spider_Easy.PrimalItem_BossTribute_Spider_Easy_C"
    spider_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Spider_Hard.PrimalItem_BossTribute_Spider_Hard_C"
    spider_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_Spider_Medium.PrimalItem_BossTribute_Spider_Medium_C"
    the_center: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_TheCenter.PrimalItem_BossTribute_TheCenter_C"
    the_center_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_TheCenter_Hard.PrimalItem_BossTribute_TheCenter_Hard_C"
    the_center_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_BossTribute_TheCenter_Medium.PrimalItem_BossTribute_TheCenter_Medium_C"

    all_bps = [rag_wyv_boss_easy, rag_wyv_boss_hard, rag_wyv_boss_medium, aberration_easy, aberration_hard,
               aberration_medium, desert_kaiju, forest_kaiju, ice_kaiju, king_kaiju_easy, king_kaiju_hard,
               king_kaiju_medium, final_battle_easy, final_battle_easy_hard, final_battle_easy_medium, boars,
               cyclops_easy, cyclops_hard, cyclops_medium, medusa_easy, medusa_hard, medusa_medium,
               dragon_easy, dragon_hard, dragon_medium, gorilla_easy, gorilla_hard, gorilla_medium,
               manticore_easy, manticore_hard, manticore_medium, spider_easy, spider_hard, spider_medium,
               the_center, the_center_hard, the_center_medium]

class VehicleParts:
    train_car_platform: str = "/Game/Packs/Frontier/Structures/TrainCarts/PrimalItem_TrainCar_Platform.PrimalItem_TrainCar_Platform_C"
    craft_brig: str = "/Game/Packs/TidesOfFortune/Vehicles/Brigantine/PrimalItemShip_Craft_Brig.PrimalItemShip_Craft_Brig_C"
    craft_galleon: str = "/Game/Packs/TidesOfFortune/Vehicles/Galleon/PrimalItemShip_Craft_Galleon.PrimalItemShip_Craft_Galleon_C"
    craft_sloop: str = "/Game/Packs/TidesOfFortune/Vehicles/Sloop/PrimalItemShip_Craft_Sloop.PrimalItemShip_Craft_Sloop_C"
    bed_racer: str = "/Game/Packs/Wasteland/Vehicles/Car/Bed/Racer/PrimalItem_Car_Bed_Racer.PrimalItem_Car_Bed_Racer_C"
    bed_rollcage: str = "/Game/Packs/Wasteland/Vehicles/Car/Bed/Rollcage/PrimalItem_Car_Bed_Rollcage.PrimalItem_Car_Bed_Rollcage_C"
    bed_truck: str = "/Game/Packs/Wasteland/Vehicles/Car/Bed/Truck/PrimalItem_Car_Bed_Truck.PrimalItem_Car_Bed_Truck_C"
    cab_racer: str = "/Game/Packs/Wasteland/Vehicles/Car/Cab/Racer/PrimalItem_Car_Cab_Racer.PrimalItem_Car_Cab_Racer_C"
    cab_rollcage: str = "/Game/Packs/Wasteland/Vehicles/Car/Cab/Rollcage/PrimalItem_Car_Cab_Rollcage.PrimalItem_Car_Cab_Rollcage_C"
    cab_truck: str = "/Game/Packs/Wasteland/Vehicles/Car/Cab/Truck/PrimalItem_Car_Cab_Truck.PrimalItem_Car_Cab_Truck_C"
    chassis_main: str = "/Game/Packs/Wasteland/Vehicles/Car/Chassis/Main/PrimalItem_Car_Chassis_Main.PrimalItem_Car_Chassis_Main_C"
    engine_racer: str = "/Game/Packs/Wasteland/Vehicles/Car/EngineCompartment/Racer/PrimalItem_Car_Engine_Racer.PrimalItem_Car_Engine_Racer_C"
    engine_rollcage: str = "/Game/Packs/Wasteland/Vehicles/Car/EngineCompartment/Rollcage/PrimalItem_Car_Engine_Rollcage.PrimalItem_Car_Engine_Rollcage_C"
    engine_truck: str = "/Game/Packs/Wasteland/Vehicles/Car/EngineCompartment/Truck/PrimalItem_Car_Engine_Truck.PrimalItem_Car_Engine_Truck_C"
    frontmod_armor: str = "/Game/Packs/Wasteland/Vehicles/Car/FrontEndMod/Armor/PrimalItem_Car_Frontmod_Armor.PrimalItem_Car_Frontmod_Armor_C"
    frontmod_buzzsaw: str = "/Game/Packs/Wasteland/Vehicles/Car/FrontEndMod/Buzzsaw/PrimalItem_Car_Frontmod_Buzzsaw.PrimalItem_Car_Frontmod_Buzzsaw_C"
    frontmod_cow_catcher: str = "/Game/Packs/Wasteland/Vehicles/Car/FrontEndMod/CowCatcher/PrimalItem_Car_Frontmod_CowCatcher.PrimalItem_Car_Frontmod_CowCatcher_C"
    frontmod_spikes: str = "/Game/Packs/Wasteland/Vehicles/Car/FrontEndMod/Spikes/PrimalItem_Car_Frontmod_Spikes.PrimalItem_Car_Frontmod_Spikes_C"
    rearmod_afterburner: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/Afterburner/PrimalItem_Car_Rearmod_Afterburner.PrimalItem_Car_Rearmod_Afterburner_C"
    rearmod_hook: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/Hook/PrimalItem_Car_Rearmod_Hook.PrimalItem_Car_Rearmod_Hook_C"
    rearmod_jump: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/JumpJet/PrimalItem_Car_Rearmod_Jump.PrimalItem_Car_Rearmod_Jump_C"
    rearmod_mines: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/Mines/PrimalItem_Car_Rearmod_Mines.PrimalItem_Car_Rearmod_Mines_C"
    rearmod_sludge: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/Sludge/PrimalItem_Car_Rearmod_Sludge.PrimalItem_Car_Rearmod_Sludge_C"
    rearmod_smoke: str = "/Game/Packs/Wasteland/Vehicles/Car/RearEndMod/Smoke/PrimalItem_Car_Rearmod_Smoke.PrimalItem_Car_Rearmod_Smoke_C"
    turret_cannon: str = "/Game/Packs/Wasteland/Vehicles/Car/Turret/Cannon/PrimalItem_Car_Turret_Cannon.PrimalItem_Car_Turret_Cannon_C"
    turret_flamethrower: str = "/Game/Packs/Wasteland/Vehicles/Car/Turret/Flamethrower/PrimalItem_Car_Turret_Flamethrower.PrimalItem_Car_Turret_Flamethrower_C"
    turret_flight_seeker: str = "/Game/Packs/Wasteland/Vehicles/Car/Turret/Flightseeker/PrimalItem_Car_Turret_FlightSeeker.PrimalItem_Car_Turret_FlightSeeker_C"
    turret_minigun: str = "/Game/Packs/Wasteland/Vehicles/Car/Turret/Minigun/PrimalItem_Car_Turret_Minigun.PrimalItem_Car_Turret_Minigun_C"
    turret_shotgun: str = "/Game/Packs/Wasteland/Vehicles/Car/Turret/Shotgun/PrimalItem_Car_Turret_Shotgun.PrimalItem_Car_Turret_Shotgun_C"
    wheels_racer: str = "/Game/Packs/Wasteland/Vehicles/Car/WheelsAndSuspension/Racer/PrimalItem_Car_Wheels_Racer.PrimalItem_Car_Wheels_Racer_C"
    wheels_rollcage: str = "/Game/Packs/Wasteland/Vehicles/Car/WheelsAndSuspension/RollCage/PrimalItem_Car_Wheels_Rollcage.PrimalItem_Car_Wheels_Rollcage_C"
    wheels_truck: str = "/Game/Packs/Wasteland/Vehicles/Car/WheelsAndSuspension/Truck/PrimalItem_Car_Wheels_Truck.PrimalItem_Car_Wheels_Truck_C"
    raft: str = "/Game/PrimalEarth/Items/Raft/PrimalItemRaft.PrimalItemRaft_C"
    craft_trireme: str = "/Game/Water/Vessels/Trireme/PrimalItemShip_Craft_Trireme.PrimalItemShip_Craft_Trireme_C"
    primal_inventory_component_shipyard_large: str = "/Game/Packs/TidesOfFortune/Structures/Shipyard/Gameplay/PrimalInventoryComponent_ShipyardLarge.PrimalInventoryComponent_ShipyardLarge_C"

    all_bps = [train_car_platform, craft_brig, craft_galleon, craft_sloop, bed_racer, bed_rollcage, bed_truck,
               cab_racer, cab_rollcage, cab_truck, chassis_main, engine_racer, engine_rollcage, engine_truck,
               frontmod_armor, frontmod_buzzsaw, frontmod_cow_catcher, frontmod_spikes, rearmod_afterburner,
               rearmod_hook, rearmod_jump, rearmod_mines, rearmod_sludge, rearmod_smoke, turret_cannon,
               turret_flamethrower, turret_flight_seeker, turret_minigun, turret_shotgun, wheels_racer,
               wheels_rollcage, wheels_truck, raft, craft_trireme, primal_inventory_component_shipyard_large]

class Recipes:
    type1: str = "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemCustomDrinkRecipe_Type1.PrimalItemCustomDrinkRecipe_Type1_C"
    type2: str = "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemCustomDrinkRecipe_Type2.PrimalItemCustomDrinkRecipe_Type2_C"
    custom_food_recipe_type1: str = "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemCustomFoodRecipe_Type1.PrimalItemCustomFoodRecipe_Type1_C"
    custom_food_recipe_type2: str = "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemCustomFoodRecipe_Type2.PrimalItemCustomFoodRecipe_Type2_C"
    type3: str = "/Game/PrimalEarth/CoreBlueprints/Items/Consumables/PrimalItemCustomFoodRecipe_Type3.PrimalItemCustomFoodRecipe_Type3_C"
    battle_tartare: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_BattleTartare.PrimalItem_RecipeNote_BattleTartare_C"
    calien_soup: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_CalienSoup.PrimalItem_RecipeNote_CalienSoup_C"
    dye: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_Dye.PrimalItem_RecipeNote_Dye_C"
    enduro_stew: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_EnduroStew.PrimalItem_RecipeNote_EnduroStew_C"
    focal_chili: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_FocalChili.PrimalItem_RecipeNote_FocalChili_C"
    fria_curry: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_FriaCurry.PrimalItem_RecipeNote_FriaCurry_C"
    heal_soup: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_HealSoup.PrimalItem_RecipeNote_HealSoup_C"
    jerky: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_Jerky.PrimalItem_RecipeNote_Jerky_C"
    kibble: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_Kibble.PrimalItem_RecipeNote_Kibble_C"
    lazarus_chowder: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_LazarusChowder.PrimalItem_RecipeNote_LazarusChowder_C"
    measurements: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_Measurements.PrimalItem_RecipeNote_Measurements_C"
    respec_soup: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_RespecSoup.PrimalItem_RecipeNote_RespecSoup_C"
    shadow_steak: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_ShadowSteak.PrimalItem_RecipeNote_ShadowSteak_C"
    stamina_soup: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_RecipeNote_StaminaSoup.PrimalItem_RecipeNote_StaminaSoup_C"

    all_bps = [type1, type2, custom_food_recipe_type1, custom_food_recipe_type2, type3, battle_tartare,
               calien_soup, dye, enduro_stew, focal_chili, fria_curry, heal_soup, jerky, kibble,
               lazarus_chowder, measurements, respec_soup, shadow_steak, stamina_soup]

class RepairKits:
    boots_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_BootsOnly.PrimalItem_RepairKit_BootsOnly_C"
    gloves_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_GlovesOnly.PrimalItem_RepairKit_GlovesOnly_C"
    hat_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_HatOnly.PrimalItem_RepairKit_HatOnly_C"
    pants_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_PantsOnly.PrimalItem_RepairKit_PantsOnly_C"
    shield_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_ShieldOnly.PrimalItem_RepairKit_ShieldOnly_C"
    shirt_only: str = "/Game/ClubARk/Rewards/RepairKit/Armor/PrimalItem_RepairKit_ShirtOnly.PrimalItem_RepairKit_ShirtOnly_C"
    weapons_only: str = "/Game/ClubARk/Rewards/RepairKit/Weapons/PrimalItem_RepairKit_WeaponsOnly.PrimalItem_RepairKit_WeaponsOnly_C"

    all_bps = [boots_only, gloves_only, hat_only, pants_only, shield_only, shirt_only, weapons_only]

class TreasureMaps:
    shoulder_dragon: str = "/Game/ASA/Dinos/ShoulderDragon/Chest/PrimalItem_TreasureMap_ShoulderDragon.PrimalItem_TreasureMap_ShoulderDragon_C"
    treasure_map: str = "/Game/Packs/Frontier/Structures/TreasureCache/TreasureMap/PrimalItem_TreasureMap.PrimalItem_TreasureMap_C"
    wild_supply_drop: str = "/Game/Packs/Frontier/Structures/TreasureCache/TreasureMap/PrimalItem_TreasureMap_WildSupplyDrop.PrimalItem_TreasureMap_WildSupplyDrop_C"
    wild_bottle_s1_gen1: str = "/Game/Packs/TidesOfFortune/Items/Tools/TreasureMapBottle/PrimalItem_TreasureMap_Wild_Bottle_S1_Gen1.PrimalItem_TreasureMap_Wild_Bottle_S1_Gen1_C"
    wild_bottle_s2_gen1: str = "/Game/Packs/TidesOfFortune/Items/Tools/TreasureMapBottle/PrimalItem_TreasureMap_Wild_Bottle_S2_Gen1.PrimalItem_TreasureMap_Wild_Bottle_S2_Gen1_C"
    wild_bottle_s3_gen1: str = "/Game/Packs/TidesOfFortune/Items/Tools/TreasureMapBottle/PrimalItem_TreasureMap_Wild_Bottle_S3_Gen1.PrimalItem_TreasureMap_Wild_Bottle_S3_Gen1_C"

    all_bps = [shoulder_dragon, treasure_map, wild_supply_drop, wild_bottle_s1_gen1, wild_bottle_s2_gen1,
               wild_bottle_s3_gen1]

class Inventories:
    gas_collector: str = "/Game/Aberration/CoreBlueprints/Inventories/PrimalInventoryBP_GasCollector.PrimalInventoryBP_GasCollector_C"
    primal_inventory_component_bp_city_terminal: str = "/Game/Aberration/CoreBlueprints/Inventories/PrimalInventoryComponentBP_CityTerminal.PrimalInventoryComponentBP_CityTerminal_C"
    primal_inventory_component_bp_power_node: str = "/Game/Aberration/CoreBlueprints/Inventories/PrimalInventoryComponentBP_PowerNode.PrimalInventoryComponentBP_PowerNode_C"
    primal_inventory_component_bp_radio_active_charge_lantern_ground: str = "/Game/Aberration/CoreBlueprints/Inventories/PrimalInventoryComponentBP_RadioActiveChargeLanternGround.PrimalInventoryComponentBP_RadioActiveChargeLanternGround_C"
    cryo_fridge: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_CryoFridge.PrimalInventoryBP_CryoFridge_C"
    taxidermy_base: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_TaxidermyBase.PrimalInventoryBP_TaxidermyBase_C"
    tribute_terminal_desert: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Desert.PrimalInventoryBP_TributeTerminal_Desert_C"
    tribute_terminal_fz: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_FZ.PrimalInventoryBP_TributeTerminal_FZ_C"
    tribute_terminal_forest: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Forest.PrimalInventoryBP_TributeTerminal_Forest_C"
    tribute_terminal_snow: str = "/Game/Extinction/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Snow.PrimalInventoryBP_TributeTerminal_Snow_C"
    dino_leash: str = "/Game/Extinction/Structures/DinoLeash/PrimalInventory_DinoLeash.PrimalInventory_DinoLeash_C"
    ammo_container: str = "/Game/Genesis2/Structures/AmmoBox/PrimalInventoryBP_AmmoContainer.PrimalInventoryBP_AmmoContainer_C"
    crop_plot_tek: str = "/Game/Genesis2/Structures/CropPlotTek/PrimalInventoryBP_CropPlot_Tek.PrimalInventoryBP_CropPlot_Tek_C"
    egg_incubator: str = "/Game/Genesis2/Structures/EggIncubator/PrimalInventoryBP_EggIncubator.PrimalInventoryBP_EggIncubator_C"
    tek_bunker: str = "/Game/LostColony/Structures/TekBunker/Inventories/PrimalInventoryBP_TekBunker.PrimalInventoryBP_TekBunker_C"
    warbench: str = "/Game/LostColony/Structures/Warbench/Inventory/PrimalInventoryBP_Warbench.PrimalInventoryBP_Warbench_C"
    tribute_terminal_miniboss_boar: str = "/Game/Mods/Astraeos/Assets/CoreBlueprints/Structures/PrimalInventoryBP_TributeTerminal_Miniboss_Boar.PrimalInventoryBP_TributeTerminal_Miniboss_Boar_C"
    storage_box_barrel: str = "/Game/Packs/Frontier/Structures/BarrelStorage/PrimalInventoryBP_StorageBox_Barrel.PrimalInventoryBP_StorageBox_Barrel_C"
    oil_lamp_chandelier: str = "/Game/Packs/Frontier/Structures/Chandelier/PrimalInventoryBP_OilLamp_Chandelier.PrimalInventoryBP_OilLamp_Chandelier_C"
    oasisaur_foliage_inventory: str = "/Game/Packs/Frontier/Structures/Oasisaur/PrimalInventoryBP_Oasisaur_FoliageInventory.PrimalInventoryBP_Oasisaur_FoliageInventory_C"
    oil_lamp: str = "/Game/Packs/Frontier/Structures/OilLamp/PrimalInventoryBP_OilLamp.PrimalInventoryBP_OilLamp_C"
    treasure_cache_small: str = "/Game/Packs/Frontier/Structures/TreasureCache/PrimalInventoryBP_TreasureCache_Small.PrimalInventoryBP_TreasureCache_Small_C"
    steampunk_clock: str = "/Game/Packs/Steampunk/Structures/Clock/PrimalInventoryBP_SteampunkClock.PrimalInventoryBP_SteampunkClock_C"
    gene_infuser: str = "/Game/Packs/Steampunk/Structures/GeneInfuser/PrimalInventoryBP_GeneInfuser.PrimalInventoryBP_GeneInfuser_C"
    industrial_preserving_bin: str = "/Game/Packs/Steampunk/Structures/IndustrialPreservingBin/PrimalInventoryBP_IndustrialPreservingBin.PrimalInventoryBP_IndustrialPreservingBin_C"
    library_storage: str = "/Game/Packs/Steampunk/Structures/LibraryStorage/PrimalInventoryBP_LibraryStorage.PrimalInventoryBP_LibraryStorage_C"
    linked_storage: str = "/Game/Packs/Steampunk/Structures/LinkedStorage/PrimalInventoryBP_LinkedStorage.PrimalInventoryBP_LinkedStorage_C"
    linked_storage_box: str = "/Game/Packs/Steampunk/Structures/LinkedStorage/PrimalInventoryBP_LinkedStorageBox.PrimalInventoryBP_LinkedStorageBox_C"
    steam_forge: str = "/Game/Packs/Steampunk/Structures/MegaForge/PrimalInventoryBP_SteamForge.PrimalInventoryBP_SteamForge_C"
    tesla_coil: str = "/Game/Packs/Steampunk/Structures/TeslaCoil/PrimalInventoryBP_TeslaCoil.PrimalInventoryBP_TeslaCoil_C"
    tinkering_desk: str = "/Game/Packs/Steampunk/Structures/TinkeringDesk/PrimalInventoryBP_TinkeringDesk.PrimalInventoryBP_TinkeringDesk_C"
    primal_inventory_component_cargo_ledger: str = "/Game/Packs/TidesOfFortune/Structures/CargoLedger/PrimalInventoryComponent_CargoLedger.PrimalInventoryComponent_CargoLedger_C"
    primal_inventory_component_fishtank: str = "/Game/Packs/TidesOfFortune/Structures/Fishtank/Components/PrimalInventoryComponent_Fishtank.PrimalInventoryComponent_Fishtank_C"
    market: str = "/Game/Packs/TidesOfFortune/Structures/Market/PrimalInventoryBP_Market.PrimalInventoryBP_Market_C"
    anti_flyer_turret: str = "/Game/Packs/Wasteland/Structures/AntiFlyerTurret/PrimalInventoryBP_AntiFlyerTurret.PrimalInventoryBP_AntiFlyerTurret_C"
    bio_grinder: str = "/Game/Packs/Wasteland/Structures/BioGrinder/PrimalInventoryBP_BioGrinder.PrimalInventoryBP_BioGrinder_C"
    garage: str = "/Game/Packs/Wasteland/Structures/Garage/PrimalInventoryBP_Garage.PrimalInventoryBP_Garage_C"
    chem_bench_tek: str = "/Game/Packs/Wasteland/Structures/TekChemBench/PrimalInventoryBP_ChemBench_Tek.PrimalInventoryBP_ChemBench_Tek_C"
    tribe_tower: str = "/Game/Packs/Wasteland/Structures/TribeTower/PrimalInventoryBP_TribeTower.PrimalInventoryBP_TribeTower_C"
    ac_base: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_AC_Base.PrimalInventoryBP_AC_Base_C"
    anvil_bench: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_AnvilBench.PrimalInventoryBP_AnvilBench_C"
    artifact_crate: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_ArtifactCrate.PrimalInventoryBP_ArtifactCrate_C"
    ballista: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Ballista.PrimalInventoryBP_Ballista_C"
    base_fuel_burning: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_BaseFuelBurning.PrimalInventoryBP_BaseFuelBurning_C"
    beaver_dam: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_BeaverDam.PrimalInventoryBP_BeaverDam_C"
    beer_barrel: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_BeerBarrel.PrimalInventoryBP_BeerBarrel_C"
    bookshelf: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Bookshelf.PrimalInventoryBP_Bookshelf_C"
    campfire: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Campfire.PrimalInventoryBP_Campfire_C"
    campfire_fireplace: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Campfire_Fireplace.PrimalInventoryBP_Campfire_Fireplace_C"
    cannon: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Cannon.PrimalInventoryBP_Cannon_C"
    catapult: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Catapult.PrimalInventoryBP_Catapult_C"
    chem_bench: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_ChemBench.PrimalInventoryBP_ChemBench_C"
    compost_bin: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CompostBin.PrimalInventoryBP_CompostBin_C"
    cooking_pot: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CookingPot.PrimalInventoryBP_CookingPot_C"
    cooking_pot_industrial: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CookingPot_Industrial.PrimalInventoryBP_CookingPot_Industrial_C"
    crop_plot_large: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CropPlot_Large.PrimalInventoryBP_CropPlot_Large_C"
    crop_plot_medium: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CropPlot_Medium.PrimalInventoryBP_CropPlot_Medium_C"
    crop_plot_small: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_CropPlot_Small.PrimalInventoryBP_CropPlot_Small_C"
    death_item_cache: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_DeathItemCache.PrimalInventoryBP_DeathItemCache_C"
    electric_generator: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_ElectricGenerator.PrimalInventoryBP_ElectricGenerator_C"
    fabricator: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Fabricator.PrimalInventoryBP_Fabricator_C"
    feeding_trough: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_FeedingTrough.PrimalInventoryBP_FeedingTrough_C"
    forge: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Forge.PrimalInventoryBP_Forge_C"
    gift: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Gift.PrimalInventoryBP_Gift_C"
    grill: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Grill.PrimalInventoryBP_Grill_C"
    hat_rack: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_HatRack.PrimalInventoryBP_HatRack_C"
    heavy_turret: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_HeavyTurret.PrimalInventoryBP_HeavyTurret_C"
    ice_box: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_IceBox.PrimalInventoryBP_IceBox_C"
    industrial_forge: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_IndustrialForge.PrimalInventoryBP_IndustrialForge_C"
    industrial_grinder: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_IndustrialGrinder.PrimalInventoryBP_IndustrialGrinder_C"
    light_base: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Light_Base.PrimalInventoryBP_Light_Base_C"
    mortar_and_pestle: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_MortarAndPestle.PrimalInventoryBP_MortarAndPestle_C"
    no_access: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_NoAccess.PrimalInventoryBP_NoAccess_C"
    preserving_bin: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_PreservingBin.PrimalInventoryBP_PreservingBin_C"
    standing_torch: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_StandingTorch.PrimalInventoryBP_StandingTorch_C"
    storage_box_huge: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_StorageBox_Huge.PrimalInventoryBP_StorageBox_Huge_C"
    storage_box_large: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_StorageBox_Large.PrimalInventoryBP_StorageBox_Large_C"
    storage_box_small: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_StorageBox_Small.PrimalInventoryBP_StorageBox_Small_C"
    supply_crate: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_SupplyCrate.PrimalInventoryBP_SupplyCrate_C"
    tap: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Tap.PrimalInventoryBP_Tap_C"
    tek_cave_tribute: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekCaveTribute.PrimalInventoryBP_TekCaveTribute_C"
    tek_cloning_chamber: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekCloningChamber.PrimalInventoryBP_TekCloningChamber_C"
    tek_generator: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekGenerator.PrimalInventoryBP_TekGenerator_C"
    tek_light: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekLight.PrimalInventoryBP_TekLight_C"
    tek_replicator: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekReplicator.PrimalInventoryBP_TekReplicator_C"
    tek_shield: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekShield.PrimalInventoryBP_TekShield_C"
    tek_transmitter: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekTransmitter.PrimalInventoryBP_TekTransmitter_C"
    tek_trough: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TekTrough.PrimalInventoryBP_TekTrough_C"
    toilet: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Toilet.PrimalInventoryBP_Toilet_C"
    tree_sap_tap: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TreeSapTap.PrimalInventoryBP_TreeSapTap_C"
    tribute_terminal1: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal1.PrimalInventoryBP_TributeTerminal1_C"
    tribute_terminal_blue: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Blue.PrimalInventoryBP_TributeTerminal_Blue_C"
    tribute_terminal_green: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Green.PrimalInventoryBP_TributeTerminal_Green_C"
    tribute_terminal_purple: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Purple.PrimalInventoryBP_TributeTerminal_Purple_C"
    tribute_terminal_red: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TributeTerminal_Red.PrimalInventoryBP_TributeTerminal_Red_C"
    trophy_base: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TrophyBase.PrimalInventoryBP_TrophyBase_C"
    trophy_wall: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TrophyWall.PrimalInventoryBP_TrophyWall_C"
    turret: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Turret.PrimalInventoryBP_Turret_C"
    turret_tek: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_TurretTek.PrimalInventoryBP_TurretTek_C"
    vessel: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_Vessel.PrimalInventoryBP_Vessel_C"
    water_tank: str = "/Game/PrimalEarth/CoreBlueprints/Inventories/PrimalInventoryBP_WaterTank.PrimalInventoryBP_WaterTank_C"
    bee_hive: str = "/Game/PrimalEarth/Structures/BeeHive/PrimalInventoryBP_BeeHive.PrimalInventoryBP_BeeHive_C"
    decor_box: str = "/Game/PrimalEarth/Structures/DecorBox/PrimalInventoryBP_DecorBox.PrimalInventoryBP_DecorBox_C"
    display_case: str = "/Game/PrimalEarth/Structures/DisplayCase/PrimalInventory_DisplayCase.PrimalInventory_DisplayCase_C"
    dedicated_storage: str = "/Game/PrimalEarth/StructuresPlus/Misc/DedicatedStorage/PrimalInventory_DedicatedStorage.PrimalInventory_DedicatedStorage_C"
    oil_pump: str = "/Game/ScorchedEarth/Structures/OilPump/PrimalInventoryBP_oilPump.PrimalInventoryBP_oilPump_C"
    water_well: str = "/Game/ScorchedEarth/Structures/WaterWell/PrimalInventoryBP_WaterWell.PrimalInventoryBP_WaterWell_C"

    all_bps = [gas_collector, primal_inventory_component_bp_city_terminal,
               primal_inventory_component_bp_power_node,
               primal_inventory_component_bp_radio_active_charge_lantern_ground, cryo_fridge, taxidermy_base,
               tribute_terminal_desert, tribute_terminal_fz, tribute_terminal_forest, tribute_terminal_snow,
               dino_leash, ammo_container, crop_plot_tek, egg_incubator, tek_bunker, warbench,
               tribute_terminal_miniboss_boar, storage_box_barrel, oil_lamp_chandelier,
               oasisaur_foliage_inventory, oil_lamp, treasure_cache_small, steampunk_clock, gene_infuser,
               industrial_preserving_bin, library_storage, linked_storage, linked_storage_box, steam_forge,
               tesla_coil, tinkering_desk, primal_inventory_component_cargo_ledger,
               primal_inventory_component_fishtank, market, anti_flyer_turret, bio_grinder, garage,
               chem_bench_tek, tribe_tower, ac_base, anvil_bench, artifact_crate, ballista, base_fuel_burning,
               beaver_dam, beer_barrel, bookshelf, campfire, campfire_fireplace, cannon, catapult, chem_bench,
               compost_bin, cooking_pot, cooking_pot_industrial, crop_plot_large, crop_plot_medium,
               crop_plot_small, death_item_cache, electric_generator, fabricator, feeding_trough, forge, gift,
               grill, hat_rack, heavy_turret, ice_box, industrial_forge, industrial_grinder, light_base,
               mortar_and_pestle, no_access, preserving_bin, standing_torch, storage_box_huge,
               storage_box_large, storage_box_small, supply_crate, tap, tek_cave_tribute, tek_cloning_chamber,
               tek_generator, tek_light, tek_replicator, tek_shield, tek_transmitter, tek_trough, toilet,
               tree_sap_tap, tribute_terminal1, tribute_terminal_blue, tribute_terminal_green,
               tribute_terminal_purple, tribute_terminal_red, trophy_base, trophy_wall, turret, turret_tek,
               vessel, water_tank, bee_hive, decor_box, display_case, dedicated_storage, oil_pump, water_well]

class Buffs:
    trick_meter_bonuses_concavenator: str = "/Game/ASA/Dinos/Concavenator/Buff_TrickMeterBonuses_Concavenator.Buff_TrickMeterBonuses_Concavenator_C"
    glider: str = "/Game/Aberration/CoreBlueprints/Buffs/Buff_Glider.Buff_Glider_C"
    primal_buff_persistent_data_impregnate: str = "/Game/Aberration/CoreBlueprints/Buffs/PrimalBuffPersistentData_Impregnate.PrimalBuffPersistentData_Impregnate_C"
    cryo_cooldown: str = "/Game/Extinction/CoreBlueprints/Buffs/Buff_CryoCooldown.Buff_CryoCooldown_C"
    sanguine_elixir_used: str = "/Game/Fjordur/Dinos/Desmodus/Buff_SanguineElixirUsed.Buff_SanguineElixirUsed_C"
    nameless_preggers_lc: str = "/Game/LostColony/CoreBlueprints/Buffs/Buff_NamelessPreggers_LC.Buff_NamelessPreggers_LC_C"
    gargoyle_bp: str = "/Game/LostColony/Dinos/Gargoyle/Buff_Gargoyle_BP.Buff_Gargoyle_BP_C"
    thrall_hostile: str = "/Game/LostColony/Dinos/Thrall/Buffs/Buff_Thrall_Hostile.Buff_Thrall_Hostile_C"
    primal_buff_persistent_data_thrall_hostile: str = "/Game/LostColony/Dinos/Thrall/Buffs/PrimalBuffPersistentData_Thrall_Hostile.PrimalBuffPersistentData_Thrall_Hostile_C"
    dino_companion_young_ice_fox: str = "/Game/LostColony/Dinos/YoungIceFox/Buff_DinoCompanion_YoungIceFox.Buff_DinoCompanion_YoungIceFox_C"
    primal_buff_persistent_data_dino_companion_young_ice_fox: str = "/Game/LostColony/Dinos/YoungIceFox/Buffs/PrimalBuffPersistentData_DinoCompanion_YoungIceFox.PrimalBuffPersistentData_DinoCompanion_YoungIceFox_C"
    time_rewind_cooldown: str = "/Game/Packs/Steampunk/Weapons/Stopwatch/Buff_TimeRewind_Cooldown.Buff_TimeRewind_Cooldown_C"
    primal_buff_persistent_data_dino_companion: str = "/Game/Packs/Wasteland/Dinos/CompanionDino/PrimalBuffPersistentData_DinoCompanion.PrimalBuffPersistentData_DinoCompanion_C"
    dino_companion_doggo: str = "/Game/Packs/Wasteland/Dinos/Doggo/Buff_DinoCompanion_Doggo.Buff_DinoCompanion_Doggo_C"
    cake_slice_cooldown_breeding: str = "/Game/PrimalEarth/CoreBlueprints/Buffs/Buff_CakeSliceCooldown_Breeding.Buff_CakeSliceCooldown_Breeding_C"
    leech: str = "/Game/PrimalEarth/CoreBlueprints/Buffs/Buff_Leech.Buff_Leech_C"
    swamp_fever: str = "/Game/PrimalEarth/CoreBlueprints/Buffs/Buff_SwampFever.Buff_SwampFever_C"
    tek_bed_vitals: str = "/Game/PrimalEarth/CoreBlueprints/Buffs/Buff_TekBedVitals.Buff_TekBedVitals_C"
    buff_data_template_tool_owner: str = "/Game/PrimalEarth/Structures/Templates/Buffs/BuffData_TemplateTool_Owner.BuffData_TemplateTool_Owner_C"
    template_tool_owner: str = "/Game/PrimalEarth/Structures/Templates/Buffs/Buff_TemplateTool_Owner.Buff_TemplateTool_Owner_C"
    base_persistent_heatstroke: str = "/Game/ScorchedEarth/CoreBlueprints/Buffs/Buff_Base_Persistent_Heatstroke.Buff_Base_Persistent_Heatstroke_C"
    primal_buff_persistent_data_generic_time_remaining: str = "/Game/ScorchedEarth/CoreBlueprints/Buffs/PrimalBuffPersistentData_GenericTimeRemaining.PrimalBuffPersistentData_GenericTimeRemaining_C"
    primal_buff_persistent_data_heat_stroke: str = "/Game/ScorchedEarth/CoreBlueprints/Buffs/PrimalBuffPersistentData_HeatStroke.PrimalBuffPersistentData_HeatStroke_C"

    all_bps = [trick_meter_bonuses_concavenator, glider, primal_buff_persistent_data_impregnate,
               cryo_cooldown, sanguine_elixir_used, nameless_preggers_lc, gargoyle_bp, thrall_hostile,
               primal_buff_persistent_data_thrall_hostile, dino_companion_young_ice_fox,
               primal_buff_persistent_data_dino_companion_young_ice_fox, time_rewind_cooldown,
               primal_buff_persistent_data_dino_companion, dino_companion_doggo, cake_slice_cooldown_breeding,
               leech, swamp_fever, tek_bed_vitals, buff_data_template_tool_owner, template_tool_owner,
               base_persistent_heatstroke, primal_buff_persistent_data_generic_time_remaining,
               primal_buff_persistent_data_heat_stroke]

class Misc:
    black_hole_dino: str = "/Game/ASA/Dinos/DarkPegasus/Cryo/PrimalItem_BlackHoleDino.PrimalItem_BlackHoleDino_C"
    rag_item_egg_wyvern_fertilized_ice: str = "/Game/ASA/Dinos/IceWyvern/Extra/Egg/RAG_Item_Egg_Wyvern_Fertilized_Ice.RAG_Item_Egg_Wyvern_Fertilized_Ice_C"
    weapon_shoulder_dragon_autumn: str = "/Game/ASA/Dinos/ShoulderDragon/Variants/Autumn/PrimalItem_WeaponShoulderDragon_Autumn.PrimalItem_WeaponShoulderDragon_Autumn_C"
    weapon_shoulder_dragon_spring: str = "/Game/ASA/Dinos/ShoulderDragon/Variants/Spring/PrimalItem_WeaponShoulderDragon_Spring.PrimalItem_WeaponShoulderDragon_Spring_C"
    weapon_shoulder_dragon_winter: str = "/Game/ASA/Dinos/ShoulderDragon/Variants/Winter/PrimalItem_WeaponShoulderDragon_Winter.PrimalItem_WeaponShoulderDragon_Winter_C"
    charge_battery: str = "/Game/Aberration/WeaponGlowStickCharge/PrimalItem_ChargeBattery.PrimalItem_ChargeBattery_C"
    glow_stick: str = "/Game/Aberration/WeaponGlowStickThrow/PrimalItem_GlowStick.PrimalItem_GlowStick_C"
    plant_species_z_grenade: str = "/Game/Aberration/WeaponPlantSpeciesZ/PrimalItem_PlantSpeciesZ_Grenade.PrimalItem_PlantSpeciesZ_Grenade_C"
    tek_sniper: str = "/Game/Aberration/WeaponTekSniper/PrimalItem_TekSniper.PrimalItem_TekSniper_C"
    accessory_draconic_cape: str = "/Game/Dragontopia/CoreBlueprints/Armor/PrimalItemAccessory_DraconicCape.PrimalItemAccessory_DraconicCape_C"
    weapon_drake_claw: str = "/Game/Dragontopia/Weapons/DrakeClaw/PrimalItem_WeaponDrakeClaw.PrimalItem_WeaponDrakeClaw_C"
    spawner_enforcer: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItem_Spawner_Enforcer.PrimalItem_Spawner_Enforcer_C"
    spawner_mek: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItem_Spawner_Mek.PrimalItem_Spawner_Mek_C"
    taxidermy_dermis: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItem_TaxidermyDermis.PrimalItem_TaxidermyDermis_C"
    taxidermy_dermis_no_upload: str = "/Game/Extinction/CoreBlueprints/Items/PrimalItem_TaxidermyDermis_NoUpload.PrimalItem_TaxidermyDermis_NoUpload_C"
    weapon_taxidermy_tool: str = "/Game/Extinction/CoreBlueprints/Weapons/PrimalItem_WeaponTaxidermyTool.PrimalItem_WeaponTaxidermyTool_C"
    weapon_scout_remote: str = "/Game/Extinction/Dinos/Scout/PrimalItem_WeaponScoutRemote.PrimalItem_WeaponScoutRemote_C"
    spawner_enforcer_city_terminal: str = "/Game/Extinction/Structures/CityTerminal/PrimalItem_Spawner_Enforcer_CityTerminal.PrimalItem_Spawner_Enforcer_CityTerminal_C"
    weapon_scout_remote_city_terminal: str = "/Game/Extinction/Structures/CityTerminal/PrimalItem_WeaponScoutRemote_CityTerminal.PrimalItem_WeaponScoutRemote_CityTerminal_C"
    weapon_admin_blink_rifle: str = "/Game/Extinction/Weapon_AdminBlinkRifle/PrimalItem_WeaponAdminBlinkRifle.PrimalItem_WeaponAdminBlinkRifle_C"
    sanguine_elixir: str = "/Game/Fjordur/Dinos/Desmodus/PrimalItem_SanguineElixir.PrimalItem_SanguineElixir_C"
    spawner_hover_skiff: str = "/Game/Genesis/CoreBlueprints/Items/PrimalItem_Spawner_HoverSkiff.PrimalItem_Spawner_HoverSkiff_C"
    weapon_tek_cruise_missile: str = "/Game/Genesis/Weapons/CruiseMissile/PrimalItem_WeaponTekCruiseMissile.PrimalItem_WeaponTekCruiseMissile_C"
    weapon_fishing_net: str = "/Game/Genesis/Weapons/FishingNet/PrimalItem_WeaponFishingNet.PrimalItem_WeaponFishingNet_C"
    hotbar_skill_base: str = "/Game/LostColony/CoreBlueprints/Skills/PrimalItem_HotbarSkill_Base.PrimalItem_HotbarSkill_Base_C"
    empty_cryopod_angel_fox: str = "/Game/LostColony/Dinos/AngelFox/CoreBlueprints/PrimalItem_EmptyCryopod_AngelFox.PrimalItem_EmptyCryopod_AngelFox_C"
    pristine_vulpite: str = "/Game/LostColony/Dinos/AngelFox/CoreBlueprints/PrimalItem_PristineVulpite.PrimalItem_PristineVulpite_C"
    corrupted_vulpite: str = "/Game/LostColony/Dinos/DevilFox/CoreBlueprints/PrimalItem_CorruptedVulpite.PrimalItem_CorruptedVulpite_C"
    empty_cryopod_gargoyle: str = "/Game/LostColony/Dinos/Gargoyle/PrimalItem_EmptyCryopod_Gargoyle.PrimalItem_EmptyCryopod_Gargoyle_C"
    taxidermy_dermis_gargoyle: str = "/Game/LostColony/Dinos/Gargoyle/PrimalItem_TaxidermyDermis_Gargoyle.PrimalItem_TaxidermyDermis_Gargoyle_C"
    weapon_lost_charge_pet: str = "/Game/LostColony/Dinos/LostChargePet/Weapon/PrimalItem_WeaponLostChargePet.PrimalItem_WeaponLostChargePet_C"
    dino_companion_whistle_young_ice_fox: str = "/Game/LostColony/Dinos/YoungIceFox/PrimalItem_DinoCompanion_Whistle_YoungIceFox.PrimalItem_DinoCompanion_Whistle_YoungIceFox_C"
    lost_colony_bunker_module: str = "/Game/LostColony/Structures/TekBunker/Modules/PrimalItem_LostColony_BunkerModule.PrimalItem_LostColony_BunkerModule_C"
    weapon_base_clipboard_and_hammer: str = "/Game/LostColony/Weapons/ClipboardAndHammer/PrimalItem_WeaponBaseClipboardAndHammer.PrimalItem_WeaponBaseClipboardAndHammer_C"
    holo_decoy: str = "/Game/LostColony/Weapons/HoloDecoy/PrimalItem_HoloDecoy.PrimalItem_HoloDecoy_C"
    coffin_snapshot: str = "/Game/Packs/Frontier/CoreBlueprints/Items/PrimalItem_CoffinSnapshot.PrimalItem_CoffinSnapshot_C"
    death_essence_bp: str = "/Game/Packs/Frontier/CoreBlueprints/Items/PrimalItem_DeathEssence_BP.PrimalItem_DeathEssence_BP_C"
    train_engine: str = "/Game/Packs/Frontier/Dinos/Train/PrimalItem_TrainEngine.PrimalItem_TrainEngine_C"
    spawner_helper_bot: str = "/Game/Packs/Steampunk/Dinos/HelperBot/PrimalItem_Spawner_HelperBot.PrimalItem_Spawner_HelperBot_C"
    dino_spawner_zeppelin: str = "/Game/Packs/Steampunk/Dinos/Zeppelin/PrimalItem_DinoSpawner_Zeppelin.PrimalItem_DinoSpawner_Zeppelin_C"
    bounty_page: str = "/Game/Packs/TidesOfFortune/Structures/BountyBoard/PrimalItem_BountyPage.PrimalItem_BountyPage_C"
    charge_battery_mini: str = "/Game/Packs/Wasteland/CoreBlueprints/Items/PrimalItem_ChargeBattery_Mini.PrimalItem_ChargeBattery_Mini_C"
    dino_companion_whistle_doggo: str = "/Game/Packs/Wasteland/Dinos/Doggo/PrimalItem_DinoCompanion_Whistle_Doggo.PrimalItem_DinoCompanion_Whistle_Doggo_C"
    car_saved: str = "/Game/Packs/Wasteland/Structures/Garage/PrimalItem_CarSaved.PrimalItem_CarSaved_C"
    craft_car: str = "/Game/Packs/Wasteland/Structures/Garage/PrimalItem_CraftCar.PrimalItem_CraftCar_C"
    repair_car: str = "/Game/Packs/Wasteland/Structures/Garage/PrimalItem_RepairCar.PrimalItem_RepairCar_C"
    antifire_grenade: str = "/Game/Packs/Wasteland/Weapons/AntiFireGrenade/PrimalItem_AntifireGrenade.PrimalItem_AntifireGrenade_C"
    weapon_spear_explosive: str = "/Game/Packs/Wasteland/Weapons/ExplosiveSpear/PrimalItem_WeaponSpear_Explosive.PrimalItem_WeaponSpear_Explosive_C"
    dungeon_entrance_tek_cave_easy: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_DungeonEntrance_TekCave_Easy.PrimalItem_DungeonEntrance_TekCave_Easy_C"
    dungeon_entrance_tek_cave_hard: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_DungeonEntrance_TekCave_Hard.PrimalItem_DungeonEntrance_TekCave_Hard_C"
    dungeon_entrance_tek_cave_medium: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_DungeonEntrance_TekCave_Medium.PrimalItem_DungeonEntrance_TekCave_Medium_C"
    power_node_charge: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Cloth/PrimalItem_PowerNodeCharge.PrimalItem_PowerNodeCharge_C"
    chibi_dino_random_craftable: str = "/Game/PrimalEarth/CoreBlueprints/Items/Armor/Skin/ChibiDinos/PrimalItem_ChibiDino_RandomCraftable.PrimalItem_ChibiDino_RandomCraftable_C"
    note: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_Note.PrimalItem_Note_C"
    starting_note: str = "/Game/PrimalEarth/CoreBlueprints/Items/Notes/PrimalItem_StartingNote.PrimalItem_StartingNote_C"
    fish_basket_filled: str = "/Game/PrimalEarth/CoreBlueprints/Items/PrimalItem_FishBasketFilled.PrimalItem_FishBasketFilled_C"
    pliers: str = "/Game/PrimalEarth/CoreBlueprints/Items/PrimalItem_Pliers.PrimalItem_Pliers_C"
    weapon_lasso: str = "/Game/PrimalEarth/CoreBlueprints/Weapons/PrimalItem_WeaponLasso.PrimalItem_WeaponLasso_C"
    motorboat: str = "/Game/PrimalEarth/Items/Raft/PrimalItemMotorboat.PrimalItemMotorboat_C"
    love_tap_club: str = "/Game/PrimalEarth/Structures/Skins/LoveEvolved/LoveExtrasV2/Lovely_RoseClub/PrimalItem_LoveTap_Club.PrimalItem_LoveTap_Club_C"
    template_tablet: str = "/Game/PrimalEarth/Structures/Templates/PrimalItem_TemplateTablet.PrimalItem_TemplateTablet_C"
    dino_costume_custom: str = "/Game/PrimalEarth/Test/PrimalItemDinoCostume_Custom.PrimalItemDinoCostume_Custom_C"
    blood_extractor: str = "/Game/PrimalEarth/Test/PrimalItem_BloodExtractor.PrimalItem_BloodExtractor_C"
    camera: str = "/Game/PrimalEarth/Test/PrimalItem_Camera.PrimalItem_Camera_C"
    weapon_magnifying_glass: str = "/Game/PrimalEarth/Test/PrimalItem_WeaponMagnifyingGlass.PrimalItem_WeaponMagnifyingGlass_C"
    weapon_spyglass: str = "/Game/PrimalEarth/Test/PrimalItem_WeaponSpyglass.PrimalItem_WeaponSpyglass_C"
    weapon_cluster_grenade: str = "/Game/ScorchedEarth/WeaponClusterGrenade/PrimalItem_WeaponClusterGrenade.PrimalItem_WeaponClusterGrenade_C"
    weapon_electronic_binoculars: str = "/Game/ScorchedEarth/WeaponElectronicBinoculars/PrimalItem_WeaponElectronicBinoculars.PrimalItem_WeaponElectronicBinoculars_C"
    weapon_oil_jar: str = "/Game/ScorchedEarth/WeaponOilJar/PrimalItem_WeaponOilJar.PrimalItem_WeaponOilJar_C"
    val_megaraptor_spike: str = "/Game/ASA/Dinos/Megaraptor/Spike/ValMegaraptorSpike.ValMegaraptorSpike_C"
    polar_bear: str = "/Game/Mods/Ragnarok/Custom_Assets/Dinos/Polar_Bear/Polar_Bear.Polar_Bear_C"
    mb_button: str = "/Game/Mods/Ragnarok/Custom_Assets/Trap/Multi_Switch_Door/MB_Button.MB_Button_C"
    helper_bot_ai_data: str = "/Game/Packs/Steampunk/Dinos/HelperBot/AI/BP_HelperBot_AIData.BP_HelperBot_AIData_C"
    helper_bot_docking_bay: str = "/Game/Packs/Steampunk/Dinos/HelperBot/BP_HelperBot_DockingBay.BP_HelperBot_DockingBay_C"
    byte_array_object: str = "/Game/PrimalEarth/CoreBlueprints/ByteArrayObject.ByteArrayObject_C"
    pda_voice_collection: str = "/Game/PrimalEarth/Sound/PlayerVoice/PDA_VoiceCollection.PDA_VoiceCollection_C"

    all_bps = [black_hole_dino, rag_item_egg_wyvern_fertilized_ice, weapon_shoulder_dragon_autumn,
               weapon_shoulder_dragon_spring, weapon_shoulder_dragon_winter, charge_battery, glow_stick,
               plant_species_z_grenade, tek_sniper, accessory_draconic_cape, weapon_drake_claw,
               spawner_enforcer, spawner_mek, taxidermy_dermis, taxidermy_dermis_no_upload,
               weapon_taxidermy_tool, weapon_scout_remote, spawner_enforcer_city_terminal,
               weapon_scout_remote_city_terminal, weapon_admin_blink_rifle, sanguine_elixir,
               spawner_hover_skiff, weapon_tek_cruise_missile, weapon_fishing_net, hotbar_skill_base,
               empty_cryopod_angel_fox, pristine_vulpite, corrupted_vulpite, empty_cryopod_gargoyle,
               taxidermy_dermis_gargoyle, weapon_lost_charge_pet, dino_companion_whistle_young_ice_fox,
               lost_colony_bunker_module, weapon_base_clipboard_and_hammer, holo_decoy, coffin_snapshot,
               death_essence_bp, train_engine, spawner_helper_bot, dino_spawner_zeppelin, bounty_page,
               charge_battery_mini, dino_companion_whistle_doggo, car_saved, craft_car, repair_car,
               antifire_grenade, weapon_spear_explosive, dungeon_entrance_tek_cave_easy,
               dungeon_entrance_tek_cave_hard, dungeon_entrance_tek_cave_medium, power_node_charge,
               chibi_dino_random_craftable, note, starting_note, fish_basket_filled, pliers, weapon_lasso,
               motorboat, love_tap_club, template_tablet, dino_costume_custom, blood_extractor, camera,
               weapon_magnifying_glass, weapon_spyglass, weapon_cluster_grenade, weapon_electronic_binoculars,
               weapon_oil_jar, val_megaraptor_spike, polar_bear, mb_button, helper_bot_ai_data,
               helper_bot_docking_bay, byte_array_object, pda_voice_collection]

class Items:
    item_traits: ItemTraits = ItemTraits()
    boss_tributes: BossTributes = BossTributes()
    vehicle_parts: VehicleParts = VehicleParts()
    recipes: Recipes = Recipes()
    repair_kits: RepairKits = RepairKits()
    treasure_maps: TreasureMaps = TreasureMaps()
    inventories: Inventories = Inventories()
    buffs: Buffs = Buffs()
    misc: Misc = Misc()

    all_bps = item_traits.all_bps + boss_tributes.all_bps + vehicle_parts.all_bps + recipes.all_bps + \
        repair_kits.all_bps + treasure_maps.all_bps + inventories.all_bps + buffs.all_bps + \
        misc.all_bps
