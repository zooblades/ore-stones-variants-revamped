package com.orestonesvariants.revamped.registry;

/** Blocks in which the ore variants generate. */
public enum HostStone {
    ANDESITE("andesite"),
    DIORITE("diorite"),
    GRANITE("granite"),
    TUFF("tuff"),
    /** Only lapis is generated in sandstone. */
    SANDSTONE("sandstone");

    public final String id;

    HostStone(String id) {
        this.id = id;
    }

    /** Which ores exist for this host. Keep in sync with GROUPS in tools/generate_resources.py. */
    public boolean has(OreType ore) {
        return this != SANDSTONE || ore == OreType.LAPIS;
    }
}
