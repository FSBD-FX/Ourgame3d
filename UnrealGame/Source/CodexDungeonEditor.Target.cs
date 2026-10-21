using UnrealBuildTool;

public class CodexDungeonEditorTarget : TargetRules
{
    public CodexDungeonEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_5;
        ExtraModuleNames.Add("CodexDungeon");
    }
}
