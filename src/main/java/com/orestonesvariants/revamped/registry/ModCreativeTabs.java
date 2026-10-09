package com.orestonesvariants.revamped.registry;

import com.orestonesvariants.revamped.OreStonesVariantsRevamped;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, OreStonesVariantsRevamped.MODID);

    public static final RegistryObject<CreativeModeTab> MAIN = TABS.register("main", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup." + OreStonesVariantsRevamped.MODID))
                    .icon(() -> new ItemStack(ModBlocks.ICON_BLOCK.get()))
                    .displayItems((params, output) ->
                            ModBlocks.ALL_ORES.forEach(block -> output.accept(block.get())))
                    .build());

    private ModCreativeTabs() {}
}
