package com.orestonesvariants.revamped.neoforge;

import com.orestonesvariants.revamped.ModContent;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.registries.DeferredRegister;

@Mod(ModContent.MODID)
public class OreStonesVariantsRevamped {
    public OreStonesVariantsRevamped(IEventBus modEventBus) {
        DeferredRegister.Blocks blocks = DeferredRegister.createBlocks(ModContent.MODID);
        DeferredRegister.Items items = DeferredRegister.createItems(ModContent.MODID);
        DeferredRegister<CreativeModeTab> tabs = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ModContent.MODID);

        for (ModContent.Entry entry : ModContent.ENTRIES) {
            var block = blocks.register(entry.name(), () -> ModContent.createBlock(entry));
            items.register(entry.name(), () -> new BlockItem(block.get(), new Item.Properties()));
        }
        tabs.register("main", () -> ModContent.createTab(CreativeModeTab.builder()));

        blocks.register(modEventBus);
        items.register(modEventBus);
        tabs.register(modEventBus);
    }
}
