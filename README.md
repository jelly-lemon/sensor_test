# 倾角传感器测试
程序功能描述：用串口连接一个倾角传感器，根据倾角传感器返回来的角度信息，同步绘制茶壶。   
![avatar](https://github.com/jelly-lemon/sensor_test/blob/master/image/%E5%80%BE%E8%A7%92%E4%BC%A0%E6%84%9F%E5%99%A8%20%E8%8C%B6%E5%A3%B6.gif)

# 其它说明
绘制茶壶需要用到 PyOpenGL 库，但是如果直接使用 pip 安装 PyOpenGL（也就是使用命令 pip install PyOpenGL），那么此时安装的版本是 32 位的，就和我用的 64 位 Python 不兼容，会有问题。换句话说，通过 pip 只能安装 32 位的 PyOpenGL 库，但是我们需要 64 位的，所以需要手动安装。   

首先下载 64 位的安装包 PyOpenGL-3.1.5-cp36-cp36m-win_amd64.whl（我已经放在了本项目中），然后需要手动安装，也就是用命令 pip install PyOpenGL-3.1.5-cp36-cp36m-win_amd64.whl。
