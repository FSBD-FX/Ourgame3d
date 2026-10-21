bool WriteNewBytes(const FString& Path,const uint8* Bytes,uint64 Length)
{
#if PLATFORM_WINDOWS
 if(Length>MAX_uint32)return false;
 HANDLE File=::CreateFileW(*Path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(File==INVALID_HANDLE_VALUE)return false;
 DWORD Written=0;const bool Ok=::WriteFile(File,Bytes,DWORD(Length),&Written,nullptr)!=0&&Written==Length&&::FlushFileBuffers(File)!=0;
 ::CloseHandle(File);return Ok; // Failed partial bytes are preserved, never replaced.
#else
 return false;
#endif
}
bool WriteNewUTF8(const FString& Path,const FString& Text)
{
#if PLATFORM_WINDOWS
 const FTCHARToUTF8 UTF8(*Text,Text.Len());
 HANDLE File=::CreateFileW(*Path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(File==INVALID_HANDLE_VALUE)return false;
 DWORD Written=0;const DWORD Length=DWORD(UTF8.Length());
 const bool Ok=::WriteFile(File,UTF8.Get(),Length,&Written,nullptr)!=0&&Written==Length&&::FlushFileBuffers(File)!=0;
 ::CloseHandle(File);return Ok; // Failed partial bytes remain owned evidence; never overwrite/retry.
#else
 return false; // This isolated native proof contract is Windows-only.
#endif
}
