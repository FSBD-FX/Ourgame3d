#pragma once
// Standalone value and API-shape harness. No Unreal Actor, texture or GPU claims.
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>
#include <set>
#include <vector>
#include <utility>
#include <algorithm>
#define TEXT(S) S
#define CODEXDUNGEON_API
using TCHAR=char;using uint8=uint8_t;using uint32=uint32_t;using uint64=uint64_t;using int32=int32_t;
struct FString{std::string Value;FString()=default;FString(const char* V):Value(V){}FString(std::string V):Value(std::move(V)){}int32 Len()const{return int32(Value.size());}char operator[](int32 I)const{return Value[size_t(I)];}bool IsEmpty()const{return Value.empty();}void Reset(){Value.clear();}bool StartsWith(const char* Prefix)const{return Value.rfind(Prefix,0)==0;}bool operator==(const FString& B)const{return Value==B.Value;}bool operator!=(const FString& B)const{return !(*this==B);}bool operator<(const FString& B)const{return Value<B.Value;}};
struct FGuid{uint32 A=0,B=0,C=0,D=0;bool IsValid()const{return A||B||C||D;}bool operator==(const FGuid& G)const{return A==G.A&&B==G.B&&C==G.C&&D==G.D;}bool operator!=(const FGuid& G)const{return !(*this==G);}};
struct FVector2D{double X=0.,Y=0.;FVector2D()=default;FVector2D(double A,double B):X(A),Y(B){}static const FVector2D ZeroVector;FVector2D operator+(FVector2D B)const{return {X+B.X,Y+B.Y};}FVector2D operator-(FVector2D B)const{return {X-B.X,Y-B.Y};}FVector2D operator*(double S)const{return {X*S,Y*S};}bool operator==(FVector2D B)const{return X==B.X&&Y==B.Y;}bool operator!=(FVector2D B)const{return !(*this==B);}bool Equals(FVector2D B,double E=1.e-6)const{return std::abs(X-B.X)<=E&&std::abs(Y-B.Y)<=E;}};inline const FVector2D FVector2D::ZeroVector{};
struct FLinearColor{float R=0,G=0,B=0,A=0;FLinearColor()=default;FLinearColor(float r,float g,float b,float a):R(r),G(g),B(b),A(a){}static const FLinearColor White;bool operator==(FLinearColor C)const{return R==C.R&&G==C.G&&B==C.B&&A==C.A;}bool operator!=(FLinearColor C)const{return R!=C.R||G!=C.G||B!=C.B||A!=C.A;}};inline const FLinearColor FLinearColor::White{1,1,1,1};
struct FMath{template<class T>static bool IsFinite(T V){return std::isfinite(V);}static double Atan2(double Y,double X){return std::atan2(Y,X);}static double RadiansToDegrees(double R){return R*180./3.14159265358979323846;}};
template<class T>struct TNumericLimits{static constexpr T Max(){return std::numeric_limits<T>::max();}};
template<class T>struct TArray:std::vector<T>{using std::vector<T>::vector;int32 Num()const{return int32(this->size());}void Add(const T& V){this->push_back(V);}void Add(T&& V){this->push_back(std::move(V));}void Reserve(int32 N){this->reserve(size_t(N));}};
template<class T>struct TSet{std::set<T> Values;bool Contains(const T& V)const{return Values.count(V)!=0;}void Add(const T& V){Values.insert(V);}int32 Num()const{return int32(Values.size());}};
template<class T>decltype(auto) MoveTemp(T&& V){return std::move(V);}
