package com.orestonesvariants.revamped.fabric;

import com.orestonesvariants.revamped.GeneratedFeatures;
import com.orestonesvariants.revamped.ModContent;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.BiomeTags;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;

public class OreStonesVariantsRevampedFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        for (ModContent.Entry entry : ModContent.ENTRIES) {
            Block block = Registry.register(BuiltInRegistries.BLOCK, ModContent.id(entry.name()), ModContent.createBlock(entry));
            Registry.register(BuiltInRegistries.ITEM, ModContent.id(entry.name()), ModContent.createBlockItem(entry, block));
        }
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, ModContent.id("main"), ModContent.createTab(FabricItemGroup.builder()));

        // The placed features themselves are data (worldgen JSON); here we only hook them into biomes.
        for (String feature : GeneratedFeatures.OVERWORLD) {
            BiomeModifications.addFeature(BiomeSelectors.foundInOverworld(), GenerationStep.Decoration.UNDERGROUND_ORES,
                    ResourceKey.create(Registries.PLACED_FEATURE, ModContent.id(feature)));
        }
        for (String feature : GeneratedFeatures.MOUNTAINS) {
            BiomeModifications.addFeature(BiomeSelectors.tag(BiomeTags.IS_MOUNTAIN), GenerationStep.Decoration.UNDERGROUND_ORES,
                    ResourceKey.create(Registries.PLACED_FEATURE, ModContent.id(feature)));
        }
    }
}
