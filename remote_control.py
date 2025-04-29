""" 
PYTHONPATH=. python -m ahkpy remote_control.py
"""
from  ahkpy_beamicon import beamicon

def main():
    doc = beamicon.setup_external_keyboard()
    print(doc)

if __name__ == "__main__":
    main()
