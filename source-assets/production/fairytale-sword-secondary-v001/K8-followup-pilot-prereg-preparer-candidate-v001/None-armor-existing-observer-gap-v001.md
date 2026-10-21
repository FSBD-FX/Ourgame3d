# Existing native observer None-armor boundary

The actual admitted `F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp` is47014 bytes / `5f0d0a978a4defb61ec338bc4d77a31ae51f45a68bba1b284d143eecb60044a9`, pinned by current CM8936717c…. It has no truthful None-armor selection for this normal K route.

- Lines147–149: Gear() requires `EArmor::LightArmor`, the exact LGT instance/version, SWD instance and legal cooldown version receipt.
- Line233: every active K callback requires ExpectedDrawCount==8.
- Line248: the normal route registers a QA display `ARM-LGT-001` source.
- Line249: normal E completion must put that LGT instance into armor slot2 before the route proceeds.
- Lines259–268 parse case/prereg and fixed proof flags; there is no optional armor mode or None branch.

The K presentation runtime has a None5 drawing branch, but that does not make this observer capable of proving a normal None route. Passing an invented armor JSON field would leave the actual observer in LGT and would mislabel the evidence. This helper therefore exposes no None selector and records `armor_scope=LGT_ONLY`, `None_armor_supported=false` for its existing observer scope.

No Source change is implemented. A later separate, reviewed native observer route would be needed to omit actual LGT acquisition, authorize actual no-armor binding, expect five slots and serialize/prove that state. That remains a real coverage gap rather than a completed native test.
