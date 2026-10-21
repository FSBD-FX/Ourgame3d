  R->SetBoolField(TEXT("request258_primary1_bridge_optin"),Bridge258ObservationEnabled());
  R->SetStringField(TEXT("request258_primary1_bridge_source_contract_sha256"),TEXT("f85284dc25d0a5f0be5bf09aa7b9f7dbdf2a62bccbb61e4ca0c5ce0ef1238f6e"));
  TArray<JV> Bridge258Pins;
  if(Bridge258ObservationEnabled())for(const auto& Pin:Bridge258SourcePins)
  {auto S=MakeShared<FJsonObject>();S->SetNumberField(TEXT("frame"),Pin.Frame);S->SetStringField(TEXT("component"),Pin.Component);S->SetStringField(TEXT("object_path"),Pin.ObjectPath);S->SetStringField(TEXT("source_png"),Pin.SourcePNG);Id(S,TEXT("source_png_bytes"),Pin.SourceBytes);S->SetStringField(TEXT("source_png_sha256"),Pin.SourceSHA256);Bridge258Pins.Add(MakeShared<FJsonValueObject>(S));}
  R->SetArrayField(TEXT("request258_primary1_bridge_source_pins"),Bridge258Pins);
