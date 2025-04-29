""" 
PYTHONPATH=. python -m ahkpy remote_control.py
"""
from  autohotkey_py_beamicon import beamicon

def main():
    doc = beamicon.setup_external_keyboard()
    print(doc)

if __name__ == "__main__":
    main()
