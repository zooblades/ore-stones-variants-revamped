package com.orestonesvariants.revamped.forge;

import com.orestonesvariants.revamped.ModContent;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(ModContent.MODID)
public class OreStonesVariantsRevamped {
    public OreStonesVariantsRevamped() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();
        DeferredRegister<Block> blocks = DeferredRegister.create(ForgeRegistries.BLOCKS, ModContent.MODID);
        DeferredRegister<Item> items = DeferredRegister.create(ForgeRegistries.ITEMS, ModContent.MODID);
        DeferredRegister<CreativeModeTab> tabs = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ModContent.MODID);

        for (ModContent.Entry entry : ModContent.ENTRIES) {
            RegistryObject<Block> block = blocks.register(entry.name(), () -> ModContent.createBlock(entry));
            items.register(entry.name(), () -> new BlockItem(block.get(), new Item.Properties()));
        }
        tabs.register("main", () -> ModContent.createTab(CreativeModeTab.builder()));

        blocks.register(modEventBus);
        items.register(modEventBus);
        tabs.register(modEventBus);
    }
}
