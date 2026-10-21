# Solid TAR.XZ exact-byte native retention candidate

Root owns actual E execution. This tool does not replace the existing ZIP tools or pipeline. Old Source Art E599/E600 ZIP formats and their checkers remain untouched.

Full native leaf (Root only, future NEW batch):

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 `
 'F:/Ourgame/source-assets/production/fairytale-hero-air-v001/native-retention-solid-candidate-v001/retain-native-media-lossless-solid-tar-xz-v001.py' `
 --source 'F:/Ourgame/过程图稿与视频/<closed native leaf>' --batch '2026-10-19_<topic>_solid_v001' --preset 3
```

Default destination is E:/OurGame/Knight/过程图稿与视频. Source must be one direct F native-media leaf; every regular file and its original relative name is included, covering 原件 and 展示副本 and metadata. Production mode has no member filtering. Existing batches refuse before writes; partial failures remain. Source files are never deleted, rewritten or reencoded. E root README must exist and remain byte-identical.

Readonly independent verification, with ALL source files and TAR file members streamed twice:

```
python -B -X utf8 retain-native-media-lossless-solid-tar-xz-v001.py --verify-index <new batch>/E-retention-index-v001.json
```

No archive extraction is performed. Python tarfile and lzma use one solid TAR/XZ stream with CRC64. Hashing reads at most1MiB per application read; tar members stream from each source handle. LZMA retains its bounded codec dictionary/workspace, never a whole829MiB clip. TAR container timestamps are zero; exact source file bytes and relative names are preserved. This is not an NTFS ACL/alternate-stream backup.

Safe local real-frame sample (2–14 original PNGs, output only this candidate/sample-storage):

```
python -B -X utf8 retain-native-media-lossless-solid-tar-xz-v001.py --source <existing F leaf> --batch 2026-10-19_<sample>_v001 --sample-frames 8 --preset 3
```

Actual measured first8 PNGs from already E608-retained left_v003:29,544,824 bytes. Same8 independent DEFLATE1 ZIP:8,647,330 bytes, pack0.422s. Solid preset6:766,688 bytes (8.87% of ZIP), pack14.434s / total14.864s including two source+archive passes. Preset3:926,336 bytes (10.71% of ZIP), pack0.641s / total1.094s. Both samples have two original member size/SHA passes, zero differences. Final source independently reverified both samples twice. Full-clip compression ratio/runtime is NOT inferred from this8-frame sample.

Preset3 is a reasonable Root-selected speed/size option from this sample; default stays6. Solid access is sequential: retrieving a late member requires decoding its preceding stream, and corruption can affect later members. Original F files remain available. Preserve new batch/index/packet and verify before any View; retention is neither publication nor visual/audio/final acceptance.

11/11 lightweight synthetic host cases pass: Unicode originals+presentation, bad paths, duplicate/extra/missing members, changed source size/hash/membership, existing target, corrupted XZ, links/wrong member bytes, root README drift, omitted-full index and false subset/full scope. Failed fixtures remain under validation-runs. Tests never modify actual source media/E. The small historical sample tool is preserved; final code adds only a fail-closed full/subset argument guard (precise AST delta recorded), without changing any compression/stream verification code.

No UE, external API, dependencies installed, source deletion, whole clip copy, image/video/audio decode or View occurred. Actual E retention is still a future Root action.
