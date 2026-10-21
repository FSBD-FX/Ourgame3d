JO Bridge258LegacyResidencyStatus(const FString& RequestedPath,const UTexture2D* Texture)
{
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("requested_path"),RequestedPath);
 O->SetNumberField(TEXT("observed_monotonic_s"),FPlatformTime::Seconds());
 O->SetBoolField(TEXT("object_present"),Texture!=nullptr);
 if(!Texture)
 {
  for(const TCHAR* Key:{TEXT("actual_path"),TEXT("class"),TEXT("width"),TEXT("height"),TEXT("object_flags"),TEXT("is_compiling"),TEXT("async_cache_complete"),TEXT("pending_initialization"),TEXT("resource_initialized"),TEXT("resource_is_proxy")})O->SetField(Key,MakeShared<FJsonValueNull>());
  O->SetBoolField(TEXT("resource_present"),false);O->SetBoolField(TEXT("editor_status_available"),false);return O;
 }
 O->SetStringField(TEXT("actual_path"),Texture->GetPathName());O->SetStringField(TEXT("class"),Texture->GetClass()->GetName());
 O->SetNumberField(TEXT("width"),Texture->GetSizeX());O->SetNumberField(TEXT("height"),Texture->GetSizeY());Id(O,TEXT("object_flags"),uint64(Texture->GetFlags()));
 O->SetBoolField(TEXT("pending_initialization"),Texture->HasPendingRenderResourceInitialization());
 const FTextureResource* Resource=Texture->GetResource();O->SetBoolField(TEXT("resource_present"),Resource!=nullptr);
 if(Resource){O->SetBoolField(TEXT("resource_initialized"),Resource->IsInitialized());O->SetBoolField(TEXT("resource_is_proxy"),Resource->IsProxy());}
 else{O->SetField(TEXT("resource_initialized"),MakeShared<FJsonValueNull>());O->SetField(TEXT("resource_is_proxy"),MakeShared<FJsonValueNull>());}
#if WITH_EDITOR
 O->SetBoolField(TEXT("editor_status_available"),true);O->SetBoolField(TEXT("is_compiling"),Texture->IsCompiling());O->SetBoolField(TEXT("async_cache_complete"),Texture->IsAsyncCacheComplete());
#else
 O->SetBoolField(TEXT("editor_status_available"),false);O->SetField(TEXT("is_compiling"),MakeShared<FJsonValueNull>());O->SetField(TEXT("async_cache_complete"),MakeShared<FJsonValueNull>());
#endif
 return O;
}

