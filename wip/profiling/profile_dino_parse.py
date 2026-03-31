"""Profile where time is spent in DinoApi.get_all with 1 vs 4 workers."""
import time
import sys
import gc

def main():
    print(f"Python: {sys.version}")
    if hasattr(sys, '_is_gil_enabled'):
        print(f"GIL disabled: {not sys._is_gil_enabled()}")
    
    from arkparse import AsaSave
    from arkparse.api import DinoApi
    from pathlib import Path
    
    save_path = Path(r"C:\Users\Vincent\Downloads\Astraeos_WP\Astraeos_WP.ark")
    print(f"\nLoading save: {save_path}")
    
    t0 = time.perf_counter()
    save = AsaSave(save_path)
    print(f"Save loaded in {time.perf_counter() - t0:.2f}s")
    
    # === Phase 1: Time breakdown of get_all ===
    print("\n" + "=" * 60)
    print("Phase 1: Time breakdown of get_all (1 worker)")
    print("=" * 60)
    
    dapi = DinoApi(save)
    
    # Step A: get_all_objects (fetches from save_connection cache)
    t0 = time.perf_counter()
    objects = dapi.get_all_objects()
    t_objects = time.perf_counter() - t0
    print(f"  get_all_objects: {t_objects:.3f}s  ({len(objects)} objects)")
    
    # Count categories
    dino_count = 0
    cryopod_count = 0
    status_count = 0
    for obj in objects.values():
        if "Dinos/" in obj.blueprint and "_Character_" in obj.blueprint:
            dino_count += 1
        elif "PrimalItem_SCSCryopod" in obj.blueprint or "PrimalItem_WeaponEmptyCryopod" in obj.blueprint:
            cryopod_count += 1
        elif "DinoCharacterStatusComponent" in obj.blueprint:
            status_count += 1
    print(f"  Categories: {dino_count} dinos, {cryopod_count} cryopods, {status_count} status components")
    
    # Step B: Full get_all with 1 worker
    dapi2 = DinoApi(save)
    t0 = time.perf_counter()
    dinos_1 = dapi2.get_all(max_workers=1)
    t_1worker = time.perf_counter() - t0
    print(f"\n  get_all (1 worker):  {t_1worker:.3f}s  ({len(dinos_1)} dinos)")
    
    # Step C: Full get_all with 4 workers (fresh api)
    dapi3 = DinoApi(save)
    gc.collect()
    t0 = time.perf_counter()
    dinos_4 = dapi3.get_all(max_workers=4)
    t_4worker = time.perf_counter() - t0
    print(f"  get_all (4 workers): {t_4worker:.3f}s  ({len(dinos_4)} dinos)")
    
    if t_4worker > 0:
        print(f"\n  Speedup: {t_1worker / t_4worker:.2f}x")
    
    # === Phase 2: Isolate dino parsing vs cryopod parsing ===
    print("\n" + "=" * 60)
    print("Phase 2: Dino parsing only (no cryopods)")
    print("=" * 60)
    
    dapi4 = DinoApi(save)
    t0 = time.perf_counter()
    dinos_no_cryo_1 = dapi4.get_all(max_workers=1, include_cryos=False)
    t_nocryo_1 = time.perf_counter() - t0
    print(f"  1 worker (no cryos):  {t_nocryo_1:.3f}s  ({len(dinos_no_cryo_1)} dinos)")
    
    dapi5 = DinoApi(save)
    gc.collect()
    t0 = time.perf_counter()
    dinos_no_cryo_4 = dapi5.get_all(max_workers=4, include_cryos=False)
    t_nocryo_4 = time.perf_counter() - t0
    print(f"  4 workers (no cryos): {t_nocryo_4:.3f}s  ({len(dinos_no_cryo_4)} dinos)")
    
    if t_nocryo_4 > 0:
        print(f"\n  Speedup (no cryos): {t_nocryo_1 / t_nocryo_4:.2f}x")
    
    # === Phase 3: Cryopods only ===
    print("\n" + "=" * 60)
    print("Phase 3: Cryopod parsing only")
    print("=" * 60)
    
    dapi6 = DinoApi(save)
    t0 = time.perf_counter()
    dinos_cryo_only = dapi6.get_all(max_workers=1, include_wild=False, include_tamed=False, only_cryopodded=True)
    t_cryo = time.perf_counter() - t0
    # Count cryopods parsed
    cryo_parsed = len(dapi6.parsed_cryopods)
    print(f"  Cryopods: {t_cryo:.3f}s  ({cryo_parsed} cryopods -> {len(dinos_cryo_only)} dinos)")
    
    cryopod_time = t_1worker - t_nocryo_1
    dino_time = t_nocryo_1
    print(f"\n  Estimated time split:")
    print(f"    get_all_objects:  {t_objects:.3f}s")
    print(f"    Dino parsing:    {dino_time:.3f}s")
    print(f"    Cryopod parsing: {cryopod_time:.3f}s")
    print(f"    Total:           {t_1worker:.3f}s")

if __name__ == "__main__":
    main()
