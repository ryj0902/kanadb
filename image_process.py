import hashlib
import os
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

from tqdm import tqdm


def hash_png_file(path, base_dir):
    """파일 해시 값 계산"""
    with open(path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    rel_path = os.path.relpath(path, base_dir)
    return rel_path, file_hash


def get_file_list(directory, extension=".png"):
    """디렉토리 내 특정 확장자 파일들의 절대 경로 목록 반환"""
    file_list = []
    for file in os.listdir(directory):
        if file.lower().endswith(extension):
            path = os.path.join(directory, file)
            file_list.append(path)
    return file_list


def get_png_hashes(directory, max_workers=8):
    """디렉토리 내 모든 png 파일에 대한 해시 값 반환"""
    hashes = {}
    png_files = get_file_list(directory, ".png")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(hash_png_file, path, directory): path for path in png_files
        }
        for future in tqdm(
            as_completed(futures), total=len(futures), desc=f"Hashing: {directory}"
        ):
            rel_path, file_hash = future.result()
            hashes[rel_path] = file_hash

    return hashes


def copy_changed_files(target_dir, orig_dir, old_dir, new_dir):
    """변경된 PNG 파일을 new_dir로 복사"""
    os.makedirs(new_dir, exist_ok=True)
    target_hashes = get_png_hashes(target_dir)
    orig_hashes = get_png_hashes(orig_dir)
    old_files = get_file_list(old_dir, ".webp")

    # 복사가 필요한 파일 리스트 추출
    copy_list = []
    for rel_path, target_hash in target_hashes.items():
        orig_hash = orig_hashes.get(rel_path)
        filename = os.path.join(old_dir, rel_path.replace(".png", ".webp"))
        if orig_hash != target_hash or filename not in old_files:
            copy_list.append(rel_path)
    print(f"[INFO] 신규 파일 개수: {len(copy_list)}")

    for rel_path in tqdm(copy_list, desc="Copy to new dir"):
        src_path = os.path.join(target_dir, rel_path)
        dest_path = os.path.join(new_dir, rel_path)
        shutil.copy2(src_path, dest_path)


def convert_single_png_to_webp(png_path):
    """단일 PNG → WebP 변환 함수"""
    webp_path = os.path.splitext(png_path)[0] + ".webp"
    try:
        subprocess.run(
            ["cwebp", "-lossless", png_path, "-o", webp_path],
            check=True,
            capture_output=True,
        )
        return (png_path, True, "")
    except subprocess.CalledProcessError as e:
        return (png_path, False, e.stderr.decode())


def convert_png_to_webp(directory, max_workers=8):
    """PNG → WebP 변환 작업을 멀티프로세싱으로 수행"""
    png_files = get_file_list(directory, ".png")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(convert_single_png_to_webp, path): path
            for path in png_files
        }

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Converting to WebP"
        ):
            png_path, success, err = future.result()
            if not success:
                print(f"[ERROR] Failed to convert: {png_path}")
                print(err)


def delete_png_files(directory):
    """디렉토리 내 PNG 파일 삭제"""
    png_files = get_file_list(directory, ".png")

    for file in tqdm(png_files, desc="Deleting png"):
        os.remove(file)


def merge_directories(src_dir, dst_dir):
    """src_dir의 파일들을 dst_dir로 복사(덮어쓰기)"""
    for root, _, files in os.walk(src_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), src_dir)
            dst_path = os.path.join(dst_dir, rel_path)
            shutil.copy2(os.path.join(root, file), dst_path)


if __name__ == "__main__":
    # 방금 추출한 png 파일들
    target_dir = "D:\workspace\Kanatales\kanadb\static\card\Texture2D"
    # 기존에 추출했었던 png 파일들
    orig_dir = "D:\workspace\Kanatales\kanadb\static\card\Texture2D_orig"
    # 기존에 사용하던 webp 파일들
    old_dir = "D:\workspace\Kanatales\kanadb\static\card\Texture2D_old"
    # 새로 갱신해야 할 webp 파일들
    new_dir = "D:\workspace\Kanatales\kanadb\static\card\Texture2D_new"

    # 1. 변경 파일 복사
    copy_changed_files(target_dir, orig_dir, old_dir, new_dir)
    # 2. PNG → WebP 변환
    convert_png_to_webp(new_dir)
    # 3. PNG 삭제
    delete_png_files(new_dir)
    # 4. orig_dir 제거 + target_dir → orig_dir 이름 변경
    print(f"Remove {orig_dir}")
    shutil.rmtree(orig_dir)
    os.rename(target_dir, orig_dir)
    # 5. new_dir → old_dir 병합, old_dir → target_dir 변경
    print("Merge new → old dir")
    merge_directories(new_dir, old_dir)
    print("Rename Texture2D_old → Texture2D")
    os.rename(old_dir, target_dir)

    # convert_png_to_webp(target_dir)
    # delete_png_files(target_dir)
