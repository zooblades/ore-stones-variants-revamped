package com.orestonesvariants.revamped.registry;

import com.orestonesvariants.revamped.OreStonesVariantsRevamped;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.RedStoneOreBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

/**
 * Registers every host stone x ore combination, e.g. "andesite_coal_ore".
 * Block ids must match the files produced by tools/generate_resources.py.
 */
public final class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, OreStonesVariantsRevamped.MODID);
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, OreStonesVariantsRevamped.MODID);

    public static final List<RegistryObject<Block>> ALL_ORES = new ArrayList<>();
    public static RegistryObject<Block> ICON_BLOCK;

    static {
        for (HostStone stone : HostStone.values()) {
            for (OreType ore : OreType.values()) {
                if (!ore.enabled) {
                    continue;
                }
                String name = stone.id + "_" + ore.id + "_ore";
                RegistryObject<Block> block = BLOCKS.register(name, () -> createBlock(ore));
                ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
                ALL_ORES.add(block);
                if (stone == HostStone.ANDESITE && ore == OreType.DIAMOND) {
                    ICON_BLOCK = block;
                }
            }
        }
    }

    private static Block createBlock(OreType ore) {
        BlockBehaviour.Properties props = BlockBehaviour.Properties.copy(ore.vanilla.get());
        if (ore == OreType.REDSTONE) {
            // copy() also keeps the "lit" light level function of vanilla redstone ore
            return new RedStoneOreBlock(props);
        }
        return new DropExperienceBlock(props, ore.xp);
    }

    private ModBlocks() {}
}
