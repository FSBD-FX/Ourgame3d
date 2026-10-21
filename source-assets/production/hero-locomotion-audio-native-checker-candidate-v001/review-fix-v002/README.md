# Scoped input gate fix v002

Only one function and one native-session call are added to the byte-for-byte
previous checker: the fixed Shift_right normal input sequence must have exactly
12 edges, in original order, and each `down` must be an actual bool.
Enter down/up, D down/up twice, E down/up, SpaceBar down/up, LeftShift down/up.
All prior time, context, state, native-source, audio and optical gates remain.

The original frozen checker/config/tests are preserved. The dependency table
is copied byte-identically into this child, so HERE-based resolution and the
native checker/config self-membership checks bind this new freeze correctly.

Added tests use the pinned historical successful Shift_right runtime JSON only
as evidence for the real 12-edge schema. It is not current locomotion audio
native evidence. Eight failures with no errors were observed before adding the
gate; nine tests then passed. The unchanged original 13 test bodies also run
against the new checker module, and actual current CM/AD preflight is recorded.

No UE launch, game Source/Content/tools change, generated audio or media View.
Root must independently review this scoped fix before actual native capture.
