BlockA = 0x24  
BlockB = 0xab

print(":::Blocks:::")
print("BlockA = " + hex(BlockA))
print("BlockB = " + hex(BlockB))
print(":::Blocks:::")

print("\n")

CURR = BlockA
PREV = CURR >> 1

print(":::init:::")
print("curr = A")
print("prev = " + hex(PREV))
print(":::init:::")

print("\n")

CURR = BlockB
rip = CURR ^ PREV 
PREV = CURR >> 1

print(":::A -> B:::")
print("curr = B")
print("rip = " + hex(rip))
print("prev = " + hex(PREV))
print(":::A -> B:::")

print("\n")

CURR = BlockA
rip = CURR ^ PREV
PREV = CURR >> 1

print(":::B -> A:::")
print("curr = A")
print("rip = " + hex(rip))
print("prev = " + hex(PREV))
print(":::B -> A:::")
