#!/usr/bin/env bash
# Starts a real dedicated server with the mod jar and checks that blocks and ore features work.
# usage: tools/smoke_test.sh <fabric|neoforge|forge|neoforge-legacy> <minecraft version> <path to mod jar> [loader version]
#   neoforge        = NeoForge 21.x (Minecraft 1.21+)
#   forge           = Minecraft Forge 1.20.1
#   neoforge-legacy = NeoForge 1.20.1 (net.neoforged:forge)
# Runs in CI (needs curl, jq, java). Result is reported as GitHub annotations (::notice / ::error).
set -uo pipefail
LOADER=$1; MC=$2; JAR=$(realpath "$3"); VERSION_OVERRIDE=${4:-}
NS=ore_stones_variants_revamped
WORK=$(mktemp -d); cd "$WORK"; mkdir mods; cp "$JAR" mods/

fail() {
  echo "::error title=SMOKE FAIL $LOADER $MC::$1"
  if [ -f server.log ]; then
    grep -iE "ERROR|Exception|Caused by|$NS|Failed|missing|Changed the block|Placed|not loaded|Unknown|Could not|forceload|Marked" server.log | cut -c1-400 | sed 's/%/%25/g' | head -9 | while read -r l; do echo "::error title=log $LOADER $MC::$l"; done
    echo "----- last 60 log lines -----"; tail -60 server.log
  fi
  exit 1
}

echo "eula=true" > eula.txt
printf 'online-mode=false\nlevel-seed=12345\nview-distance=4\nsimulation-distance=4\nmax-tick-time=-1\n' > server.properties

case "$LOADER" in
  fabric)
    LV=$(curl -fsSL "https://meta.fabricmc.net/v2/versions/loader/$MC" | jq -r '[.[]|select(.loader.stable)][0].loader.version') || fail "cannot get fabric loader version"
    IV=$(curl -fsSL https://meta.fabricmc.net/v2/versions/installer | jq -r '[.[]|select(.stable)][0].version') || fail "cannot get fabric installer version"
    curl -fsSL -o server.jar "https://meta.fabricmc.net/v2/versions/loader/$MC/$LV/$IV/server/jar" || fail "cannot download fabric server"
    API_URL=$(curl -fsSLG "https://api.modrinth.com/v2/project/fabric-api/version" --data-urlencode "game_versions=[\"$MC\"]" --data-urlencode 'loaders=["fabric"]' | jq -r '.[0].files[0].url') || fail "cannot query fabric api"
    [ -n "$API_URL" ] && [ "$API_URL" != "null" ] || fail "no Fabric API for $MC"
    curl -fsSL -o mods/fabric-api.jar "$API_URL" || fail "cannot download fabric api"
    CMD=(java -Xmx2G -jar server.jar nogui)
    ;;
  neoforge)
    MINOR=${MC#1.21.}; [ "$MINOR" = "$MC" ] && MINOR=0
    PREFIX="21.$MINOR."
    V=$(curl -fsSL https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml | grep -o "<version>$PREFIX[^<]*</version>" | sed 's/<[^>]*>//g' | tail -1)
    [ -n "$V" ] || fail "no NeoForge $PREFIX* version found"
    echo "NeoForge version: $V"
    curl -fsSL -o installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/$V/neoforge-$V-installer.jar" || fail "cannot download neoforge installer"
    java -jar installer.jar --installServer > install.log 2>&1 || { cp install.log server.log; fail "neoforge installer failed"; }
    echo "-Xmx2G" >> user_jvm_args.txt
    CMD=(java @user_jvm_args.txt "@libraries/net/neoforged/neoforge/$V/unix_args.txt" nogui)
    ;;
  forge|neoforge-legacy)
    if [ "$LOADER" = forge ]; then
      MAVEN=https://maven.minecraftforge.net/net/minecraftforge/forge; PATHDIR=net/minecraftforge/forge
    else
      MAVEN=https://maven.neoforged.net/releases/net/neoforged/forge; PATHDIR=net/neoforged/forge
    fi
    if [ -n "$VERSION_OVERRIDE" ]; then V="$MC-$VERSION_OVERRIDE"
    else V=$(curl -fsSL "$MAVEN/maven-metadata.xml" | grep -o "<version>$MC-[^<]*</version>" | sed 's/<[^>]*>//g' | tail -1)
    fi
    [ -n "$V" ] || fail "no $LOADER version found for $MC"
    echo "$LOADER version: $V"
    curl -fsSL -o installer.jar "$MAVEN/$V/forge-$V-installer.jar" || fail "cannot download $LOADER installer"
    java -jar installer.jar --installServer > install.log 2>&1 || { cp install.log server.log; fail "$LOADER installer failed"; }
    echo "-Xmx2G" >> user_jvm_args.txt
    CMD=(java @user_jvm_args.txt "@libraries/$PATHDIR/$V/unix_args.txt" nogui)
    ;;
  *) fail "unknown loader $LOADER" ;;
