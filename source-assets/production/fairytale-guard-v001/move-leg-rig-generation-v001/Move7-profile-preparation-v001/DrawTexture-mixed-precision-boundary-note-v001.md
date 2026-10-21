`DrawTexture_float32_trace` records the actual mixed-precision API boundary; its name does not mean every field is float32.

- Top and Size coordinates, RotationDegrees, UV and UVSize enter the DrawTexture float parameters. Top/Size/Rotation are explicitly cast to float32 by this host; UV values are exactly representable0/1/-1 and remain exact through that cast.
- RotationPivotUV is an FVector2D(double) value. It stays double and must not be cast to float32 merely because it is inside this trace object. DrawScale1 is exact; ScalePosition is boolfalse.
- `source_to_screen_affine_float32` is a separate six-coefficient float oracle. It is not a claim that Unreal internally draws from that matrix or that its reconstructed corners are bit-identical to the mixed-precision DrawTexture path. Native validation must compare the actual submitted API values with the corresponding host fields.

The double full affine and positive-size DrawTexture representation are mathematically equivalent before API rounding. For left facing, use one complete representation: affine-reflected vertices with ordinaryUV OR positive rectangle/negated angle/mirroredUV/mirrored pivot. Applying both gives an erroneous second mirror. The source-pivot double fraction and its mirrored1-x fraction must follow the same representation.

Current final host verification is `host-reference-verification-v002.json` (266 checks), which adds rejection when a positive finite viewport scale underflows the float backend. It changes no profile, source, author point, rig parameter, nominal display scale or phase formula. The earlier265-check report remains historical and pins its earlier solver version.
