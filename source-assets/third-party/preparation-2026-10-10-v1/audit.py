"""Read asset structure and checksums without editing source assets or displaying media.

These metadata checks do not verify Unity import, animation retargeting, visual style,
sound quality, animation behavior, or gameplay readiness.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import struct
import wave

ROOT=Path(__file__).resolve().parent

def fbx_info(path):
    b=path.read_bytes()
    if not b.startswith(b'Kaydara FBX Binary  \0\x1a\0'):
        return {'format':'FBX ASCII or unsupported; not parsed'}
    version=struct.unpack_from('<I',b,23)[0]
    wide=version>=7500
    header_size=25 if wide else 13
    header_fmt='<QQQB' if wide else '<IIIB'
    selected=[]
    scalar={'Y':('<h',2),'C':('<?',1),'I':('<i',4),'F':('<f',4),'D':('<d',8),'L':('<q',8)}
    def node(pos):
        end,count,prop_len,name_len=struct.unpack_from(header_fmt,b,pos)
        if end==0:
            return None,pos+header_size
        pos+=header_size
        name=b[pos:pos+name_len].decode('utf-8','replace')
        pos+=name_len
        props=[]
        for _ in range(count):
            kind=chr(b[pos]);pos+=1
            if kind in scalar:
                fmt,size=scalar[kind]
                value=struct.unpack_from(fmt,b,pos)[0];pos+=size
            elif kind in 'SR':
                size=struct.unpack_from('<I',b,pos)[0];pos+=4
                value=b[pos:pos+size].decode('utf-8','replace') if kind=='S' else {'raw_bytes':size}
                pos+=size
            elif kind in 'fdlibc':
                length,encoding,size=struct.unpack_from('<III',b,pos);pos+=12+size
                value={'array_count':length,'encoding':encoding,'stored_bytes':size}
            else:
                raise ValueError(f'Unknown FBX property type {kind!r}')
            props.append(value)
        children=[]
        while pos<end:
            if b[pos:pos+header_size]==bytes(header_size):
                pos+=header_size
                break
            child,pos=node(pos)
            if child:
                children.append(child)
        item={'name':name,'props':props,'children':children}
        if name in ('Model','Geometry','Deformer','AnimationStack','AnimationLayer','Take','Texture','Video','P'):
            selected.append(item)
        return item,end
    pos=27
    while pos+header_size<=len(b) and b[pos:pos+header_size]!=bytes(header_size):
        _,pos=node(pos)
    def clean(x):
        return x.split('\0')[0] if isinstance(x,str) else x
    models=[n for n in selected if n['name']=='Model' and len(n['props'])>=3]
    bones=[clean(n['props'][1]) for n in models if n['props'][2] in ('LimbNode','Root')]
    mesh_models=[clean(n['props'][1]) for n in models if n['props'][2]=='Mesh']
    anims=[]
    for n in selected:
        if n['name']=='AnimationStack':
            info={'name':clean(n['props'][1] if len(n['props'])>1 else n['props'][0])}
            for child in n['children']:
                for prop in child['children']:
                    p=prop['props']
                    if len(p)>4 and p[0] in ('LocalStart','LocalStop','ReferenceStart','ReferenceStop'):
                        info[p[0]]=p[-1]
            if 'LocalStart' in info and 'LocalStop' in info:
                info['duration_seconds_from_fbx_ticks']=(info['LocalStop']-info['LocalStart'])/46186158000
            anims.append(info)
    units=[n['props'][-1] for n in selected if n['name']=='P' and n['props'] and n['props'][0]=='UnitScaleFactor']
    deform=Counter(n['props'][2] for n in selected if n['name']=='Deformer' and len(n['props'])>2)
    textures=[n['props'][-1] for n in selected if n['name']=='P' and n['props'] and n['props'][0]=='Path']
    return {'format':'binary FBX','fbx_version':version,'unit_scale_factor':units,'mesh_model_names':mesh_models,'bone_count':len(bones),'bone_names':bones,'deformer_counts':dict(deform),'animation_stack_count':len(anims),'animation_stacks':anims,'texture_property_paths':textures}

def glb_info(path):
    b=path.read_bytes()
    if b[:4]!=b'glTF':
        raise ValueError('Not a GLB')
    version,total=struct.unpack_from('<II',b,4)
    pos=12
    data=None
    while pos<total:
        size,kind=struct.unpack_from('<II',b,pos);pos+=8
        if kind==0x4e4f534a:
            data=json.loads(b[pos:pos+size].decode())
            break
        pos+=size
    nodes=data.get('nodes',[])
    skins=[{'name':s.get('name'),'joint_count':len(s.get('joints',[])),'joint_names':[nodes[j].get('name',str(j)) for j in s.get('joints',[])]} for s in data.get('skins',[])]
    anims=[]
    for a in data.get('animations',[]):
        ranges=[]
        for sampler in a.get('samplers',[]):
            accessor=data.get('accessors',[])[sampler['input']]
            if 'min' in accessor and 'max' in accessor:
                ranges.append((accessor['min'][0],accessor['max'][0]))
        item={'name':a.get('name'),'channel_count':len(a.get('channels',[]))}
        if ranges:
            item['time_min_seconds']=min(v[0] for v in ranges)
            item['time_max_seconds']=max(v[1] for v in ranges)
        anims.append(item)
    return {'format':'GLB','version':version,'meshes':len(data.get('meshes',[])),'skins':skins,'animation_count':len(anims),'animations':anims}

def ogg_info(path):
    b=path.read_bytes()
    pos=0
    last_granule=0
    first_packet=b''
    pages=0
    while pos+27<=len(b):
        if b[pos:pos+4]!=b'OggS':
            raise ValueError('Invalid Ogg page boundary')
        granule=struct.unpack_from('<Q',b,pos+6)[0]
        segments=b[pos+26]
        lacing=b[pos+27:pos+27+segments]
        size=sum(lacing)
        start=pos+27+segments
        if pages==0:
            first_packet=b[start:start+size]
        if granule!=0xffffffffffffffff:
            last_granule=granule
        pages+=1
        pos=start+size
    out={'format':'Ogg','pages':pages,'valid_page_boundaries':pos==len(b)}
    if first_packet.startswith(b'\x01vorbis'):
        channels=first_packet[11]
        rate=struct.unpack_from('<I',first_packet,12)[0]
        out.update(codec='Vorbis',channels=channels,sample_rate_hz=rate,duration_seconds=last_granule/rate)
    elif first_packet.startswith(b'OpusHead'):
        pre_skip=struct.unpack_from('<H',first_packet,10)[0]
        out.update(codec='Opus',channels=first_packet[9],sample_rate_hz=48000,duration_seconds=(last_granule-pre_skip)/48000)
    return out

def audit(folder):
    root=folder/'extracted'
    listing=[]
    parsed=[]
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        b=p.read_bytes()
        rel=str(p.relative_to(root))
        listing.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        try:
            if p.suffix.lower()=='.fbx':
                info=fbx_info(p)
            elif p.suffix.lower()=='.glb':
                info=glb_info(p)
            elif p.suffix.lower()=='.ogg':
                info=ogg_info(p)
            elif p.suffix.lower()=='.wav':
                with wave.open(str(p)) as w:
                    info={'format':'WAV','sample_rate_hz':w.getframerate(),'channels':w.getnchannels(),'duration_seconds':w.getnframes()/w.getframerate()}
            else:
                continue
        except Exception as e:
            info={'parse_error':str(e)}
        parsed.append({'path':rel,**info})
    (folder/'file-checksums-sha256.json').write_text(json.dumps(listing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (folder/'structure-audit.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(folder.name,'files',len(listing),'audited structures',len(parsed),'errors',sum('parse_error' in p for p in parsed),flush=True)

if __name__=='__main__':
    for folder in ROOT.iterdir():
        if folder.is_dir() and (folder/'extracted').is_dir():
            audit(folder)
