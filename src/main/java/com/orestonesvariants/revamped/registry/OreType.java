package com.orestonesvariants.revamped.registry;

import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

import java.util.function.Supplier;

public enum OreType {
    COAL("coal", () -> Blocks.COAL_ORE, UniformInt.of(0, 2)),
    COPPER("copper", () -> Blocks.COPPER_ORE, UniformInt.of(0, 0)),
    IRON("iron", () -> Blocks.IRON_ORE, UniformInt.of(0, 0)),
    GOLD("gold", () -> Blocks.GOLD_ORE, UniformInt.of(0, 0)),
    REDSTONE("redstone", () -> Blocks.REDSTONE_ORE, null), // redstone ore has its own block class
    LAPIS("lapis", () -> Blocks.LAPIS_ORE, UniformInt.of(2, 5)),
    DIAMOND("diamond", () -> Blocks.DIAMOND_ORE, UniformInt.of(3, 7)),
    EMERALD("emerald", () -> Blocks.EMERALD_ORE, UniformInt.of(3, 7));

    public final String id;
    /** Vanilla ore whose block properties (hardness, tool requirement, sound) are copied. */
    public final Supplier<Block> vanilla;
    public final IntProvider xp;

    OreType(String id, Supplier<Block> vanilla, IntProvider xp) {
        this.id = id;
        this.vanilla = vanilla;
        this.xp = xp;
    }
}
