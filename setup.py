import os
import random
import string


def create_demo_folder_with_files():
    folder_name = "demo"
    file_names = [f"file{i}.txt" for i in range(1, 5)]

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    if not os.path.exists(folder_name + "/unpack"):
        os.makedirs(folder_name + "/unpack")
    if not os.path.exists(folder_name + "/full_unpack"):
        os.makedirs(folder_name + "/full_unpack")

    for file_name in file_names:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        shuffled_content = ''.join(random.sample(random_string, len(random_string)))

        with open(os.path.join(folder_name, file_name), "w") as file:
            file.write(shuffled_content)

    print(f"Folder '{folder_name}' created with files: {', '.join(file_names)}")


if __name__ == "__main__":
    create_demo_folder_with_files()