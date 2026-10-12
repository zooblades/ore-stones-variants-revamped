package com.orestonesvariants.revamped.registry;

import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

import java.util.function.Supplier;

public enum OreType {
    COAL("coal", () -> Blocks.COAL_ORE, () -> Blocks.DEEPSLATE_COAL_ORE, UniformInt.of(0, 2)),
    COPPER("copper", () -> Blocks.COPPER_ORE, () -> Blocks.DEEPSLATE_COPPER_ORE, UniformInt.of(0, 0)),
    IRON("iron", () -> Blocks.IRON_ORE, () -> Blocks.DEEPSLATE_IRON_ORE, UniformInt.of(0, 0)),
    GOLD("gold", () -> Blocks.GOLD_ORE, () -> Blocks.DEEPSLATE_GOLD_ORE, UniformInt.of(0, 0)),
    REDSTONE("redstone", () -> Blocks.REDSTONE_ORE, () -> Blocks.DEEPSLATE_REDSTONE_ORE, null), // own block class
    LAPIS("lapis", () -> Blocks.LAPIS_ORE, () -> Blocks.DEEPSLATE_LAPIS_ORE, UniformInt.of(2, 5)),
    DIAMOND("diamond", () -> Blocks.DIAMOND_ORE, () -> Blocks.DEEPSLATE_DIAMOND_ORE, UniformInt.of(3, 7)),
    EMERALD("emerald", () -> Blocks.EMERALD_ORE, () -> Blocks.DEEPSLATE_EMERALD_ORE, UniformInt.of(3, 7));

    public final String id;
    /** Vanilla stone ore whose block properties (hardness, tool requirement, sound) are copied. */
    public final Supplier<Block> vanilla;
    /** Vanilla deepslate ore, copied for the tuff variants (harder, like deepslate ores). */
    public final Supplier<Block> deepslate;
    public final IntProvider xp;

    OreType(String id, Supplier<Block> vanilla, Supplier<Block> deepslate, IntProvider xp) {
        this.id = id;
        this.vanilla = vanilla;
        this.deepslate = deepslate;
        this.xp = xp;
    }
}
