import os

os.add_dll_directory(r"C:\vips\bin")
from concurrent.futures import ThreadPoolExecutor, as_completed

import pyvips
from tqdm import tqdm

# =========================
# CONFIG
# =========================
CPU_COUNT = os.cpu_count() or 4

# 👉 libvips는 내부적으로 멀티스레드 사용
# 너무 많이 돌리면 오히려 느려짐
WORKERS = max(2, CPU_COUNT // 2)


# =========================
# FILE LIST
# =========================
def get_file_list(directory, extension=".png"):
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extension):
                file_list.append(os.path.join(root, file))
    return file_list


# =========================
# CONVERT
# =========================
def convert_single_png_to_webp(png_path):
    webp_path = os.path.splitext(png_path)[0] + ".webp"

    try:
        image = pyvips.Image.new_from_file(
            png_path,
            access="sequential",
        )

        image.write_to_file(
            webp_path,
            lossless=True,
            effort=4,
        )

        return (png_path, True, "")

    except Exception as e:
        return (png_path, False, str(e))


def convert_png_to_webp(directory):
    png_files = get_file_list(directory, ".png")

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(convert_single_png_to_webp, path): path
            for path in png_files
        }

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Converting (pyvips)",
        ):
            png_path, success, err = future.result()
            if not success:
                print(f"[ERROR] {png_path}")
                print(err)


# =========================
# DELETE
# =========================
def delete_png_files(directory):
    png_files = get_file_list(directory, ".png")

    for file in tqdm(png_files, desc="Deleting PNG"):
        os.remove(file)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    target_dir = r"D:\workspace\Kanatales\kanadb\static\card\Texture2D"

    convert_png_to_webp(target_dir)
    delete_png_files(target_dir)
