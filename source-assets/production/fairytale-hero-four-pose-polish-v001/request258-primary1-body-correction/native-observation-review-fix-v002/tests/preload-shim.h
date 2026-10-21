#pragma once
#include "ue-small-shim.h"
#include <map>
#include <memory>
#include <set>
struct FPreloadParse{static bool Param(const wchar_t*,const wchar_t* Name){const std::wstring N(Name);return N==L"DungeonFairytaleLeatherPrimary1Preview"||(N==L"DungeonFairytalePrimary1Bridge258Preview"&&HostFlag);}static bool Value(const wchar_t*,const wchar_t* Name,FString& Out){if(std::wstring(Name)!=L"DungeonHeroLandingPriorityAction=")return false;Out=HostAction;return true;}};
#define FParse FPreloadParse
template<class T>struct FPreloadArray:std::vector<T>{using std::vector<T>::vector;void Add(const T& V){this->push_back(V);}template<class... A>void Emplace(A&&... V){this->emplace_back(std::forward<A>(V)...);}};
#define TArray FPreloadArray
struct UTexture2D{FString Path;bool Loaded=false;explicit UTexture2D(FString P):Path(std::move(P)){} };using UTexture=UTexture2D;
inline std::map<std::wstring,std::unique_ptr<UTexture2D>> HostAssets;inline int HostLoadCalls=0,HostFlushCalls=0,HostStrongRefs=0;
template<class T>T* LoadObject(void*,const wchar_t* Path){++HostLoadCalls;const auto I=HostAssets.find(Path);if(I==HostAssets.end())return nullptr;I->second->Loaded=true;return I->second.get();}
inline void FlushRenderingCommands(){++HostFlushCalls;}
template<class T>struct TStrongObjectPtr{T* P=nullptr;explicit TStrongObjectPtr(T* V):P(V){if(P)++HostStrongRefs;}TStrongObjectPtr(const TStrongObjectPtr&)=delete;TStrongObjectPtr&operator=(const TStrongObjectPtr&)=delete;TStrongObjectPtr(TStrongObjectPtr&& V)noexcept:P(V.P){V.P=nullptr;}~TStrongObjectPtr(){if(P)--HostStrongRefs;}};
struct FPackageName{static bool DoesPackageExist(const FString& Package){for(const auto& V:HostAssets)if(V.first.substr(0,V.first.rfind(L'.'))==Package.S)return true;return false;}};
struct FHostTexturePtr{UTexture2D* P=nullptr;UTexture2D* Get()const{return P;}};
struct FHostFrames{std::map<std::wstring,FHostTexturePtr> M;FHostTexturePtr* Find(const FString& Name){auto I=M.find(Name.S);return I==M.end()?nullptr:&I->second;}void Add(const FString& Name,UTexture2D* P){M[Name.S]={P};}};
class ADungeonHUD{public:bool bUseFairytaleSwordEquipmentBoundPreview=true;FHostFrames Frames;UTexture2D* GetFairytaleSwordArmorPrimary1Texture(const FString&,int32);void RunActualPrimary1Preload(){TArray<UTexture*> ReadyArmorTextures;
#include "actual-hud-primary1-loop.inc"
}};
