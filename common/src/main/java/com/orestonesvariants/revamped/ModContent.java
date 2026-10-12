package com.orestonesvariants.revamped;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.RedStoneOreBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;

import java.util.ArrayList;
import java.util.List;

/**
 * Loader independent content definition. The NeoForge and Fabric modules only register
 * what is described here, so both loaders always get the same blocks.
 * Block ids must match the files produced by tools/generate_resources.py.
 */
public final class ModContent {
    public static final String MODID = "ore_stones_variants_revamped";

    /** One block: host stone + ore, e.g. "granite_redstone_ore". */
    public record Entry(String name, HostStone stone, OreType ore) {}

    public static final List<Entry> ENTRIES = buildEntries();

    private static List<Entry> buildEntries() {
        List<Entry> list = new ArrayList<>();
        for (HostStone stone : HostStone.values()) {
            for (OreType ore : OreType.values()) {
                if (stone.has(ore)) {
                    list.add(new Entry(stone.id + "_" + ore.id + "_ore", stone, ore));
                }
            }
        }
        return List.copyOf(list);
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }

    public static Block createBlock(Entry entry) {
        Block template = entry.stone() == HostStone.TUFF ? entry.ore().deepslate.get() : entry.ore().vanilla.get();
        BlockBehaviour.Properties props = BlockBehaviour.Properties.ofFullCopy(template);
        if (entry.ore() == OreType.REDSTONE) {
            // ofFullCopy keeps the "lit" light level function of vanilla redstone ore
            return new RedStoneOreBlock(props);
        }
        return new DropExperienceBlock(entry.ore().xp, props);
    }

    public static CreativeModeTab createTab() {
        return CreativeModeTab.builder()
                .title(Component.translatable("itemGroup." + MODID))
                .icon(() -> new ItemStack(BuiltInRegistries.ITEM.get(id("andesite_diamond_ore"))))
                .displayItems((parameters, output) -> {
                    for (Entry entry : ENTRIES) {
                        output.accept(BuiltInRegistries.ITEM.get(id(entry.name())));
                    }
                })
                .build();
    }

    private ModContent() {}
}
