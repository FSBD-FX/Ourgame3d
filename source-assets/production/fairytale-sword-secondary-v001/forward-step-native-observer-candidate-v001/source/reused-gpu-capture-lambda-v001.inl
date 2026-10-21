const auto Capture=[&](const FString& Path,const FString& PNGSHA,const FString& RGBASHA,int32 Frame,int32 Component)
  {
   UTexture2D* T=FindObject<UTexture2D>(nullptr,*Path);
   if(!Need(!Unique.Contains(Path)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512&&T->GetResource()&&!T->HasPendingRenderResourceInitialization(),TEXT("All requested exact preloaded Texture2D512 resources required before normal input")))return false;
   Unique.Add(Path);const FTextureRHIRef RHI=T->GetResource()->TextureRHI;
   if(!Need(RHI.IsValid()&&RHI->GetDesc().Extent==FIntPoint(512,512)&&(RHI->GetFormat()==PF_B8G8R8A8||RHI->GetFormat()==PF_R8G8B8A8),TEXT("GPU readback requires actual uncompressed BGRA8/RGBA8 mip0 512; no lossy fallback")))return false;
   TArray<FColor> GPU;const double ReadStart=FPlatformTime::Seconds();
   ENQUEUE_RENDER_COMMAND(SwdForwardStepOriginalGPUReadback)([RHI,&GPU](FRHICommandListImmediate& Cmd)
   {FReadSurfaceDataFlags Flags(RCM_UNorm);Flags.SetLinearToGamma(false);Flags.SetMip(0);Cmd.ReadSurfaceData(RHI,FIntRect(0,0,512,512),GPU,Flags);});
   FlushRenderingCommands();const double ReadStop=FPlatformTime::Seconds();
   static_assert(sizeof(FColor)==4,"Native original GPU proof requires packed BGRA8 FColor");
   const int32 ByteCount=512*512*4;
   if(!Need(GPU.Num()==512*512,TEXT("Actual original GPU mip0 readback is incomplete")))return false;
   const FString Stem=FString::Printf(TEXT("texture-readback/%03d"),StartupTextures.Num());const FString GPUFile=Stem+TEXT(".gpu-bgra8.bin");
   if(!Need(WriteNewBytes(Directory/GPUFile,reinterpret_cast<const uint8*>(GPU.GetData()),uint64(GPU.Num())*sizeof(FColor)),TEXT("GPU original bytes could not be preserved exclusively")))return false;
   auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("texture"),Path);O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetNumberField(TEXT("frame"),Frame);O->SetNumberField(TEXT("component"),Component);O->SetStringField(TEXT("source_SHA_metadata"),PNGSHA);O->SetStringField(TEXT("source_RGBA_SHA_metadata"),RGBASHA);O->SetBoolField(TEXT("resource_ready"),true);O->SetBoolField(TEXT("pending_initialization"),false);O->SetBoolField(TEXT("sRGB"),T->SRGB);O->SetNumberField(TEXT("RHI_format"),int32(RHI->GetFormat()));O->SetStringField(TEXT("GPU_file"),GPUFile);O->SetNumberField(TEXT("GPU_BGRA8_CRC32"),FCrc::MemCrc32(GPU.GetData(),ByteCount));O->SetStringField(TEXT("read_flags"),TEXT("RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy"));O->SetNumberField(TEXT("read_start_monotonic_s"),ReadStart);O->SetNumberField(TEXT("read_stop_monotonic_s"),ReadStop);
#if WITH_EDITOR && WITH_EDITORONLY_DATA
   TArray64<uint8> Mip;
   if(!Need(T->Source.IsValid()&&T->Source.GetSizeX()==512&&T->Source.GetSizeY()==512&&T->Source.GetFormat()==TSF_BGRA8&&T->Source.GetMipData(Mip,0)&&Mip.Num()==512*512*4,TEXT("Actual imported editor source mip0 BGRA8 unavailable; no metadata substitute")))return false;
   const FString SourceFile=Stem+TEXT(".editor-source-bgra8.bin");if(!Need(WriteNewBytes(Directory/SourceFile,Mip.GetData(),uint64(Mip.Num())),TEXT("Imported source mip0 original bytes could not be preserved")))return false;
   O->SetStringField(TEXT("editor_source_file"),SourceFile);O->SetStringField(TEXT("editor_source_format"),TEXT("TSF_BGRA8"));O->SetNumberField(TEXT("editor_source_BGRA8_CRC32"),FCrc::MemCrc32(Mip.GetData(),ByteCount));
#else
   return Need(false,TEXT("This isolated exact source proof requires editor source data"));
#endif
   StartupTextures.Add(MakeShared<FJsonValueObject>(O));return true;
  };
  