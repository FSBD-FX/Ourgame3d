"""Revision2 narrows real hand/cuff boundaries; preserves original candidate files."""
from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'assemble-XBW-reload-four-keyposes-v001.py').read_text('utf-8')
source=source.replace('XBW-reload-four-keyposes-v001','XBW-reload-four-keyposes-v002').replace('XBW-reload-four-keyposes-{name}-v001','XBW-reload-four-keyposes-{name}-v002').replace('XBW-reload-four-keypose-layer-candidate-v001','XBW-reload-four-keypose-layer-candidate-v002')
start=source.index('near_polys=[');end=source.index('support_polys=[',start)
source=source[:start]+'''near_polys=[
 [(266,264),(294,264),(303,259),(315,255),(331,254),(342,257),(350,263),(350,270),(345,272),(337,268),(332,268),(334,274),(339,279),(338,284),(331,287),(327,290),(335,286),(342,284),(346,286),(346,290),(338,294),(324,296),(310,296),(301,292),(294,296),(270,294),(265,287)],
 [(175,265),(203,264),(213,263),(224,262),(236,264),(242,268),(245,273),(246,279),(243,282),(239,283),(240,287),(236,291),(231,293),(226,296),(221,295),(217,293),(210,294),(202,292),(176,291)],
 [(215,267),(239,269),(250,271),(255,265),(268,259),(281,258),(292,262),(297,268),(298,273),(293,275),(287,272),(285,276),(286,280),(296,279),(301,282),(301,286),(296,291),(279,291),(270,293),(256,290),(248,288),(239,292),(218,289),(215,282)],
 [(181,297),(205,297),(212,296),(221,295),(231,296),(238,300),(241,305),(240,309),(238,312),(240,316),(238,320),(234,323),(225,325),(214,324),(207,321),(198,321),(182,318)]]
''' + source[end:]
source=source.replace('loading_bolt_pincher_negative_space','loading_bolt_pinch_gap_in_front_of_underlying_torso')
source=source.replace('pinch center may correctly be alpha0 between opaque fingers.','pinch gap may show underlying opaque torso; the near-hand selection leaves its opening free so the bolt can occupy the gap. Overall body alpha alone cannot classify this opening.')
exec(compile(source,str(P/'assemble-XBW-reload-four-keyposes-v002.py'),'exec'))
