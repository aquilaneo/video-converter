import sys
import os
import glob
import subprocess
import json


def convert_directory(dirPath, src, dest, bitrate_coef):
    # ファイルとディレクトリに仕分け
    listDir = os.listdir(dirPath)
    files = glob.glob(os.path.join(dirPath, "*." + src))
    directories = [directory for directory in listDir if os.path.isdir(os.path.join(dirPath, directory))]
    
    for file in files:
        newName = file.replace("." + src, "." + dest)
        info = get_info(file)
        if info["codec"] != "h265" and info["codec"] != "hevc":
            encode(file, newName, info["bitrate"] * bitrate_coef)
            os.remove(file)
    
    # サブフォルダも再帰的に変換
    for directory in directories:
        convert_directory(os.path.join(dirPath, directory), src, dest, bitrate_coef)


def get_info(path):
    # ffprobeコマンドを使用
    result = subprocess.run(["ffprobe", "-i", path, "-hide_banner", "-show_streams", "-show_format", "-print_format", "json", "-loglevel", "quiet"], encoding="utf-8", stdout=subprocess.PIPE)
    result_json = json.loads(result.stdout)

    # 情報を取得
    codec = result_json["streams"][0]["codec_name"]
    bitrate = int(result_json["format"]["bit_rate"])
    return {"codec": codec, "bitrate": bitrate}


def encode(inputPath, outputName, target_bitrate):
    subprocess.run(["ffmpeg", "-i", inputPath, "-c:v", "hevc_nvenc", "-c:a", "copy", "-b:v", str(target_bitrate), "-tag:v", "hvc1", outputName])


# コマンドライン引数読み取り
args = sys.argv
if len(args) != 5:
    print("Error: コマンドライン引数を入力してください！")
    exit()
dirPath = args[1]
src = args[2]
dest = args[3]
bitrate_coef = float(args[4])

# ディレクトリかどうか判断
if not os.path.isdir(dirPath):
    print("Error: コマンドライン引数にはディレクトリのパスを指定してください！")
    exit()

# 変換開始
convert_directory(dirPath, src, dest, bitrate_coef)