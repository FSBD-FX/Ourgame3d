   for(int32 Index=0;Index<Bridge258LegacyReadbackRefs.Num();++Index)
    Bridge258LegacyResidencyBefore.Add(MakeShared<FJsonValueObject>(Bridge258LegacyResidencyStatus(Bridge258LegacyRequestedPaths[Index],Bridge258LegacyReadbackRefs[Index].Get())));
#if WITH_EDITOR
   // UObject load/render flush do not complete editor platform-data compilation.
   // Restrict this pre-audio/pre-input barrier to the fourteen retained old layers.
   TArray<UTexture*> Bridge258LegacyCompilationTargets;
   for(const auto& Ref:Bridge258LegacyReadbackRefs)if(Ref.Get())Bridge258LegacyCompilationTargets.Add(Ref.Get());
   Bridge258LegacyFinishRequested=true;Bridge258LegacyFinishTargetCount=Bridge258LegacyCompilationTargets.Num();
   FTextureCompilingManager::Get().FinishCompilation(Bridge258LegacyCompilationTargets);
#endif
