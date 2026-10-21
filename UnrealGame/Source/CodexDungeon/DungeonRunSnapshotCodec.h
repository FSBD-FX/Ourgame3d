#pragma once
#include "DungeonRunAggregate.h"

// Pure canonical UTF-8 transport for the implemented BoundDevelopmentV1 owner
// graph only. No actor construction, clock/RNG step, input, audio, file IO or
// new-process Continue is performed here. A failure preserves Out exactly.
//
// Versioned object: {"codec":"bound-run-v1","snapshot":{...}}. Every struct
// field is named and mandatory; unknown/duplicate fields are rejected. Object
// keys are ordinal sorted, arrays retain their original order, maps use numeric
// key order. Integer/enum/count values are canonical decimal strings. IEEE754
// float/double values are fixed-width lowercase hexadecimal bit strings (8/16
// digits). Optional owners are explicit null or the complete owning object.
// Native transforms retain translation/scale/quaternion values, never Euler
// conversion or normalization. Encoding uses no BOM, whitespace or trailing LF.
// Object field names retain C++ member spelling below the two envelope keys.
// Strings use literal UTF-8 for valid Unicode, escaped quote/backslash and
// lowercase \u00xx for every ASCII control, including embedded NUL. Signed
// integers also use decimal strings. No JSON numeric token represents a value.
// Implementation ceilings: 64 MiB payload and aggregate typed storage, depth
// 128, 1,048,576 values/elements/string units, 256 fields/name characters. This
// version covers implemented bound-development owners, not full D13 account,
// settings/journal storage, disk publication or a fresh-process Continue.
namespace DungeonRunSnapshotCodec
{
CODEXDUNGEON_API bool Encode(const FDungeonRunSnapshot& Saved,TArray<uint8>& Out,FString& Diagnostic);
CODEXDUNGEON_API bool Decode(const TArray<uint8>& Payload,FDungeonValidatedRun& Out,FString& Diagnostic);
}
