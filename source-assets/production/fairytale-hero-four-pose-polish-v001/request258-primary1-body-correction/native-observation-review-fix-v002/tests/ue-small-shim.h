#pragma once
#include <string>
#include <vector>
#include <cwchar>
#include <cmath>
#include <algorithm>
#include <cstdint>
using int32=std::int32_t;using uint64=std::uint64_t;using TCHAR=wchar_t;
#define TEXT(X) L##X
struct FString{
 std::wstring S;FString()=default;FString(const wchar_t* V):S(V){}FString(std::wstring V):S(std::move(V)){}
 bool IsEmpty()const{return S.empty();}const wchar_t* operator*()const{return S.c_str();}
 bool operator==(const FString& B)const{return S==B.S;}bool operator!=(const FString& B)const{return S!=B.S;}
 FString operator+(const FString& B)const{return FString(S+B.S);}
 template<class... A>static FString Printf(const wchar_t* F,A... V){wchar_t B[2048];std::swprintf(B,2048,F,V...);return FString(B);}
};
template<class T>struct TArray:std::vector<T>{using std::vector<T>::vector;int32 Num()const{return int32(this->size());}bool Contains(const T& V)const{return std::find(this->begin(),this->end(),V)!=this->end();}};
struct FVector2D{double X=0,Y=0;FVector2D()=default;FVector2D(double A,double B):X(A),Y(B){}bool operator==(const FVector2D& B)const{return X==B.X&&Y==B.Y;}bool operator!=(const FVector2D& B)const{return !(*this==B);}};
struct FMath{static double Atan2(double Y,double X){return std::atan2(Y,X);}static double RadiansToDegrees(double X){return X*180./3.14159265358979323846;}};
inline bool HostFlag=false;inline FString HostAction(TEXT("J"));
struct FCommandLine{static const wchar_t* Get(){return TEXT("");}};
struct FParse{static bool Param(const wchar_t*,const wchar_t* Name){return HostFlag&&std::wstring(Name)==L"DungeonFairytalePrimary1Bridge258Preview";}static bool Value(const wchar_t*,const wchar_t* Name,FString& Out){if(std::wstring(Name)!=L"DungeonHeroLandingPriorityAction=")return false;Out=HostAction;return true;}};
struct FDungeonFairytaleSwordDraw{
 bool Active=true,Supported=true,ActionPoseSupported=true,TextureReady=true,ArmorDrawn=true,GearPlaceholder=false;
 int32 Frame=0,Facing=1;FString Clip,WeaponPath;TArray<FString> DrawStack;FVector2D Root,Grip;double WeaponScale=.5,WeaponAngle=0.;
};
inline bool SwordDrawn(const FDungeonFairytaleSwordDraw& D){return !D.WeaponPath.IsEmpty()&&D.DrawStack.Contains(D.WeaponPath);}
