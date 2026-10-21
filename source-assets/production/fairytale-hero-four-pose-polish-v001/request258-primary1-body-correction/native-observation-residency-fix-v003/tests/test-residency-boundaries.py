"""Static source boundary checks only; never a UE compilation/residency PASS."""
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent.parent
SOURCE=(HERE/'projected/DungeonHeroLandingPriorityProbeV001.cpp').read_text(encoding='utf-8')
PRELOAD=SOURCE[SOURCE.index('TArray<TStrongObjectPtr<UTexture2D>> Bridge258LegacyReadbackRefs;'):SOURCE.index('IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);')]

class Boundaries(unittest.TestCase):
    def test_compilation_barrier_precedes_original_flush_and_strict_capture(self):
        call='FTextureCompilingManager::Get().FinishCompilation(Bridge258LegacyCompilationTargets);'
        self.assertIn(call,PRELOAD)
        self.assertLess(PRELOAD.index('LoadObject<UTexture2D>'),PRELOAD.index(call))
        self.assertLess(PRELOAD.index(call),PRELOAD.index('FlushRenderingCommands();'))
        self.assertLess(SOURCE.index(call),SOURCE.index('UTexture2D* T=FindObject<UTexture2D>(nullptr,*Path);'))
    def test_compilation_targets_are_only_loaded_old14_inside_existing_optin_J(self):
        self.assertIn('if(Bridge258ObservationEnabled()&&Action==TEXT("J"))',PRELOAD)
        self.assertIn('for(const auto& Ref:Bridge258LegacyReadbackRefs)if(Ref.Get())Bridge258LegacyCompilationTargets.Add(Ref.Get());',PRELOAD)
        self.assertIn('#if WITH_EDITOR',PRELOAD)
        self.assertNotIn('FinishAllCompilation',SOURCE)
    def test_before_and_after_are_real_snapshots_on_each_side_of_barrier(self):
        before='Bridge258LegacyResidencyBefore.Add(MakeShared<FJsonValueObject>(Bridge258LegacyResidencyStatus(' 
        after='Bridge258LegacyResidencyAfter.Add(MakeShared<FJsonValueObject>(Bridge258LegacyResidencyStatus('
        self.assertIn(before,PRELOAD);self.assertIn(after,PRELOAD)
        self.assertLess(PRELOAD.index(before),PRELOAD.index('FinishCompilation('))
        self.assertLess(PRELOAD.index('FlushRenderingCommands();'),PRELOAD.index(after))
        self.assertIn('R->SetObjectField(TEXT("request258_primary1_legacy_residency"),LegacyResidency);',SOURCE)
    def test_missing_objects_and_editor_only_status_remain_explicitly_unavailable(self):
        self.assertIn('JO Bridge258LegacyResidencyStatus(',SOURCE)
        helper=SOURCE[SOURCE.index('JO Bridge258LegacyResidencyStatus('):SOURCE.index('struct FDungeonHeroLandingPriorityProofStateV001')]
        self.assertIn('if(!Texture)',helper)
        self.assertIn('MakeShared<FJsonValueNull>()',helper)
        self.assertIn('Texture->IsCompiling()',helper)
        self.assertIn('Texture->IsAsyncCacheComplete()',helper)
        self.assertIn('Resource->IsProxy()',helper)
        self.assertIn('Resource->IsInitialized()',helper)
    def test_no_asset_mutation_or_global_compilation_shortcut_is_added(self):
        self.assertNotIn('FinishAllCompilation',PRELOAD)
        self.assertNotIn('->UpdateResource(',PRELOAD)
        self.assertNotIn('->FinishCachePlatformData(',PRELOAD)

if __name__=='__main__':unittest.main(verbosity=2)
