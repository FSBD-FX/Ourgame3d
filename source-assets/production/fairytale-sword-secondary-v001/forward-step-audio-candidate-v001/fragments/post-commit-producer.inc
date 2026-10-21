            const auto AudioAfter=Fighter->GetGroundPosition();
            const auto& AudioSkill=Fighter->GetWeaponActionsState();const auto& AudioView=GetEquipmentView();
            const bool AudioScope=Fighter==PlayerFighter&&Fighter->IsEquipmentBound()&&AudioView.Bound
                &&AudioView.RunGuid.IsValid()&&AudioView.RoomInstanceId&&AudioView.Revision
                &&ActionAudioState.RunGuid==AudioView.RunGuid&&WeaponWorld.RunGuid==AudioView.RunGuid
                &&WeaponWorld.RoomInstanceId==AudioView.RoomInstanceId&&AudioSkill.Time==SimulationTime
                &&E.AtTime>=SkillBatchFrom&&E.AtTime<=SkillBatchTo&&HeroLocomotionAudioActiveV001()
                &&Fighter->JumpHeight==0.f&&Fighter->JumpVelocity==0.f&&AudioSkill.Budget.Grounded
                &&Fighter->GetMeleeCombatState().Grounded;
            if(DungeonHeroForwardStepAudioV001::Eligible(E,AudioSkill.Action,Fighter->GetRuntimeEntityId(),
                AudioView.OwnerId,AudioScope,SimulationTime,AudioBefore,AudioAfter))
            {
                const uint64 AudioSequence=ActionAudioState.NextSequence;
                AppendActionAudio(TEXT("HERO_STEP_LIGHT_01"),E.AtTime,Fighter->GetRuntimeEntityId(),
                    E.ActionId,E.InstanceId,0,AudioView.Revision);
                if(ActionAudioState.NextSequence==AudioSequence+1&&!ActionAudioState.Records.IsEmpty()
                    &&ActionAudioState.Records.Last().Sequence==AudioSequence)
                {
                    auto& Witness=ActionAudioState.Records.Last().ForwardStep;Witness.Present=true;
                    Witness.EventId=E.EventId;Witness.SubhitId=E.SubhitId;Witness.RequestedSignedDistance=E.ForwardStep;
                    Witness.Before=AudioBefore;Witness.After=AudioAfter;Witness.CommittedDelta=AudioAfter-AudioBefore;
                }
            }
