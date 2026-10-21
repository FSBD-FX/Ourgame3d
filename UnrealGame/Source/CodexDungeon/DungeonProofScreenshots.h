#pragma once

// Optional isolated QA process only. Source viewport pixels remain unchanged.
void InstallFastLosslessProofScreenshots();

// Call on the game thread after movie/audio capture stops and before reporting.
// Seals the opt-in async queue and waits for real PNG/receipt completion.
// Normal synchronous installations have no queue and return true.
bool FlushFastLosslessProofScreenshots();
