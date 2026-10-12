#!/usr/bin/env python3
"""
Generates blockstates, models, loot tables, tags, lang files, BALANCE.md and world generation
JSON for Ore Stones Variants Revamped.

Run from the repo root:  python3 tools/generate_resources.py

Textures are NOT overwritten: if the png already exists it is kept. Missing ones get a simple
placeholder so the mod always loads. Edit the tables below to rebalance, then re-run the script.
"""
import json
import os
import shutil

MOD_ID = "ore_stones_variants_revamped"
ROOT = os.path.join("src", "main", "resources")
ASSETS = os.path.join(ROOT, "assets", MOD_ID)
DATA = os.path.join(ROOT, "data", MOD_ID)

# host id -> (vanilla block, ru adjective, en name)
HOSTS = {
    "andesite": ("minecraft:andesite", "Андезитовая", "Andesite"),
    "diorite": ("minecraft:diorite", "Диоритовая", "Diorite"),
    "granite": ("minecraft:granite", "Гранитная", "Granite"),
    "tuff": ("minecraft:tuff", "Туфовая", "Tuff"),
    "sandstone": ("minecraft:sandstone", "Песчаниковая", "Sandstone"),
}

# Share of underground volume that a host occupies at the heights where its blobs exist.
# andesite+diorite+granite blobs: 3 x (2 blobs x 64 blocks) per chunk in Y 0..60  -> ~2.5%
# tuff blobs: 2 blobs x 64 blocks per chunk in Y -64..0                           -> ~0.75%
# sandstone: a ~5 block thick layer under desert/beach sand, estimated hit rate ~19% for Y 55..80
DENSITY = {"stone": 0.025, "tuff": 0.0075, "sandstone": 0.19}
SURFACE_BAND = {"stone": (0, 60), "tuff": (-64, 0), "sandstone": (55, 80)}

# ---------------------------------------------------------------------------
# BALANCE TABLES
# count   = placement attempts per chunk (a vein only appears if the attempt lands in the host)
# size    = max blocks per vein
# y_min/y_max, dist = height range and distribution ("uniform" or "trapezoid")
# rarity  = 1 in N chunks tries to generate at all (1 = every chunk)
# air     = chance to discard a block that touches air
# biomes  = biome tag
# ---------------------------------------------------------------------------
def ore(en, ru, count, size, y_min, y_max, dist="uniform", rarity=1, air=0.0, biomes="#minecraft:is_overworld"):
    return dict(en=en, ru=ru, count=count, size=size, y_min=y_min, y_max=y_max, dist=dist,
                rarity=rarity, air=air, biomes=biomes)

GROUPS = {
    # veins in andesite / diorite / granite (one vein can cross all three)
    "stone": dict(hosts=["andesite", "diorite", "granite"], feature="ore_{ore}_variants", ores={
        "coal":     ore("Coal", "угольная руда", 19, 10, 0, 80),
        "copper":   ore("Copper", "медная руда", 15, 8, 0, 64, "trapezoid"),
        "iron":     ore("Iron", "железная руда", 11, 6, 0, 60, "trapezoid"),
        "redstone": ore("Redstone", "редстоуновая руда", 6, 5, 0, 15),
        "lapis":    ore("Lapis Lazuli", "лазуритовая руда", 3, 4, 0, 32, "trapezoid", air=0.5),
        "gold":     ore("Gold", "золотая руда", 3, 4, 0, 32, "trapezoid"),
        "diamond":  ore("Diamond", "алмазная руда", 3, 3, 0, 16, "trapezoid", rarity=2, air=0.5),
        "emerald":  ore("Emerald", "изумрудная руда", 5, 2, 0, 64, rarity=2, biomes="#minecraft:is_mountain"),
    }),
    # veins in tuff (deepslate layer, below Y 0)
    "tuff": dict(hosts=["tuff"], feature="ore_{ore}_tuff_variants", ores={
        "coal":     ore("Coal", "угольная руда", 14, 10, -64, -1),
        "copper":   ore("Copper", "медная руда", 14, 8, -64, -1),
        "iron":     ore("Iron", "железная руда", 11, 6, -64, -1),
        "redstone": ore("Redstone", "редстоуновая руда", 17, 5, -64, -1),
        "lapis":    ore("Lapis Lazuli", "лазуритовая руда", 6, 4, -64, -1, "trapezoid", air=0.5),
        "gold":     ore("Gold", "золотая руда", 7, 4, -64, -1, "trapezoid"),
        "diamond":  ore("Diamond", "алмазная руда", 6, 3, -64, -16, rarity=2, air=0.5),
        "emerald":  ore("Emerald", "изумрудная руда", 7, 2, -64, -1, rarity=2, biomes="#minecraft:is_mountain"),
    }),
    # rare lapis in sandstone (under desert / beach sand)
    "sandstone": dict(hosts=["sandstone"], feature="ore_{ore}_sandstone_variants", ores={
        "lapis":    ore("Lapis Lazuli", "лазуритовая руда", 2, 4, 55, 80, rarity=5),
    }),
}

