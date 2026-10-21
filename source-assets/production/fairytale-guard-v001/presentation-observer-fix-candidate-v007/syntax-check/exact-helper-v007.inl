// Called only after NextBoundary has bounded every body's MotionSegments
// From/To point. PositionAt is one affine observation strictly inside (Begin,End);
// either exact endpoint may be a zero-duration/new segment, queried separately.
// An analytic root is only a bracket proposal, never the legality predicate.
bool FirstRepresentableWakeEntry(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,
    Guard::FPoint Center,double Begin,double End,double& At)
{
    if(!(End>Begin))return false;
    const auto Inside=[&](double Time)
    {
        const auto P=PositionAt(B,F,Time);
        const double X=(P.X-Center.X)/235.,Y=(P.Y-Center.Y)/110.;
        return X*X+Y*Y<=1.; // Original native NearWake geometry, no epsilon.
    };
    if(Inside(Begin))return false; // The real cursor Pump already observed this.
    const auto FindInOpenSlice=[&](double SearchBegin,double Limit,double& Found)
    {
        if(!(Limit>SearchBegin))return false;
        // A real legal endpoint is already a bracket even if the discriminant
        // rounded negative. Do not let analytic cancellation veto that witness.
        double InsideTime=Limit;
        if(!Inside(InsideTime))
        {
            double Entry=0.,Exit=1.;
            if(!EllipseContact(PositionAt(B,F,SearchBegin)-XY(Center),PositionAt(B,F,Limit)-XY(Center),
                235.,110.,Entry,Exit))return false;
            InsideTime=SearchBegin+(Limit-SearchBegin)*Entry;
            if(!Inside(InsideTime))
            {
                InsideTime=SearchBegin+(Limit-SearchBegin)*(Entry+(Exit-Entry)*.5);
                if(!Inside(InsideTime))return false; // No certified legal bracket.
            }
        }
        double OutsideTime=SearchBegin;
        constexpr int MaxRefinements=std::numeric_limits<double>::max_exponent
            -std::numeric_limits<double>::min_exponent+std::numeric_limits<double>::digits+4;
        for(int I=0;I<MaxRefinements;++I)
        {
            const double Mid=OutsideTime+(InsideTime-OutsideTime)*.5;
            if(Mid==OutsideTime||Mid==InsideTime)
            {Found=InsideTime;return Found>Begin&&Found<=Limit&&Inside(Found);}
            if(Inside(Mid))InsideTime=Mid;else OutsideTime=Mid;
        }
        return false;
    };
    // Preserve half-open motion semantics. Never interpolate across an instant
    // target step to manufacture a Wake point between two real observations.
    const double AfterBegin=std::nextafter(Begin,End),BeforeEnd=std::nextafter(End,Begin);
    if(AfterBegin<End)
    {
        // ValidFrame also permits a zero-duration observation at Begin. Its
        // position cannot stand in for the mapping on the actual open slice.
        if(Inside(AfterBegin)){At=AfterBegin;return true;}
        if(FindInOpenSlice(AfterBegin,BeforeEnd,At))return true;
    }
    if(Inside(End)){At=End;return true;} // Real endpoint, including a legal step.
    return false;
}