esac

# Wait until the server reports "Done", generate 64 chunks naturally and count ore variant blocks
# (fill ... replace #tag reports how many blocks matched), then place blocks / features by hand and stop.
commander() {
  for i in $(seq 1 200); do grep -q 'Done (' server.log 2>/dev/null && break; sleep 2; done
  sleep 3
  echo "forceload add -64 -64 63 63"
  for i in $(seq 1 40); do
    echo "execute if loaded 63 64 63 run say GEN_LOADED"
    sleep 5
    grep -q 'GEN_LOADED' server.log 2>/dev/null && break
    if grep -q 'Unknown or incomplete command' server.log 2>/dev/null; then sleep 70; break; fi
  done
  sleep 3
  for ore in coal copper iron gold redstone lapis diamond emerald; do
    for region in stone tuff; do
      if [ "$region" = stone ]; then y1=0; y2=120; else y1=-64; y2=-1; fi
      echo "say GENCOUNT $ore $region"
      for cx in -4 -3 -2 -1 0 1 2 3; do
        for cz in -4 -3 -2 -1 0 1 2 3; do
          echo "fill $((cx*16)) $y1 $((cz*16)) $((cx*16+15)) $y2 $((cz*16+15)) minecraft:air replace #$NS:variants/$ore"
          sleep 0.1
        done
      done
    done
  done
  echo "say GENCOUNT_END"
  sleep 3
  echo "setblock 0 100 0 $NS:tuff_redstone_ore"
  sleep 1
  echo "setblock 1 100 0 $NS:andesite_coal_ore"
  sleep 1
  echo "fill 0 -40 0 8 -30 8 minecraft:tuff"
  sleep 1
  for pos in "4 -35 4" "5 -34 3" "3 -36 5"; do
    echo "place feature $NS:ore_coal_tuff_variants $pos"
    sleep 1
  done
  echo "fill 0 20 0 8 30 8 minecraft:granite"
  sleep 1
  for pos in "4 25 4" "5 26 3" "3 24 5"; do
    echo "place feature $NS:ore_coal_variants $pos"
    sleep 1
  done
  sleep 4
  echo "stop"
  sleep 8
}
commander | timeout 900 "${CMD[@]}" > server.log 2>&1
echo "server exit code: $?"

grep -q 'Done (' server.log || fail "server did not finish loading"
grep -q "Changed the block at 0, 100, 0" server.log || fail "setblock tuff_redstone_ore did not work (block missing?)"
grep -q "Changed the block at 1, 100, 0" server.log || fail "setblock andesite_coal_ore did not work (block missing?)"
grep -q "Placed \"$NS:ore_coal_tuff_variants\"" server.log || fail "tuff ore feature was not placed (worldgen JSON not loaded?)"
grep -q "Placed \"$NS:ore_coal_variants\"" server.log || fail "stone ore feature was not placed (worldgen JSON not loaded?)"
if grep -E "Failed to load|Couldn't parse|Parsing error|Unbound values|Missing" server.log | grep -qi "$NS"; then fail "errors mentioning the mod found in log"; fi
# ---- natural generation report ----
COUNTS=$(awk '/GENCOUNT_END/ {next} /GENCOUNT / {t=$0; sub(/.*GENCOUNT /,"",t); split(t,b," "); key=b[1]"_"b[2]; next} /Successfully filled/ {n=$0; sub(/.*filled /,"",n); sub(/ block.*/,"",n); cnt[key]+=n} END {for (k in cnt) print k, cnt[k]}' server.log | sort)
count_of() { echo "$COUNTS" | awk -v k="$1" '$1==k {print $2}' | head -1 | grep . || echo 0; }
grep -q 'GENCOUNT_END' server.log || fail "natural generation count did not finish"
REPORT=""
for ore in coal copper iron gold redstone lapis diamond emerald; do
  REPORT="$REPORT $ore: stone=$(count_of ${ore}_stone) tuff=$(count_of ${ore}_tuff);"
done
echo "::notice title=GEN $LOADER $MC (ore blocks in 64 chunks)::$REPORT"
echo "GEN $LOADER $MC (ore blocks in 64 chunks):$REPORT"
for ore in coal copper iron redstone; do
  [ "$(count_of ${ore}_stone)" -gt 0 ] || fail "no natural $ore variants in stone (biome hook / placement broken?). counts:$REPORT"
  [ "$(count_of ${ore}_tuff)" -gt 0 ] || fail "no natural $ore variants in tuff (biome hook / placement broken?). counts:$REPORT"
done
echo "::notice title=SMOKE PASS $LOADER $MC::server started, blocks registered, ore features placed"
echo "SMOKE PASS $LOADER $MC"