NEEDS_STONE = {"coal", "copper", "iron", "lapis"}
NEEDS_IRON = {"gold", "redstone", "diamond", "emerald"}
# (item, count range, bonus formula)
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
PLACEHOLDER_HOST_COLORS = {
    "andesite": (136, 136, 136), "diorite": (200, 200, 200), "granite": (155, 105, 90),
    "tuff": (106, 110, 111), "sandstone": (218, 210, 163),
}
# sandstone has distinct top/bottom textures
EXTRA_FACES = {"sandstone": ["top", "bottom"]}


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def block_name(host, ore_id):
    return f"{host}_{ore_id}_ore"


def make_placeholder(path, host, ore_id):
    """Tiny 16x16 placeholder: host colour with a few ore-coloured pixels. Never overwrites."""
    if os.path.exists(path):
        return
    from PIL import Image
    import random
    rng = random.Random(f"{host}{ore_id}")
    base = PLACEHOLDER_HOST_COLORS[host]
    img = Image.new("RGB", (16, 16))
    for x in range(16):
        for y in range(16):
            d = rng.randint(-14, 14)
            img.putpixel((x, y), tuple(max(0, min(255, c + d)) for c in base))
    oc = PLACEHOLDER_ORE_COLORS[ore_id]
    for cx, cy in [(3, 3), (10, 4), (5, 10), (12, 12), (8, 7)]:
        for dx in (0, 1):
            for dy in (0, 1):
                img.putpixel((cx + dx, cy + dy), oc)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def loot_table(host, ore_id):
    name = block_name(host, ore_id)
    item, count_range, bonus = DROPS[ore_id]
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


def veins_per_chunk(group, cfg):
    """Rough estimate of veins that actually start inside the host per chunk."""
    lo, hi = SURFACE_BAND[group]
    overlap = max(0, min(cfg["y_max"], hi) - max(cfg["y_min"], lo)) / max(1, cfg["y_max"] - cfg["y_min"])
    if group == "sandstone":
        overlap = 1.0
    return cfg["count"] * DENSITY[group] * overlap / cfg["rarity"]


def clean_generated():
    """Remove everything this script generates (existing textures are never touched)."""
    for path in [DATA,
                 os.path.join(ROOT, "data", "forge"),
                 os.path.join(ROOT, "data", "minecraft"),
                 os.path.join(ASSETS, "blockstates"),
                 os.path.join(ASSETS, "models"),
                 os.path.join(ASSETS, "lang")]:
        shutil.rmtree(path, ignore_errors=True)


