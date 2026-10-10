#!/usr/bin/env python3
"""
Generates blockstates, models, loot tables, tags, lang files and world generation JSON
for Ore Stones Variants Revamped.

Run from the repo root:  python3 tools/generate_resources.py

Textures are NOT overwritten: if src/main/resources/assets/<modid>/textures/block/<name>.png
already exists it is kept. Missing ones get a simple placeholder so the mod always loads.
Edit the ORES table below to rebalance world generation, then re-run the script.
"""
import json
import os
import shutil

MOD_ID = "ore_stones_variants_revamped"
ROOT = os.path.join("src", "main", "resources")
ASSETS = os.path.join(ROOT, "assets", MOD_ID)
DATA = os.path.join(ROOT, "data", MOD_ID)

STONES = {  # id -> (vanilla block, ru name, en name)
    "andesite": ("minecraft:andesite", "Андезитовая", "Andesite"),
    "diorite": ("minecraft:diorite", "Диоритовая", "Diorite"),
    "granite": ("minecraft:granite", "Гранитная", "Granite"),
}

# ---------------------------------------------------------------------------
# BALANCE TABLE
# count   = placement attempts per chunk (a vein only appears if the attempt lands in a stone blob)
# size    = max blocks per vein
# y_min/y_max = height range (stone blobs only exist at Y 0..60, rare ones up to 128)
# dist    = "uniform" or "trapezoid" (trapezoid = most veins in the middle of the range)
# rarity  = 1 in N chunks tries to generate at all (1 = every chunk)
# air     = chance to discard a block that touches air (hides ores in caves)
# biomes  = biome tag
# enabled = False -> ore is not generated at all (also set "enabled" in OreType.java!)
# ---------------------------------------------------------------------------
ORES = {
    "coal":     dict(en="Coal",     ru="угольная руда",    count=20, size=10, y_min=0, y_max=80, dist="uniform",   rarity=1, air=0.0, biomes="#minecraft:is_overworld", enabled=True),
    "copper":   dict(en="Copper",   ru="медная руда",      count=14, size=8,  y_min=0, y_max=64, dist="trapezoid", rarity=1, air=0.0, biomes="#minecraft:is_overworld", enabled=False),
    "iron":     dict(en="Iron",     ru="железная руда",    count=10, size=6,  y_min=0, y_max=60, dist="trapezoid", rarity=1, air=0.0, biomes="#minecraft:is_overworld", enabled=True),
    "redstone": dict(en="Redstone", ru="редстоуновая руда",count=8,  size=5,  y_min=0, y_max=15, dist="uniform",   rarity=1, air=0.0, biomes="#minecraft:is_overworld", enabled=False),
    "lapis":    dict(en="Lapis Lazuli", ru="лазуритовая руда", count=4, size=4, y_min=0, y_max=32, dist="trapezoid", rarity=1, air=0.5, biomes="#minecraft:is_overworld", enabled=False),
    "gold":     dict(en="Gold",     ru="золотая руда",     count=4,  size=4,  y_min=0, y_max=32, dist="trapezoid", rarity=1, air=0.0, biomes="#minecraft:is_overworld", enabled=True),
    "diamond":  dict(en="Diamond",  ru="алмазная руда",    count=4,  size=3,  y_min=0, y_max=16, dist="trapezoid", rarity=2, air=0.5, biomes="#minecraft:is_overworld", enabled=True),
    "emerald":  dict(en="Emerald",  ru="изумрудная руда",  count=6,  size=2,  y_min=0, y_max=64, dist="uniform",   rarity=2, air=0.0, biomes="#minecraft:is_mountain", enabled=False),
}

NEEDS_STONE = {"coal", "copper", "iron", "lapis"}
NEEDS_IRON = {"gold", "redstone", "diamond", "emerald"}
# Fortune-capable drops: (item, min, max, bonus)
DROPS = {
    "coal": ("minecraft:coal", None, "ore_drops"),
    "copper": ("minecraft:raw_copper", (2, 5), "ore_drops"),
    "iron": ("minecraft:raw_iron", None, "ore_drops"),
    "gold": ("minecraft:raw_gold", None, "ore_drops"),
    "redstone": ("minecraft:redstone", (4, 5), "uniform_bonus_count"),
    "lapis": ("minecraft:lapis_lazuli", (4, 9), "ore_drops"),
    "diamond": ("minecraft:diamond", None, "ore_drops"),
    "emerald": ("minecraft:emerald", None, "ore_drops"),
}
PLACEHOLDER_ORE_COLORS = {
    "coal": (30, 30, 30), "copper": (200, 110, 70), "iron": (216, 175, 147),
    "gold": (250, 220, 60), "redstone": (220, 20, 20), "lapis": (30, 70, 190),
    "diamond": (90, 235, 225), "emerald": (30, 200, 80),
}
PLACEHOLDER_STONE_COLORS = {
    "andesite": (136, 136, 136), "diorite": (200, 200, 200), "granite": (155, 105, 90),
}


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def block_name(stone, ore):
    return f"{stone}_{ore}_ore"


