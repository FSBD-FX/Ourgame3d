using UnrealBuildTool;

public class CodexDungeonTarget : TargetRules
{
    public CodexDungeonTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_5;
        ExtraModuleNames.Add("CodexDungeon");
    }
}