def main():
    clean_generated()
    blocks = []  # (host, ore, name)
    lang_en = {f"itemGroup.{MOD_ID}": "Ore Stones Variants Revamped"}
    lang_ru = {f"itemGroup.{MOD_ID}": "Ore Stones Variants Revamped"}

    for gname, group in GROUPS.items():
        for host in group["hosts"]:
            _, ru_host, en_host = HOSTS[host]
            for ore_id, cfg in group["ores"].items():
                name = block_name(host, ore_id)
                blocks.append((host, ore_id, name))
                model = f"{MOD_ID}:block/{name}"
                if ore_id == "redstone":
                    write_json(os.path.join(ASSETS, "blockstates", f"{name}.json"),
                               {"variants": {"lit=false": {"model": model}, "lit=true": {"model": model}}})
                else:
                    write_json(os.path.join(ASSETS, "blockstates", f"{name}.json"),
                               {"variants": {"": {"model": model}}})
                tex_dir = os.path.join(ASSETS, "textures", "block")
                make_placeholder(os.path.join(tex_dir, f"{name}.png"), host, ore_id)
                if host in EXTRA_FACES:
                    for face in EXTRA_FACES[host]:
                        make_placeholder(os.path.join(tex_dir, f"{name}_{face}.png"), host, ore_id)
                    write_json(os.path.join(ASSETS, "models", "block", f"{name}.json"), {
                        "parent": "minecraft:block/cube_bottom_top",
                        "textures": {"top": f"{model}_top", "bottom": f"{model}_bottom", "side": model}})
                else:
                    write_json(os.path.join(ASSETS, "models", "block", f"{name}.json"),
                               {"parent": "minecraft:block/cube_all", "textures": {"all": model}})
                write_json(os.path.join(ASSETS, "models", "item", f"{name}.json"), {"parent": model})
                write_json(os.path.join(DATA, "loot_tables", "blocks", f"{name}.json"), loot_table(host, ore_id))
                lang_en[f"block.{MOD_ID}.{name}"] = f"{en_host} {cfg['en']} Ore"
                lang_ru[f"block.{MOD_ID}.{name}"] = f"{ru_host} {cfg['ru']}"

    write_json(os.path.join(ASSETS, "lang", "en_us.json"), lang_en)
    write_json(os.path.join(ASSETS, "lang", "ru_ru.json"), lang_ru)

    # --- tags ---
    def tag(path, values):
        write_json(path, {"replace": False, "values": values})

    ore_ids = sorted({o for _, o, _ in blocks}, key=lambda x: list(DROPS).index(x))
    mc_blocks = os.path.join(ROOT, "data", "minecraft", "tags", "blocks")
    tag(os.path.join(mc_blocks, "mineable", "pickaxe.json"), [f"{MOD_ID}:{n}" for _, _, n in blocks])
    tag(os.path.join(mc_blocks, "needs_stone_tool.json"), [f"{MOD_ID}:{n}" for _, o, n in blocks if o in NEEDS_STONE])
    tag(os.path.join(mc_blocks, "needs_iron_tool.json"), [f"{MOD_ID}:{n}" for _, o, n in blocks if o in NEEDS_IRON])
    forge_blocks = os.path.join(ROOT, "data", "forge", "tags", "blocks")
    forge_items = os.path.join(ROOT, "data", "forge", "tags", "items")
    tag(os.path.join(forge_blocks, "ores.json"), [f"#forge:ores/{o}" for o in ore_ids])
    tag(os.path.join(forge_items, "ores.json"), [f"#forge:ores/{o}" for o in ore_ids])
    for o in ore_ids:
        vals = [f"{MOD_ID}:{n}" for _, oo, n in blocks if oo == o]
        tag(os.path.join(forge_blocks, "ores", f"{o}.json"), vals)
        tag(os.path.join(forge_items, "ores", f"{o}.json"), vals)
    for host in HOSTS:
        vals = [f"{MOD_ID}:{n}" for h, _, n in blocks if h == host]
        tag(os.path.join(forge_blocks, "ores_in_ground", f"{host}.json"), vals)
        tag(os.path.join(forge_items, "ores_in_ground", f"{host}.json"), vals)

    # --- world generation ---
    biome_modifiers = {}
    balance_rows = []
    for gname, group in GROUPS.items():
        for ore_id, cfg in group["ores"].items():
            targets = [{
                "target": {"predicate_type": "minecraft:block_match", "block": HOSTS[h][0]},
                "state": {"Name": f"{MOD_ID}:{block_name(h, ore_id)}"},
            } for h in group["hosts"]]
            feat = group["feature"].format(ore=ore_id)
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
            balance_rows.append((gname, ore_id, cfg))

    for i, (biomes, feats) in enumerate(biome_modifiers.items()):
        write_json(os.path.join(DATA, "forge", "biome_modifier", f"add_ore_variants_{i}.json"), {
            "type": "forge:add_features", "biomes": biomes, "features": feats, "step": "underground_ores",
        })

    # --- BALANCE.md (estimates) ---
    titles = {"stone": "Андезит, диорит, гранит (Y 0…60)", "tuff": "Туф (Y -64…-1)", "sandstone": "Песчаник (пустыни и пляжи)"}
    lines = ["# Баланс генерации (оценка)", "",
             "Файл создаётся скриптом `tools/generate_resources.py`. «Жил на чанк» это оценка: жила появляется,",
             "только если попытка попала в нужный камень. В реальном мире цифры будут немного отличаться.", ""]
    totals = {}
    for gname in GROUPS:
        lines += [f"## {titles[gname]}", "",
                  "| Руда | Попыток/чанк | Размер | Y | Редкость | Жил на чанк | 1 жила на N чанков |",
                  "|---|---|---|---|---|---|---|"]
        for g, o, cfg in balance_rows:
            if g != gname:
                continue
            v = veins_per_chunk(g, cfg)
            totals[o] = totals.get(o, 0) + v
            rar = "каждый чанк" if cfg["rarity"] == 1 else f"1 из {cfg['rarity']} чанков"
            if cfg["air"]:
                rar += f", {int(cfg['air'] * 100)}% скрыть у воздуха"
            if cfg["biomes"].endswith("is_mountain"):
                rar += ", горные биомы"
            lines.append(f"| {cfg['ru'].capitalize()} | {cfg['count']} | {cfg['size']} | {cfg['y_min']}…{cfg['y_max']} | {rar} | {v:.3f} | ~{1 / v:.0f} |")
        lines.append("")
    lines += ["## Итого (без песчаника)", "", "| Руда | Жил на чанк, все камни |", "|---|---|"]
    for o in DROPS:
        t = sum(veins_per_chunk(g, c) for g, oo, c in balance_rows if oo == o and g != "sandstone")
        lines.append(f"| {o} | {t:.3f} |")
    with open("BALANCE.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Generated {len(blocks)} blocks.")


if __name__ == "__main__":
    main()
