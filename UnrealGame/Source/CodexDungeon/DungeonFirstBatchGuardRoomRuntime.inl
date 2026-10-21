// Compiled only as part of ADungeonGameMode. Root owns actual native admission.
bool ADungeonGameMode::BeginFirstBatchGuardRoom(uint64 Seed)
{
 if(IsRunInstallGated()||!IsValid(PlayerFighter)||!GetWorld())return false;
 const auto Layout=DungeonRoomLayout::ExplorationPreview();
 PlayerFighter->SetActorLocation(FVector(Layout.Entry.X,Layout.Entry.Y,0));
 if(!BeginEquipmentRun(EDungeonEquipmentRunConfig::FirstBatch,Seed))return false;
 PlayerFighter->SetActorTickEnabled(false);
 if(!SceneObjects->BeginRoom(EquipmentRuntime->View.RunGuid,1)||!SpawnSceneExplorationRoom())return false;
 FString Why;
 if(!RunRewards->BeginFirstBatchGuardPlan(Seed,SceneEncounterEntityId,SimulationTime,Why))
 {LastMessage=TEXT("Bridge房间计划拒绝：")+Why;bWaitingForStart=true;return false;}
 bWaitingForStart=true;bFirstBatchGuardRoomRequested=true;
 LastMessage=TEXT("石廊试炼：三个固定敌人槽位，前组终结后才预告后组。Enter开始。");return true;
}
void ADungeonGameMode::StartFirstBatchGuardRoom(){BeginFirstBatchGuardRoom(71);}
bool ADungeonGameMode::QueryFirstBatchGuardRoom(FDungeonFirstBatchGuardRoomView& Out) const
{
 if(!RunRewards)return false;const auto S=RunRewards->Capture();
 if(S.Schema!=2||S.RoomPlans.IsEmpty()||S.RoomPlans.Last().RoomInstanceId!=GetEquipmentView().RoomInstanceId)return false;
 Out=S.RoomPlans.Last();return true;
}
bool ADungeonGameMode::GuardRoomMayStartAttack(uint64 Entity,double At) const
{
 FDungeonFirstBatchGuardRoomView P;if(!QueryFirstBatchGuardRoom(P))return true;
 const auto* X=P.Slots.FindByPredicate([Entity](const auto& S){return S.EntityId==Entity;});
 return X&&At>=P.OrientationUntil&&At>=X->MaterializedAt+.6;
}
bool ADungeonGameMode::GuardRoomAnchorLegal(FVector2D P,FVector2D Half,double MinimumDistance) const
{
 if(!IsValid(PlayerFighter)||(P-PlayerFighter->GetGroundPosition()).Size()<MinimumDistance)return false;
 const auto Bounds=DungeonRoomLayout::CenterBounds();
 if(!Bounds.IsInsideOrOn(P-Half)||!Bounds.IsInsideOrOn(P+Half))return false;
 const auto& Wall=SceneObjects->Current().Layout.Barrier;
 if(FBox2D(P-Half,P+Half).Intersect(Wall))return false;
 // Warning candidates remain within the authored view footprint around the
 // player's ground projection. Native screenshot acceptance is still required.
 const auto Observer=PlayerFighter->GetGroundPosition();const auto D=P-Observer;
 if(FMath::Abs(D.X)>800.||FMath::Abs(D.Y)>600.
  ||DungeonExploration::FExploration::VisibilityAt({P.X,P.Y},{Observer.X,Observer.Y})<=.05)return false;
 for(const auto& B:CaptureKnightBodies())if(B.bAlive&&B.bBlocksBody)
 {const auto V=P-B.Start,Sum=Half+B.BodyHalfExtent;if(FMath::Abs(V.X)<Sum.X&&FMath::Abs(V.Y)<Sum.Y)return false;}
 FCollisionQueryParams Params(SCENE_QUERY_STAT(BridgeWarningLOS),false);Params.AddIgnoredActor(PlayerFighter);
 for(auto E:Enemies)if(IsValid(E))Params.AddIgnoredActor(E);
 FHitResult Hit;return !GetWorld()->LineTraceSingleByObjectType(Hit,FVector(Observer.X,Observer.Y,0),FVector(P.X,P.Y,0),
  FCollisionObjectQueryParams(ECC_WorldStatic),Params)||!Hit.bBlockingHit;
}
void ADungeonGameMode::AdvanceFirstBatchGuardRoom()
{
 if(IsRunInstallGated()||bGameOver||bWaitingForStart||!IsValid(PlayerFighter)||PlayerFighter->bDead)return;
 // Called after the complete same-timestamp damage/death batch, before any
 // future admission. Death during that batch cannot create a new wave or payout.
 for(auto E:Enemies)if(IsValid(E)&&E->bDead&&!E->bDeathReported)SettleFirstBatchGuardDeath(E);
 FDungeonFirstBatchGuardRoomView P;if(!QueryFirstBatchGuardRoom(P)||P.ClearAt>=0.)return;
 for(int32 I=1;I<P.Slots.Num();++I)
 {
  auto& X=P.Slots[I];if(X.Stage==EDungeonGuardRoomSlotStage::Dead||X.Stage==EDungeonGuardRoomSlotStage::Materialized)continue;
  if(P.Slots[I-1].Stage!=EDungeonGuardRoomSlotStage::Dead||SimulationTime<P.Slots[I-1].DeadAt+2.||SimulationTime<P.OrientationUntil)return;
  if(X.RetryAt>=0.&&SimulationTime<X.RetryAt)return;
  if(X.Stage==EDungeonGuardRoomSlotStage::Future&&X.AnchorAttempt>=DungeonGuardRoomRewardsV2::MaxAnchorAttempts)
  {LastMessage=TEXT("合法入口持续受阻；技术暂停，保留槽位／生命／预分配，可重开调查。");bWaitingForStart=true;return;}
  const auto BatDefinition=DungeonStoneBat::FBatKernel::Definition();const auto GuardDefinition=DungeonStoneGuard::FGuardKernel::Definition();
  const FVector2D Half=I==1?FVector2D(BatDefinition.BodyHalfX,BatDefinition.BodyHalfY):FVector2D(GuardDefinition.BodyHalfX,GuardDefinition.BodyHalfY);
  if(X.Stage==EDungeonGuardRoomSlotStage::Future)
  {
   bool Found=false;
   for(uint32 N=0;N<DungeonGuardRoomRewardsV2::AnchorCount;++N,++X.AnchorAttempt)
   {
    X.SpawnPosition=DungeonGuardRoomRewardsV2::Anchor(P.Seed,I,X.AnchorAttempt);
    if(GuardRoomAnchorLegal(X.SpawnPosition,Half,350.)){Found=true;break;}
   }
   if(!Found){X.RetryAt=SimulationTime+1.;X.SpawnPosition=DungeonGuardRoomRewardsV2::Anchor(P.Seed,I,X.AnchorAttempt);}
   else{X.WarningAt=SimulationTime;X.RetryAt=-1.;X.Stage=EDungeonGuardRoomSlotStage::Warning;LastMessage=TEXT("入口正在预告，后组尚未出生。");}
   FString Why;if(!RunRewards->CommitFirstBatchGuardPlan(P,Why)){LastMessage=Why;bWaitingForStart=true;}return;
  }
  if(X.Stage==EDungeonGuardRoomSlotStage::Warning&&SimulationTime>=X.WarningAt+1.2)
  {
   if(!GuardRoomAnchorLegal(X.SpawnPosition,Half,220.))
   {X.Stage=EDungeonGuardRoomSlotStage::Future;X.WarningAt=-1.;X.RetryAt=SimulationTime+1.;++X.AnchorAttempt;
    X.SpawnPosition=DungeonGuardRoomRewardsV2::Anchor(P.Seed,I,X.AnchorAttempt);FString Why;
    if(!RunRewards->CommitFirstBatchGuardPlan(P,Why)){LastMessage=Why;bWaitingForStart=true;}return;}
   ADungeonFighter* E=I==1?SpawnStoneBat(X.SpawnPosition):SpawnStoneGuard(X.SpawnPosition);
   if(!E){LastMessage=TEXT("出生失败，保留同一槽位与预分配；请检查原生接纳。");bWaitingForStart=true;return;}
   X.EntityId=FindWorldEntityId(E);X.MaterializedAt=SimulationTime;X.RetryAt=-1.;X.Stage=EDungeonGuardRoomSlotStage::Materialized;
   FString Why;if(!RunRewards->CommitFirstBatchGuardPlan(P,Why)){LastMessage=Why;bWaitingForStart=true;return;}
   E->bAIEnabled=true;LastMessage=TEXT("后组已真实显现；原生苏醒与完整攻击前摇继续。");return;
  }
  return;
 }
}
void ADungeonGameMode::SettleFirstBatchGuardDeath(ADungeonFighter* F)
{
 if(!IsValid(F)||!F->bEnemy||!F->bDead||F->bDeathReported)return;
 if(F->StoneGuard)F->bGuardDeathObserved=true;
 if(bSimulationBatch||bGameOver||!IsValid(PlayerFighter)||PlayerFighter->bDead)return;
 FDungeonFirstBatchGuardRoomView P;if(!QueryFirstBatchGuardRoom(P))return;
 const uint64 Id=FindWorldEntityId(F);const auto* X=P.Slots.FindByPredicate([Id](const auto& S){return S.EntityId==Id;});
 if(!X||X->Stage!=EDungeonGuardRoomSlotStage::Materialized||X->ContentId!=F->EnemyContentId
  ||(X->ContentId==TEXT("ENM-STN-001")&&!F->StoneKnight)||(X->ContentId==TEXT("ENM-STN-002")&&!F->StoneBat)
  ||(X->ContentId==TEXT("ENM-STN-003")&&!F->StoneGuard))return;
 FDungeonRunRewardDeathRequest Q;Q.EntityId=Id;Q.RoomInstanceId=P.RoomInstanceId;Q.ContentId=X->ContentId;
 Q.AtTime=F->StoneKnight?F->StoneKnight->State().Time:F->StoneBat?F->StoneBat->State().Time:F->StoneGuard->State().Time;
 if(F->StoneGuard)
 {
  // A resolved contact can precede the batch endpoint; only the original
  // immutable Died fact owns the paid death clock, never final State.Time.
  int32 DeathEvents=0;
  for(const auto& E:F->StoneGuard->State().Issued)if(E.Kind==DungeonStoneGuard::EEventKind::Died)
  {Q.AtTime=E.AtTime;++DeathEvents;}
  if(DeathEvents!=1){LastMessage=TEXT("Bridge Guard死亡缺少唯一原生Died来源，保留未结算状态。");return;}
 }
 Q.Position=F->GetGroundPosition();Q.FirstDeath=X->Group==0;Q.RoomCleared=X->Group==2;
 auto Candidate=MakeUnique<FDungeonRunRewards>(*RunRewards);FString Why;const auto R=Candidate->ResolveDeath(Q,Why);
 if(!R.Ok()){LastMessage=TEXT("Bridge死亡结算拒绝：")+Why;return;}
 if(F->StoneKnight&&!F->StoneKnight->State().RewardClaimed&&!F->StoneKnight->ClaimDeathReward())return;
 if(F->StoneBat&&!F->StoneBat->State().RewardClaimed&&!F->StoneBat->ClaimDeathReward())return;
 if(F->StoneGuard&&!F->StoneGuard->State().RewardClaimed&&!F->ClaimStoneGuardDeathEligibility())return;
 F->bDeathReported=true;RunRewards=MoveTemp(Candidate);
 const auto S=RunRewards->Capture();for(uint64 Object:R.ObjectIds)
 {
  const auto* O=S.Objects.FindByPredicate([Object](const auto& V){return V.ObjectId==Object;});if(!O)continue;
  FDungeonPickup Drop;Drop.Position=O->Position;Drop.Kind=TEXT("coin");Drop.RunGuid=S.RunGuid;Drop.ObjectId=O->ObjectId;
  Drop.SourceId=O->SourceId;Drop.RoomInstanceId=O->RoomInstanceId;Pickups.Add(Drop);
 }
 bRoomCleared=S.RoomPlans.Last().ClearAt>=0.;
 LastMessage=bRoomCleared?TEXT("三槽试炼已全清；金币仍须实际靠近拾取。"):TEXT("本组结束，后组喘息与入口预告继续。");
}
