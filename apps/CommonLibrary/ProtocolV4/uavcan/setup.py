from setuptools import setup, find_packages

setup(
    name="motorasst",
    version="0.1.0",
    packages=["MotorAsst", "MotorAsst.lib", "MotorAsst.ui","MotorAsst.drivers"],  # 显式声明包结构
    package_dir={
        "MotorAsst": "MotorAsst",  # 主包映射
        "MotorAsst.lib": "MotorAsst/lib",
        "MotorAsst.ui": "MotorAsst/ui",
        "MotorAsst.ui": "MotorAsst/drivers"
    },
    install_requires=[
        "pycyphal>=1.20",
        "PyQt6>=6.4.0",
    ],
    python_requires=">=3.10",
)