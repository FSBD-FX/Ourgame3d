  if(Bridge258ObservationEnabled()&&Action==TEXT("J"))
  {
   for(const auto& Pin:Bridge258SourcePins)
   {if(!Capture(Pin.ObjectPath,Pin.SourceSHA256,TEXT(""),Pin.Frame,-1))return false;++ExpectedReadbacks;}
  }
