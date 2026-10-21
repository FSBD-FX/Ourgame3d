"""Host contract tests. They do not import assets or simulate an Unreal result."""
import copy
from pathlib import Path
import unittest
from dodge32_import_contract_v001 import validate_layout, validate_receipt_assets

ROOT=Path('F:/Ourgame')
NAMESPACE='/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge'
COMPONENTS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground','ShoulderFar','Chest','ShoulderNear']

def fixture():
    assets=[]
    for frame in range(4):
        for component in COMPONENTS:
            name=f'T_Fairytale_Dodge_{component}_{frame:03d}_v001'
            package=NAMESPACE+'/'+name
            assets.append(dict(component=component,frame=frame,name=name,package_path=package,
                object_path=package+'.'+name,destination_path=NAMESPACE,
                source=dict(path=f'F:/Ourgame/HOST_SYNTHETIC_ONLY/{component}/{frame}.png',bytes=1,sha256='a'*64),
                source_RGBA_sha256='b'*64,
                saved_path=(ROOT/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset')).as_posix()))
    return dict(schema='Root-Dodge32-native-import-v001',expected_old_count=1332,expected_new_count=32,
        expected_final_count=1364,namespace=NAMESPACE,replace_existing=False,assets=assets)

def receipt_for(m):
    return dict(assets=[dict(component=x['component'],frame=x['frame'],source=copy.deepcopy(x['source']),
        actual_object_path=x['object_path'],actual_class='Texture2D',actual_dimensions=[512,512],
        actual_import_filenames=[x['source']['path']],
        actual_settings=dict(compression_settings='<TextureCompressionSettings.TC_EDITOR_ICON: 7>',
            mip_gen_settings='<TextureMipGenSettings.TMGS_NO_MIPMAPS: 13>',
            lod_group='<TextureGroup.TEXTUREGROUP_UI: 16>',never_stream='True',srgb='True',
            filter='<TextureFilter.TF_BILINEAR: 1>'),
        saved=dict(path=x['saved_path'],bytes=2,sha256='c'*64)) for x in m['assets']])

class Dodge32ContractTests(unittest.TestCase):
    def test_valid_exact_8_by_4_layout_and_native_metadata(self):
        m=fixture();validate_layout(m,ROOT);validate_receipt_assets(m,receipt_for(m),ROOT)

    def test_rejects_missing_or_duplicate_frame_before_any_import(self):
        for edit in [lambda m:m['assets'].pop(),lambda m:m['assets'].__setitem__(31,copy.deepcopy(m['assets'][0]))]:
            m=fixture();edit(m)
            with self.assertRaises(ValueError):validate_layout(m,ROOT)

    def test_rejects_saved_path_substitution_outside_exact_new_namespace(self):
        m=fixture();m['assets'][0]['saved_path']='F:/Ourgame/UnrealGame/Content/Production/EXISTING.uasset'
        with self.assertRaises(ValueError):validate_layout(m,ROOT)

    def test_rejects_native_duplicate_class_provenance_and_setting_substitution(self):
        changes=[lambda r:r['assets'].__setitem__(31,copy.deepcopy(r['assets'][0])),
            lambda r:r['assets'][0].update(actual_class='Texture'),
            lambda r:r['assets'][0].update(actual_import_filenames=['F:/Ourgame/OTHER.png']),
            lambda r:r['assets'][0]['actual_settings'].update(srgb='False')]
        for edit in changes:
            m=fixture();r=receipt_for(m);edit(r)
            with self.assertRaises(ValueError):validate_receipt_assets(m,r,ROOT)

if __name__=='__main__':unittest.main(verbosity=2)
