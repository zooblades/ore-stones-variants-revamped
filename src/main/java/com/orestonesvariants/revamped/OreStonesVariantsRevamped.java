package com.orestonesvariants.revamped;

import com.orestonesvariants.revamped.registry.ModBlocks;
import com.orestonesvariants.revamped.registry.ModCreativeTabs;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(OreStonesVariantsRevamped.MODID)
public class OreStonesVariantsRevamped {
    public static final String MODID = "ore_stones_variants_revamped";

    public OreStonesVariantsRevamped() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModBlocks.BLOCKS.register(modEventBus);
        ModBlocks.ITEMS.register(modEventBus);
        ModCreativeTabs.TABS.register(modEventBus);
    }
}
