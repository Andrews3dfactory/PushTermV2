import os

base_dir = os.path.dirname(os.path.abspath(__file__))
myprints_dir = os.path.join(base_dir, "MyPrints")

print("Base directory:", base_dir)
print("MyPrints directory:", myprints_dir)

print("\nFiles in base directory:")
print(os.listdir(base_dir))

print("\nFiles in MyPrints folder:")
if os.path.exists(myprints_dir):
    print(os.listdir(myprints_dir))
else:
    print("MyPrints folder does not exist yet.")