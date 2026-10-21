#pragma once
#include "DungeonHeroAirPresentation.h"
class ADungeonFighter{public:float HitFlash=0.f,JumpHeight=0.f;FDungeonHeroAirSample Sample;bool QueryHeroNonAttackAir(FDungeonHeroAirSample& Out)const{Out=Sample;return Sample.Valid;}};
