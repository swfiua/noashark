"""
Build a very basic gallery
"""


from pathlib import Path

print("=========")
print(" Gallery ")
print("=========")
print()

p = Path()
for image in p.glob('images/*.png'):
    print(f'.. image:: {image}\n\n')
    print()
