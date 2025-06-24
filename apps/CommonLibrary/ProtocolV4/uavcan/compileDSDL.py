#!/usr/bin/env python3
#将dsdl文件编译为.py文件
import sys
import pathlib
import pycyphal.dsdl

def compile_dsdl() -> None:
    # 定义路径
    user_dsdl_repo = pathlib.Path("custom_data_types").resolve()  # 用户DSDL仓库
    dsdl_repo = pathlib.Path("public_regulated_data_types").resolve()  # 官方DSDL仓库
    output_dir = pathlib.Path(".pyFolder")  # 编译输出目录
    
    # 检查是否已编译
    if output_dir.exists():
        print(f"[SKIP] DSDL已编译到目录: {output_dir}")
        return
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 编译官方DSDL接口
    print(f"正在编译DSDL从 {dsdl_repo} 到 {output_dir}...")
    pycyphal.dsdl.compile_all(
        [
            dsdl_repo / "uavcan",
            dsdl_repo / "reg",
            user_dsdl_repo / "dinosaurs",
        ],
        output_directory=output_dir,
    )
    print(f"[SUCCESS] DSDL编译完成! 输出目录: {output_dir}")

if __name__ == "__main__":
    compile_dsdl()
# .myvenv) zhangge@sr:~/worknote/ProtocolV4/uavcan$ tree -L 3 -a
# .
# ├── MotorAsst
# │   ├── release
# │   │   ├── hardware
# │   │   ├── lib
# │   │   ├── src
# │   │   └── ui
# │   └── test
# │       ├── designer_test.py
# │       ├── main.ui
# │       ├── __pycache__
# │       └── ui_main.py
# ├── .myvenv
# ├── .pyFolder
# │   ├── dinosaurs
# │   │   ├── __init__.py
# │   │   ├── TimeSync_1_0.py
# │   │   └── WorkMode_1_0.py
# │   ├── nunavut_support.py
# │   ├── reg
# │   │   ├── __init__.py
# │   │   └── udral
# │   └── uavcan
# │       ├── diagnostic
# │       ├── file
# │       ├── __init__.py
# │       └── time
# ├── setup.py
