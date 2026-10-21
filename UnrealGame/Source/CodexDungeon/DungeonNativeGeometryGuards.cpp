#include "DungeonNativeGeometryGuards.h"
#include "Components/PrimitiveComponent.h"
#include "Debug/DebugDrawComponent.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "PhysicsEngine/BodyInstance.h"

bool DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(
    const UWorld* World,const AActor* Actor,const UPrimitiveComponent* Component)
{
    if(!IsInGameThread()||!IsValid(World)||!IsValid(Actor)||!IsValid(Component)
        ||Actor->IsActorBeingDestroyed()||Component->IsBeingDestroyed())return false;
    // These are native UClass identities, not actor instance names or a generic
    // DebugDraw inheritance exemption. Subclasses and user geometry do not pass.
    const auto* ActorClass=Actor->GetClass();const auto* ComponentClass=Component->GetClass();
    if(!ActorClass->HasAnyClassFlags(CLASS_Native)||!ActorClass->HasAnyClassFlags(CLASS_Transient)
        ||!ComponentClass->HasAnyClassFlags(CLASS_Native)||!ComponentClass->HasAnyClassFlags(CLASS_Transient)
        ||!ActorClass->GetPathName().Equals(TEXT("/Script/GameplayDebugger.GameplayDebuggerCategoryReplicator"),ESearchCase::CaseSensitive)
        ||!ComponentClass->GetPathName().Equals(TEXT("/Script/GameplayDebugger.GameplayDebuggerRenderingComponent"),ESearchCase::CaseSensitive)
        ||!Component->IsA<UDebugDrawComponent>())return false;
    if(Actor->GetWorld()!=World||Component->GetWorld()!=World||Component->GetOwner()!=Actor
        ||Component->GetOuter()!=Actor||Actor->GetRootComponent()!=Component||Component->GetAttachParent()
        ||!Component->IsRegistered())return false;
    TInlineComponentArray<UPrimitiveComponent*> Primitives;Actor->GetComponents(Primitives);
    if(Primitives.Num()!=1||Primitives[0]!=Component)return false;
    // UE5.5's exact native rendering class inherits UPrimitiveComponent's
    // null-returning GetBodySetup. Its signature lacks const, so cast only after
    // native exact-type checks; never invoke lazy geometry getters on other types.
    if(const_cast<UPrimitiveComponent*>(Component)->GetBodySetup())return false;
    const auto* RawBody=Component->GetBodyInstance(NAME_None,false);
    // IsPhysicsStateCreated is bookkeeping and may be true without InitBody.
    // The actual raw native body/setup/weld decide whether this is draw-only.
    return RawBody&&!RawBody->IsValidBodyInstance()&&!RawBody->GetBodySetup()&&!RawBody->WeldParent;
}
