# Numerical reproduction of native scalar formulas; not UE/runtime acceptance.
from pathlib import Path
import json,math,struct,hashlib
HERE=Path(__file__).resolve().parent
BEGIN=9.605689999759198
WIDE_END=9.610689999759199
REPLANNED_END=9.607490869337335
X=-1035.4682208563124
Y=-162.2042858545901
SPEED=struct.unpack('f',struct.pack('f',286.2))[0]
def run(end,fixed):
    x1=X+SPEED*(end-BEGIN)
    def position(t):return X+(x1-X)*min(1.,max(0.,(t-BEGIN)/(end-BEGIN)))
    def r2(t):return ((position(t)+800.)/235.)**2+((Y+160.)/110.)**2
    cursor=BEGIN;trace=[]
    for iteration in range(128):
        if r2(cursor)<=1.:return dict(accepted=True,wake_at=cursor,end=end,trace=trace,previous_r2=r2(math.nextafter(cursor,BEGIN)),r2=r2(cursor))
        if cursor==end:return dict(accepted=True,wake_at=None,end=end,trace=trace)
        p=(position(cursor)+800.)/235.;dy=(Y+160.)/110.;d=(position(end)-position(cursor))/235.
        a=d*d;b=2.*p*d;c=p*p+dy*dy-1.;disc=b*b-4.*a*c;nxt=end;entry=exit=None
        if a>0. and disc>=0.:
            entry=max(0.,(-b-math.sqrt(disc))/(2.*a));exit=min(1.,(-b+math.sqrt(disc))/(2.*a))
            if entry<=exit and entry<=1. and exit>=0.:
                if fixed:
                    inside=cursor+(end-cursor)*entry
                    if r2(inside)>1.:
                        inside=cursor+(end-cursor)*(entry+(exit-entry)*.5)
                        if r2(inside)>1.:
                            inside=end
                    if r2(inside)<=1.:
                        outside=cursor
                        for j in range(2100):
                            mid=outside+(inside-outside)*.5
                            if mid==outside or mid==inside:break
                            if r2(mid)<=1.:inside=mid
                            else:outside=mid
                        nxt=inside
                elif entry>0.:nxt=cursor+(end-cursor)*entry
        trace.append(dict(iteration=iteration,cursor=cursor,limit=end,entry=entry,exit=exit,next=nxt,r2_at_cursor=r2(cursor),r2_at_next=r2(nxt)))
        if not nxt>cursor:return dict(accepted=False,reason='!(Next>Cursor)',end=end,trace=trace)
        cursor=nxt
    return dict(accepted=False,reason='iteration-limit',trace=trace)
def main():
    result=dict(schema='guard-wake-rounding-numerical-reproduction-v003',scope='Independent numerical reconstruction from original observation plus read-only native formulas. NOT actual UE-driver execution, compile, runtime, capture, visual or art acceptance.',frozen_input=dict(begin=BEGIN,wide_end=WIDE_END,replanned_end=REPLANNED_END,target_from=[X,Y],speed_float=SPEED),original_wide=run(WIDE_END,False),original_replanned=run(REPLANNED_END,False),candidate_wide=run(WIDE_END,True),candidate_replanned=run(REPLANNED_END,True))
    assert result['original_wide']['accepted']
    assert not result['original_replanned']['accepted']
    for name in ['candidate_wide','candidate_replanned']:
        q=result[name];assert q['accepted'] and q['previous_r2']>1 and q['r2']<=1
    assert result['candidate_wide']['wake_at']==result['candidate_replanned']['wake_at']
    dest=HERE/'numerical-reproduction-result-v003.json'
    if dest.exists():raise SystemExit('Refuse overwrite existing numerical result')
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Numerical original-replanned RED; representable-entry candidate GREEN. NOT UE acceptance.')
    print(dest)
if __name__=='__main__':main()
