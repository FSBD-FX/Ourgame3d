# UE5.5 installed public API evidence

All locations are under `G:/UE_5.5/Engine/Source/Runtime/`. This is static API/source evidence, not a candidate UE compilation.

| Used API | Declaration | Relevant implementation |
|---|---|---|
| `FTextureCompilingManager::FinishCompilation(TArrayView<UTexture* const>)` | `Engine/Public/TextureCompiler.h:46`, WITH_EDITOR | `Engine/Private/TextureCompiler.cpp:379–487` waits only registered requested textures, calls PostCompilation; no reentry from PostCompilation allowed |
| `UTexture::IsAsyncCacheComplete() const` | `Engine/Classes/Engine/Texture.h:1826` | reports actual async-cache completion; not FinishCachePlatformData |
| `UTexture::IsCompiling() const` | same header `:1938`, WITH_EDITOR | aliases IsDefaultTexture; `Texture2D.cpp:530–532` includes outstanding cache or proxy resource |
| `FTextureResource::IsProxy() const` | `Engine/Public/TextureResource.h:111` | virtual actual resource flag |
| `FRenderResource::IsInitialized() const` | `RenderCore/Public/RenderResource.h:161` | actual render resource initialization state |
| `UTexture::HasPendingRenderResourceInitialization() const` | `Engine/Classes/Engine/Texture.h:1976` | `Texture.cpp:1518–1521` only resource exists and is not initialized |

`Texture2D.cpp:344–348` explicitly requires FinishCompilation before requiring up-to-date platform data. `PostLoad:647–669` may begin async cache; `CreateResource:1006–1024` may create a proxy; `GetSizeX/Y:349–378` can return placeholder dimensions. `TextureCompiler.cpp:198–222` finishes cache and updates resource. `RenderCore/Private/RenderingThread.cpp:1314–1355` only flushes render/RHI work and a fence, not the texture compilation manager.

The candidate uses `#if WITH_EDITOR` for the compiler include/call and editor-only diagnostics. It never directly calls FinishCachePlatformData or UpdateResource, never changes source/asset settings, and never uses FinishAllCompilation.
