using UnrealBuildTool;

public class CodexDungeon : ModuleRules
{
    public CodexDungeon(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "RenderCore", "Json", "AudioMixer" });
        PrivateDependencyModuleNames.AddRange(new[] { "ImageCore", "ImageWrapper", "RHI" });
    }
}
