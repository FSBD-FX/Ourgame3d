#include "DungeonProofScreenshots.h"
#include "CoreMinimal.h"
#include "Engine/GameViewportClient.h"
#include "Containers/Queue.h"
#include "HAL/Event.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "HAL/Runnable.h"
#include "HAL/RunnableThread.h"
#include "ImageUtils.h"
#include "IImageWrapper.h"
#include "IImageWrapperModule.h"
#include "Misc/CommandLine.h"
#include "Misc/CoreDelegates.h"
#include "Misc/Crc.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/ScopeLock.h"
#include "Modules/ModuleManager.h"
#include "UnrealClient.h"
#if PLATFORM_WINDOWS
#include "Windows/WindowsHWrapper.h"
#endif

namespace
{
FString ProofScreenshotDirectory;
bool AsyncInstallationFailed=false;
FDelegateHandle AsyncScreenshotHandle;

struct FNativeProofPixelJob
{
    FString Filename,ReceiptFilename;
    int32 Width=0,Height=0;
    TArray<FColor> Pixels;
    uint32 SourceCRC=0;
    uint64 Sequence=0;
    double CaptureCallbackAt=0,ReservedAt=0,EnqueuedAt=0;
    bool FilenameReserved=false;
};

bool ReserveNativeMovieFilename(FNativeProofPixelJob& Job)
{
#if PLATFORM_WINDOWS
    // UE5.5's generic writer ignores FILEWRITE_NoReplaceExisting and opens with
    // CREATE_ALWAYS. Reserve the exact engine-selected name atomically instead.
    const HANDLE Handle=::CreateFileW(*Job.Filename,GENERIC_WRITE,FILE_SHARE_READ,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(Handle==INVALID_HANDLE_VALUE)
    {
        const uint32 Error=::GetLastError();
        UE_LOG(LogTemp,Error,TEXT("Async proof filename reservation failed without replacement: %s (Windows %u)"),*Job.Filename,Error);return false;
    }
    if(!::CloseHandle(Handle))
    {
        const uint32 Error=::GetLastError();
        UE_LOG(LogTemp,Error,TEXT("Async proof filename reservation close failed: %s (Windows %u)"),*Job.Filename,Error);return false;
    }
    Job.FilenameReserved=true;Job.ReservedAt=FPlatformTime::Seconds();return true;
#else
    UE_LOG(LogTemp,Error,TEXT("Async proof exclusive filename reservation is unsupported on this platform."));return false;
#endif
}

// A single serial writer owns all movie PNG and receipt I/O. Its data contains
// no UObject, viewport/request pointer or simulation/audio callback.
class FProofScreenshotWriter final:public FRunnable
{
public:
    explicit FProofScreenshotWriter(const FString& InDirectory):Directory(InDirectory)
    {
        Wake=FPlatformProcess::GetSynchEventFromPool(false);
        Idle=FPlatformProcess::GetSynchEventFromPool(true);
        if(Wake&&Idle)
        {
            Idle->Trigger();
            Thread=FRunnableThread::Create(this,TEXT("DungeonProofPNGWriter"),0,TPri_BelowNormal);
        }
    }
    ~FProofScreenshotWriter()
    {
        if(Thread)
        {
            {FScopeLock Lock(&Mutex);Accepting=false;Stopping=true;}
            Wake->Trigger();Thread->WaitForCompletion();delete Thread;
        }
        if(Idle)FPlatformProcess::ReturnSynchEventToPool(Idle);
        if(Wake)FPlatformProcess::ReturnSynchEventToPool(Wake);
    }
    bool IsReady() const{return Thread!=nullptr;}
    bool Enqueue(FNativeProofPixelJob&& Job)
    {
        {
            FScopeLock Lock(&Mutex);
            if(!Accepting||!Thread||!Job.FilenameReserved){AllSucceeded=false;++Rejected;return false;}
            Job.Sequence=Submitted+1;Job.EnqueuedAt=FPlatformTime::Seconds();
            const double CaptureAt=Job.CaptureCallbackAt;
            const uint64 PixelBytes=uint64(Job.Pixels.Num())*sizeof(FColor);
            if(!Jobs.Enqueue(MoveTemp(Job))){AllSucceeded=false;++Rejected;return false;}
            ++Submitted;if(Submitted==1)FirstCaptureAt=CaptureAt;
            LastCaptureAt=CaptureAt;
            ++Pending;PendingBytes+=PixelBytes;
            PeakPending=FMath::Max(PeakPending,Pending);PeakPendingBytes=FMath::Max(PeakPendingBytes,PendingBytes);
            Idle->Reset();
        }
        Wake->Trigger();return true;
    }
    void ReservationSucceeded()
    {FScopeLock Lock(&Mutex);++Reserved;}
    void CaptureFailed(bool ReservationFailure=false)
    {FScopeLock Lock(&Mutex);AllSucceeded=false;++Rejected;if(ReservationFailure)++ReservationFailures;}
    bool Flush()
    {
        {
            FScopeLock Lock(&Mutex);
            if(Flushed)return FlushSucceeded&&AllSucceeded;
            Accepting=false;
        }
        Wake->Trigger();Idle->Wait();
        FString Summary;bool WritesSucceeded=false;
        {
            FScopeLock Lock(&Mutex);
            WritesSucceeded=AllSucceeded&&Pending==0&&Submitted==Reserved&&Submitted==Completed&&Submitted==Saved&&Submitted==ReceiptsSaved&&Rejected==0;
            Summary=FString::Printf(TEXT("{\"requested\":true,\"active\":true,\"closed\":true,\"flushed\":true,\"success\":%s,\"movie_reserved\":%llu,\"movie_reservation_failed\":%llu,\"movie_enqueued\":%llu,\"movie_saved\":%llu,\"movie_failed\":%llu,\"movie_completed\":%llu,\"receipts_saved\":%llu,\"rejected\":%llu,\"pending\":%llu,\"peak_pending_jobs\":%llu,\"peak_queue_bytes\":%llu,\"peak_queue_bytes_scope\":\"pending_or_in_progress_BGRA8_copies_only_not_total_process_memory\",\"first_capture_callback_monotonic_s\":%.9f,\"last_capture_callback_monotonic_s\":%.9f,\"last_save_completed_monotonic_s\":%.9f,\"flush_completed_monotonic_s\":%.9f}\n"),
                WritesSucceeded?TEXT("true"):TEXT("false"),Reserved,ReservationFailures,Submitted,Saved,FailedJobs+Rejected,Completed,ReceiptsSaved,Rejected,Pending,PeakPending,PeakPendingBytes,
                FirstCaptureAt,LastCaptureAt,LastSaveCompletedAt,FPlatformTime::Seconds());
        }
        const bool SummarySaved=FFileHelper::SaveStringToFile(Summary,*(Directory/TEXT("native-async-write-summary.json")),
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
        {
            FScopeLock Lock(&Mutex);Flushed=true;FlushSucceeded=WritesSucceeded&&SummarySaved;
        }
        if(!WritesSucceeded||!SummarySaved)UE_LOG(LogTemp,Error,TEXT("Async proof PNG/receipt flush failed: %s"),*Directory);
        return WritesSucceeded&&SummarySaved;
    }
    virtual uint32 Run() override
    {
        for(;;)
        {
            FNativeProofPixelJob Job;bool HasJob=false,Exit=false;
            {
                FScopeLock Lock(&Mutex);HasJob=Jobs.Dequeue(Job);Exit=Stopping&&!HasJob;
            }
            if(HasJob)
            {
                const double SaveStartedAt=FPlatformTime::Seconds();
                const uint32 CopyCRC=FCrc::MemCrc32(Job.Pixels.GetData(),Job.Pixels.Num()*sizeof(FColor));
                const bool CopyMatches=CopyCRC==Job.SourceCRC;
                const bool ImageSaved=Job.FilenameReserved&&CopyMatches&&FImageUtils::SaveImageByExtension(*Job.Filename,
                    FImageView(Job.Pixels.GetData(),Job.Width,Job.Height),int32(EImageCompressionQuality::Uncompressed));
                const double SaveCompletedAt=FPlatformTime::Seconds();
                const FString Row=FString::Printf(TEXT("{\"file\":\"%s\",\"width\":%d,\"height\":%d,\"native_BGRA8_crc32\":%u,\"saved\":%s,\"save_wall_s\":%.9f,\"async_writer\":true,\"writer_sequence\":%llu,\"filename_reserved\":%s,\"filename_reservation_mode\":\"Windows_CreateFileW_CREATE_NEW\",\"copied_BGRA8_crc32\":%u,\"copy_crc_matches\":%s,\"capture_callback_monotonic_s\":%.9f,\"reservation_completed_monotonic_s\":%.9f,\"enqueued_monotonic_s\":%.9f,\"save_started_monotonic_s\":%.9f,\"save_completed_monotonic_s\":%.9f}\n"),
                    *FPaths::GetCleanFilename(Job.Filename),Job.Width,Job.Height,Job.SourceCRC,ImageSaved?TEXT("true"):TEXT("false"),
                    SaveCompletedAt-SaveStartedAt,Job.Sequence,Job.FilenameReserved?TEXT("true"):TEXT("false"),CopyCRC,CopyMatches?TEXT("true"):TEXT("false"),Job.CaptureCallbackAt,
                    Job.ReservedAt,Job.EnqueuedAt,SaveStartedAt,SaveCompletedAt);
                const bool ReceiptSaved=FFileHelper::SaveStringToFile(Row,*Job.ReceiptFilename,
                    FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
                {
                    FScopeLock Lock(&Mutex);++Completed;if(ImageSaved)++Saved;if(ReceiptSaved)++ReceiptsSaved;
                    if(!ImageSaved||!ReceiptSaved)++FailedJobs;
                    AllSucceeded&=ImageSaved&&ReceiptSaved;LastSaveCompletedAt=SaveCompletedAt;
                    PendingBytes-=uint64(Job.Pixels.Num())*sizeof(FColor);if(--Pending==0)Idle->Trigger();
                }
                if(!ImageSaved||!ReceiptSaved)UE_LOG(LogTemp,Error,TEXT("Async native proof PNG/receipt failed: %s"),*Job.Filename);
                continue;
            }
            if(Exit)return 0;
            Wake->Wait();
        }
    }
private:
    const FString Directory;
    FCriticalSection Mutex;
    TQueue<FNativeProofPixelJob> Jobs;
    FEvent* Wake=nullptr;FEvent* Idle=nullptr;FRunnableThread* Thread=nullptr;
    bool Accepting=true,Stopping=false,AllSucceeded=true,Flushed=false,FlushSucceeded=false;
    uint64 Submitted=0,Completed=0,Saved=0,ReceiptsSaved=0,FailedJobs=0,Rejected=0,Reserved=0,ReservationFailures=0,Pending=0,PendingBytes=0,PeakPending=0,PeakPendingBytes=0;
    double FirstCaptureAt=0,LastCaptureAt=0,LastSaveCompletedAt=0;
};
TUniquePtr<FProofScreenshotWriter> AsyncProofWriter;

void SaveNativeProofPixels(int32 Width,int32 Height,const TArray<FColor>& Bitmap)
{
    // The engine's normal ProcessScreenshotData creates movie filenames here;
    // its delegate branch bypasses that function. Keep its exact request path.
    if(GIsDumpingMovie && FScreenshotRequest::GetFilename().IsEmpty())
        FScreenshotRequest::RequestScreenshot(FString(),false,true,false);
    FString Filename=FPaths::ConvertRelativePathToFull(FScreenshotRequest::GetFilename());
    FPaths::NormalizeFilename(Filename);
    if(FPaths::GetExtension(Filename).IsEmpty()) Filename+=TEXT(".png");
    if(!Filename.StartsWith(ProofScreenshotDirectory+TEXT("/"),ESearchCase::IgnoreCase)
        ||FPaths::GetExtension(Filename)!=TEXT("png") ||Width<=0||Height<=0
        ||int64(Width)*Height!=Bitmap.Num())
    {
        UE_LOG(LogTemp,Error,TEXT("Native proof screenshot outside expected PNG/size contract: %s"),*Filename);
        return;
    }
    const double Begin=FPlatformTime::Seconds();
    const uint32 RawCRC=FCrc::MemCrc32(Bitmap.GetData(),Bitmap.Num()*sizeof(FColor));
    // UE itself supplies this BGRA8 viewport buffer with alpha255. The exact same
    // FImageView is saved synchronously, changing PNG compression alone. No crop,
    // repaint, frame substitution, resize, simulation pacing or audio operation.
    const bool Saved=FImageUtils::SaveImageByExtension(*Filename,FImageView(Bitmap.GetData(),Width,Height),
        int32(EImageCompressionQuality::Uncompressed));
    const FString Row=FString::Printf(TEXT("{\"file\":\"%s\",\"width\":%d,\"height\":%d,\"native_BGRA8_crc32\":%u,\"saved\":%s,\"save_wall_s\":%.9f}\n"),
        *FPaths::GetCleanFilename(Filename),Width,Height,RawCRC,Saved?TEXT("true"):TEXT("false"),FPlatformTime::Seconds()-Begin);
    const bool Recorded=FFileHelper::SaveStringToFile(Row,*(ProofScreenshotDirectory/TEXT("native-frame-pixels.jsonl")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
    if(!Saved||!Recorded) UE_LOG(LogTemp,Error,TEXT("Native proof PNG/receipt write failed: %s"),*Filename);
}

void SaveNativeAsyncProofPixels(int32 Width,int32 Height,const TArray<FColor>& Bitmap)
{
    const double CaptureAt=FPlatformTime::Seconds();
    // Prewarm completion must still mean the PNG and receipt really exist before
    // the engine processed callback opens movie/audio capture.
    if(!GIsDumpingMovie){SaveNativeProofPixels(Width,Height,Bitmap);return;}
    if(FScreenshotRequest::GetFilename().IsEmpty())FScreenshotRequest::RequestScreenshot(FString(),false,true,false);
    FString Filename=FPaths::ConvertRelativePathToFull(FScreenshotRequest::GetFilename());FPaths::NormalizeFilename(Filename);
    if(FPaths::GetExtension(Filename).IsEmpty())Filename+=TEXT(".png");
    if(!FPaths::GetCleanFilename(Filename).StartsWith(TEXT("MovieFrame"),ESearchCase::CaseSensitive))
    {SaveNativeProofPixels(Width,Height,Bitmap);return;}
    if(!Filename.StartsWith(ProofScreenshotDirectory+TEXT("/"),ESearchCase::IgnoreCase)
        ||FPaths::GetExtension(Filename)!=TEXT("png")||Width<=0||Height<=0||int64(Width)*Height!=Bitmap.Num()||!AsyncProofWriter)
    {
        if(AsyncProofWriter)AsyncProofWriter->CaptureFailed();
        UE_LOG(LogTemp,Error,TEXT("Async native proof screenshot violates PNG/size/writer contract: %s"),*Filename);return;
    }
    FNativeProofPixelJob Job;Job.Filename=MoveTemp(Filename);Job.ReceiptFilename=ProofScreenshotDirectory/TEXT("native-frame-pixels.jsonl");
    Job.Width=Width;Job.Height=Height;Job.CaptureCallbackAt=CaptureAt;
    if(!ReserveNativeMovieFilename(Job)){AsyncProofWriter->CaptureFailed(true);return;}
    AsyncProofWriter->ReservationSucceeded();
    Job.SourceCRC=FCrc::MemCrc32(Bitmap.GetData(),Bitmap.Num()*sizeof(FColor));
    Job.Pixels=Bitmap; // Deep immutable BGRA8 copy; the engine may release its buffer after return.
    if(!AsyncProofWriter->Enqueue(MoveTemp(Job)))UE_LOG(LogTemp,Error,TEXT("Async native proof rejected movie frame after queue seal."));
}

void ShutdownAsyncProofWriter()
{
    if(AsyncScreenshotHandle.IsValid())
    {UGameViewportClient::OnScreenshotCaptured().Remove(AsyncScreenshotHandle);AsyncScreenshotHandle.Reset();}
    if(AsyncProofWriter){AsyncProofWriter->Flush();AsyncProofWriter.Reset();}
}
}

void InstallFastLosslessProofScreenshots()
{
    static bool Installed=false;
    if(Installed ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonContentProof"))
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFastLosslessCapture"))) return;
    FString Directory;
    if(!FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Directory)) return;
    ProofScreenshotDirectory=FPaths::ConvertRelativePathToFull(Directory);
    FPaths::NormalizeDirectoryName(ProofScreenshotDirectory);
    const auto DelegateCVar=IConsoleManager::Get().FindConsoleVariable(TEXT("r.ScreenshotDelegate"));
    if(!DelegateCVar||DelegateCVar->GetInt()!=1)
    {
        UE_LOG(LogTemp,Error,TEXT("Fast lossless proof requires existing r.ScreenshotDelegate=1"));
        return;
    }
    const bool AsyncRequested=FParse::Param(FCommandLine::Get(),TEXT("DungeonAsyncLosslessCapture"));
    if(AsyncRequested)
    {
#if !PLATFORM_WINDOWS
        AsyncInstallationFailed=true;
        UE_LOG(LogTemp,Error,TEXT("Async native proof requires Windows exclusive CREATE_NEW filename reservation."));return;
#endif
        // UE ImageUtils explicitly requires this load on the game thread before
        // its worker-thread GetModulePtr path can compress an image.
        FModuleManager::LoadModuleChecked<IImageWrapperModule>(TEXT("ImageWrapper"));
        AsyncProofWriter=MakeUnique<FProofScreenshotWriter>(ProofScreenshotDirectory);
        if(!AsyncProofWriter->IsReady())
        {
            AsyncInstallationFailed=true;AsyncProofWriter.Reset();
            UE_LOG(LogTemp,Error,TEXT("Async native proof PNG writer thread could not start."));return;
        }
    }
    const FString Metadata=AsyncRequested
        ?TEXT("{\"mode\":\"native_viewport_BGRA8_lossless_PNG_zlib0\",\"async_movie_writer_requested\":true,\"async_movie_writer_active\":true,\"async_writer\":true,\"writer\":\"single_serial_FIFO_FRunnable\",\"movie_pixels\":\"immutable_full_native_BGRA8_copy\",\"movie_filename_reservation\":\"Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue\",\"prewarm_synchronous\":true,\"saved_means\":\"actual_SaveImageByExtension_result_not_enqueue\",\"flush_required_after_audio_capture_stop\":true,\"queue_drop_policy\":\"no_drop_no_replacement\",\"pixel_mutations\":false,\"simulation_pacing_changed\":false,\"audio_changed\":false,\"scope\":\"opt-in isolated QA process; engine screenshot callback; default engine processed callback and all audio capture functions retained\"}\n")
        :TEXT("{\"mode\":\"native_viewport_BGRA8_lossless_PNG_zlib0\",\"pixel_mutations\":false,\"simulation_pacing_changed\":false,\"audio_changed\":false,\"scope\":\"opt-in isolated QA process; engine screenshot callback; default engine processed callback and all audio capture functions retained\"}\n");
    if(!FFileHelper::SaveStringToFile(Metadata,*(ProofScreenshotDirectory/TEXT("native-lossless-capture.json")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM))
    {
        if(AsyncRequested){AsyncInstallationFailed=true;ShutdownAsyncProofWriter();}return;
    }
    if(AsyncRequested)
    {
        AsyncScreenshotHandle=UGameViewportClient::OnScreenshotCaptured().AddStatic(&SaveNativeAsyncProofPixels);
        FCoreDelegates::OnEnginePreExit.AddStatic(&ShutdownAsyncProofWriter);
    }
    else UGameViewportClient::OnScreenshotCaptured().AddStatic(&SaveNativeProofPixels);
    Installed=true;
}

bool FlushFastLosslessProofScreenshots()
{
    if(!IsInGameThread())
    {UE_LOG(LogTemp,Error,TEXT("Proof PNG flush must follow capture stop on the game thread."));return false;}
    if(AsyncInstallationFailed)return false;
    return !AsyncProofWriter||AsyncProofWriter->Flush();
}
