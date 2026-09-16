import os

# ===== Super constants (From HY300PRO+) =====
SUPER_SIZE = 2147483648
METADATA_SIZE = 65536
METADATA_SLOTS = 3
GROUP_SIZE = 2139095040

# ===== Helper =====
def get_size(filename):
    if os.path.exists(filename):
        return os.path.getsize(filename)
    return 0

# ===== Read sizes =====
system_a  = get_size("system_a.img")
vendor_a  = get_size("vendor_a.img")
product_a = get_size("product_a.img")

system_b  = get_size("system_b.img")
vendor_b  = get_size("vendor_b.img")
product_b = get_size("product_b.img")

print("Detected sizes:")
print("system_a =", system_a)
print("vendor_a =", vendor_a)
print("product_a =", product_a)
print("system_b =", system_b)
print("vendor_b =", vendor_b)
print("product_b =", product_b)
print()

# ===== Build command =====
cmd = f"""
.\\lpmake `
--metadata-size {METADATA_SIZE} `
--super-name super `
--metadata-slots {METADATA_SLOTS} `
--device super:{SUPER_SIZE} `
--group sb_a:{GROUP_SIZE} `
--group sb_b:{GROUP_SIZE} `
--partition system_a:readonly:{system_a}:sb_a `
--image system_a=system_a.img `
--partition vendor_a:readonly:{vendor_a}:sb_a `
--image vendor_a=vendor_a.img `
--partition product_a:readonly:{product_a}:sb_a `
--image product_a=product_a.img `
--partition system_b:readonly:{system_b}:sb_b `
--partition vendor_b:readonly:{vendor_b}:sb_b `
--partition product_b:readonly:{product_b}:sb_b `
--sparse `
-o super_new.img
"""

print("Generated lpmake command:")
print(cmd)