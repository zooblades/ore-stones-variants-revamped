package com.orestonesvariants.revamped.registry;

/** Stones in which the ore variants generate. */
public enum HostStone {
    ANDESITE("andesite"),
    DIORITE("diorite"),
    GRANITE("granite");

    public final String id;

    HostStone(String id) {
        this.id = id;
    }
}
