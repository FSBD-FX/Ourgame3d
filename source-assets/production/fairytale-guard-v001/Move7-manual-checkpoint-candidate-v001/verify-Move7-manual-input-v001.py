"""Read-only normal manual v012 gate; never starts UE or writes a receipt."""
import argparse,json
from move7_manual_contract_v001 import *
def main():
 p=argparse.ArgumentParser();p.add_argument('--manual-input',required=True);p.add_argument('--snapshot');a=p.parse_args()
 print(json.dumps(verify(a.manual_input,a.snapshot),ensure_ascii=False))
if __name__=='__main__':main()
