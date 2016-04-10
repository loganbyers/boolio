# boolio
Python library for handling interactions with booleans.io

# Note
boolio is under active development.

# Requirements
[requests](http://python-requests.org/)

# Example
```python
import boolio

# make a bool and save it
b = boolio.Bool()
print b.bid, b.val  # ???, False
b(True)
print b.bid, b.val  # ???, True
boolio.save('important_flag.bool', b)


# make a string of bool and save it
bs = boolio.BoolString(8 * 4)
print bs  # 00000000000000000000000000000000
for i, b in enumerate(bs):
    if not (i % 8):
        b(True)
print bs  # 00000001000000010000000100000001
boolio.save('debit_card_PIN.bool', bs)


# load string of bool and interpret as byte
pin_secret = boolio.load('debit_card_PIN.bool')
print len(pin_secret)  # 32
pin = []
for i in range(4):
    byte = str(pin_secret)[i*8:(i+1)*8]
    pin.append(int(byte, 2))
print pin  # [1, 1, 1, 1]


```