def make_placeholder(path, stone, ore):
    """Tiny 16x16 placeholder: stone colour with a few ore-coloured pixels. Never overwrites."""
    if os.path.exists(path):
        return
    from PIL import Image
    import random
    rng = random.Random(f"{stone}{ore}")
    base = PLACEHOLDER_STONE_COLORS[stone]
    img = Image.new("RGB", (16, 16))
    for x in range(16):
        for y in range(16):
            d = rng.randint(-14, 14)
            img.putpixel((x, y), tuple(max(0, min(255, c + d)) for c in base))
    oc = PLACEHOLDER_ORE_COLORS[ore]
    for cx, cy in [(3, 3), (10, 4), (5, 10), (12, 12), (8, 7)]:
        for dx in (0, 1):
            for dy in (0, 1):
                img.putpixel((cx + dx, cy + dy), oc)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def loot_table(stone, ore):
    name = block_name(stone, ore)
    item, count_range, bonus = DROPS[ore]
    functions = []
    if count_range:
        functions.append({"function": "minecraft:set_count",
                          "count": {"type": "minecraft:uniform", "min": float(count_range[0]), "max": float(count_range[1])},
                          "add": False})
    if bonus == "ore_drops":
        functions.append({"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune",
                          "formula": "minecraft:ore_drops"})
    else:
        functions.append({"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune",
                          "formula": "minecraft:uniform_bonus_count", "parameters": {"bonusMultiplier": 1}})
    functions.append({"function": "minecraft:explosion_decay"})
    return {
        "type": "minecraft:block",
        "pools": [{
            "rolls": 1.0, "bonus_rolls": 0.0,
            "entries": [{
                "type": "minecraft:alternatives",
                "children": [
                    {"type": "minecraft:item",
                     "conditions": [{"condition": "minecraft:match_tool", "predicate": {
                         "enchantments": [{"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]}}],
                     "name": f"{MOD_ID}:{name}"},
                    {"type": "minecraft:item", "functions": functions, "name": item},
                ],
            }],
        }],
    }


def height(cfg):
    lo = {"absolute": cfg["y_min"]}
    hi = {"absolute": cfg["y_max"]}
    t = "minecraft:uniform" if cfg["dist"] == "uniform" else "minecraft:trapezoid"
    return {"type": "minecraft:height_range",
            "height": {"type": t, "min_inclusive": lo, "max_inclusive": hi}}


def clean_generated():
    """Remove everything this script generates (textures of enabled ores are never touched)."""
    for path in [DATA,
                 os.path.join(ROOT, "data", "forge"),
                 os.path.join(ROOT, "data", "minecraft"),
                 os.path.join(ASSETS, "blockstates"),
                 os.path.join(ASSETS, "models"),
                 os.path.join(ASSETS, "lang")]:
        shutil.rmtree(path, ignore_errors=True)
    # textures of disabled ores are removed too
    tex_dir = os.path.join(ASSETS, "textures", "block")
    for stone in STONES:
        for ore, cfg in ORES.items():
            if not cfg["enabled"]:
                f = os.path.join(tex_dir, f"{block_name(stone, ore)}.png")
                if os.path.exists(f):
                    os.remove(f)


def main():
    clean_generated()
    all_blocks = []
    lang_en = {f"itemGroup.{MOD_ID}": "Ore Stones Variants Revamped"}
    lang_ru = {f"itemGroup.{MOD_ID}": "Ore Stones Variants Revamped"}

    active = {o: c for o, c in ORES.items() if c["enabled"]}

    for stone, (_, ru_stone, en_stone) in STONES.items():
        for ore, cfg in active.items():
            name = block_name(stone, ore)
            all_blocks.append((stone, ore, name))
            model = f"{MOD_ID}:block/{name}"
            # blockstate (redstone ore has a "lit" property, both states use the same model)
            if ore == "redstone":
                write_json(os.path.join(ASSETS, "blockstates", f"{name}.json"),
                           {"variants": {"lit=false": {"model": model}, "lit=true": {"model": model}}})
            else:
                write_json(os.path.join(ASSETS, "blockstates", f"{name}.json"),
                           {"variants": {"": {"model": model}}})
            write_json(os.path.join(ASSETS, "models", "block", f"{name}.json"),
                       {"parent": "minecraft:block/cube_all", "textures": {"all": model}})
            write_json(os.path.join(ASSETS, "models", "item", f"{name}.json"), {"parent": model})
            make_placeholder(os.path.join(ASSETS, "textures", "block", f"{name}.png"), stone, ore)
            write_json(os.path.join(DATA, "loot_tables", "blocks", f"{name}.json"), loot_table(stone, ore))
            lang_en[f"block.{MOD_ID}.{name}"] = f"{en_stone} {cfg['en']} Ore"
            lang_ru[f"block.{MOD_ID}.{name}"] = f"{ru_stone} {cfg['ru']}"

    write_json(os.path.join(ASSETS, "lang", "en_us.json"), lang_en)
    write_json(os.path.join(ASSETS, "lang", "ru_ru.json"), lang_ru)

    # --- tags ---
    def tag(path, values):
        write_json(path, {"replace": False, "values": values})

    mc_blocks = os.path.join(ROOT, "data", "minecraft", "tags", "blocks")
    tag(os.path.join(mc_blocks, "mineable", "pickaxe.json"), [f"{MOD_ID}:{n}" for _, _, n in all_blocks])
    tag(os.path.join(mc_blocks, "needs_stone_tool.json"), [f"{MOD_ID}:{n}" for _, o, n in all_blocks if o in NEEDS_STONE])
    tag(os.path.join(mc_blocks, "needs_iron_tool.json"), [f"{MOD_ID}:{n}" for _, o, n in all_blocks if o in NEEDS_IRON])
    forge_blocks = os.path.join(ROOT, "data", "forge", "tags", "blocks")
    forge_items = os.path.join(ROOT, "data", "forge", "tags", "items")
    tag(os.path.join(forge_blocks, "ores.json"), [f"#forge:ores/{o}" for o in active])
    tag(os.path.join(forge_items, "ores.json"), [f"#forge:ores/{o}" for o in active])
    for ore in active:
        vals = [f"{MOD_ID}:{n}" for _, o, n in all_blocks if o == ore]
        tag(os.path.join(forge_blocks, "ores", f"{ore}.json"), vals)
        tag(os.path.join(forge_items, "ores", f"{ore}.json"), vals)
    for stone in STONES:
        vals = [f"{MOD_ID}:{n}" for s, _, n in all_blocks if s == stone]
        tag(os.path.join(forge_blocks, "ores_in_ground", f"{stone}.json"), vals)
        tag(os.path.join(forge_items, "ores_in_ground", f"{stone}.json"), vals)

    # --- world generation ---
    # one configured feature per ore, vein can cross the three stones (each block picks its own variant)
    biome_modifiers = {}
    for ore, cfg in active.items():
        targets = [{
            "target": {"predicate_type": "minecraft:block_match", "block": vanilla},
            "state": {"Name": f"{MOD_ID}:{block_name(stone, ore)}"},
        } for stone, (vanilla, _, _) in STONES.items()]
        feat = f"ore_{ore}_variants"
        write_json(os.path.join(DATA, "worldgen", "configured_feature", f"{feat}.json"), {
            "type": "minecraft:ore",
            "config": {"discard_chance_on_air_exposure": cfg["air"], "size": cfg["size"], "targets": targets},
        })
        placement = [{"type": "minecraft:count", "count": cfg["count"]}]
        if cfg["rarity"] > 1:
            placement.insert(0, {"type": "minecraft:rarity_filter", "chance": cfg["rarity"]})
        placement += [{"type": "minecraft:in_square"}, height(cfg), {"type": "minecraft:biome"}]
        write_json(os.path.join(DATA, "worldgen", "placed_feature", f"{feat}.json"), {
            "feature": f"{MOD_ID}:{feat}", "placement": placement,
        })
        biome_modifiers.setdefault(cfg["biomes"], []).append(f"{MOD_ID}:{feat}")

    for i, (biomes, feats) in enumerate(biome_modifiers.items()):
        write_json(os.path.join(DATA, "forge", "biome_modifier", f"add_ore_variants_{i}.json"), {
            "type": "forge:add_features", "biomes": biomes, "features": feats, "step": "underground_ores",
        })

    print(f"Generated {len(all_blocks)} blocks.")


if __name__ == "__main__":
    main()
