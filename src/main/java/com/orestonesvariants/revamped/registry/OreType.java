package com.orestonesvariants.revamped.registry;

import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;

import java.util.function.Supplier;

public enum OreType {
    COAL("coal", () -> Blocks.COAL_ORE, UniformInt.of(0, 2), true),
    COPPER("copper", () -> Blocks.COPPER_ORE, UniformInt.of(0, 0), true),
    IRON("iron", () -> Blocks.IRON_ORE, UniformInt.of(0, 0), true),
    GOLD("gold", () -> Blocks.GOLD_ORE, UniformInt.of(0, 0), true),
    REDSTONE("redstone", () -> Blocks.REDSTONE_ORE, null, true), // has its own block class
    LAPIS("lapis", () -> Blocks.LAPIS_ORE, UniformInt.of(2, 5), true),
    DIAMOND("diamond", () -> Blocks.DIAMOND_ORE, UniformInt.of(3, 7), true),
    EMERALD("emerald", () -> Blocks.EMERALD_ORE, UniformInt.of(3, 7), true);

    public final String id;
    /** Vanilla ore whose block properties (hardness, tool requirement, sound) are copied. */
    public final Supplier<Block> vanilla;
    public final IntProvider xp;
    /** Disabled ores are not registered and not generated. Keep in sync with "enabled" in tools/generate_resources.py. */
    public final boolean enabled;

    OreType(String id, Supplier<Block> vanilla, IntProvider xp, boolean enabled) {
        this.id = id;
        this.vanilla = vanilla;
        this.xp = xp;
        this.enabled = enabled;
    }
}
