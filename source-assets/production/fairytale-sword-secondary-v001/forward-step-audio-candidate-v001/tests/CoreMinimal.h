#pragma once
#include <cstdint>
#include <string>
#include <vector>
using uint64=std::uint64_t;using uint32=std::uint32_t;
using FString=std::string;struct FGuid{};
template<class T>using TArray=std::vector<T>;
struct FVector2D { double X=0,Y=0;FVector2D()=default;FVector2D(double A,double B):X(A),Y(B){}; };
