# sudo apt-get install python3-opengl
# pip3 install pyserial

# -*- coding: utf-8 -*-
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import time, random

import serial


#
# 指定端口
#
import argparse #导入模块

parser = argparse.ArgumentParser()  #创建解析对象
parser.add_argument("--com", default="COM3")    #向该对象中添加使用到的命令行选项和参数
args = parser.parse_args() #解析命令行

com_port = args.com


# ser = serial.Serial( '/dev/ttyUSB0', 9600, timeout=0 )
ser = serial.Serial(com_port, 9600, timeout=5)  # 开启com3口，波特率115200，超时5
ser.flushInput()  # 清空缓冲区

# 全局变量
ang_fw, ang_fy, ang_hg = 0, 0, 0    # 方位角，俯仰角，横滚角
last_fw, last_fy, last_hg = 0, 0, 0 # 上一次方位角、俯仰角、横滚角，用来判断异常数据
first_flag = True   # 第一次进入标识
error_times = 0     # 错误次数

def parse_data(d1, d2):
    """
    解析数据，解析从串口获取到的数据
    :param d1:第一个字节
    :param d2:第二个字节
    :return:角度值
    """
    sig = 1
    if d1 >= 128:
        d1 ^= 255
        d2 ^= 255
        sig = -1
    return (d1 * 256 + d2 + 1) / (100 * sig)


def get_data(ser):
    """
    从串口获取角度数据，然后保存在全局变量里
    :param ser: 串口
    :return:无
    """
    global ang_fw, ang_fy, ang_hg

    global last_fw, last_fy, last_hg
    global error_times, first_flag

    t1 = time.time()

    # 每次抓取17个字节数据，8字节一帧，至少存在1个完整帧
    buff = b''

    while True:
        data = ser.read(17 - len(buff))
        buff += data
        if len(buff) >= 17:
            break
        if time.time() - t1 > 0.5:
            return

    # print( 'read:', buff, len(buff) )
    for i in range(len(buff)):
        if buff[i] == 170:
            ang_fw = parse_data(buff[i + 1], buff[i + 2])
            ang_fy = parse_data(buff[i + 3], buff[i + 4])
            ang_hg = parse_data(buff[i + 5], buff[i + 6])

            # 记录上一次获取的值
            if first_flag:
                last_fw = ang_fw
                last_fy = ang_fy
                last_hg = ang_hg

                first_flag = False

            # 后面获取的值和上一次的值进行比较
            error = 3
            if abs(last_fw - ang_fw) > error or abs(last_fy - ang_fy) > error or abs(last_hg - ang_hg) > error:

                error_times += 1
                #print('第%d次异常数据：%.2f %.2f %.2f' % (error_times, ang_fw, ang_fy, ang_hg))

                # 连续三次和last变量比较，如果都不符合要求，说明之前的last变量初值是错误数据
                if error_times >= 3:
                    last_fw = ang_fw
                    last_fy = ang_fy
                    last_hg = ang_hg
                    error_times = 0
                else:
                    ang_fw = last_fw
                    ang_fy = last_fy
                    ang_hg = last_hg
            else:
                last_fw = ang_fw
                last_fy = ang_fy
                last_hg = ang_hg

                error_times = 0

            print('%.2f %.2f %.2f' % (ang_fw, ang_fy, ang_hg))
            return




GLUTFONTS = {
    "9x15": GLUT_BITMAP_9_BY_15,
    "8x13": GLUT_BITMAP_8_BY_13,
    "tr10": GLUT_BITMAP_TIMES_ROMAN_10,
    "tr24": GLUT_BITMAP_TIMES_ROMAN_24,
    "hv10": GLUT_BITMAP_HELVETICA_10,
    "hv12": GLUT_BITMAP_HELVETICA_12,
    "hv18": GLUT_BITMAP_HELVETICA_18,
}


def myBitmapLength(font, text):
    """ Compute the length in pixels of a text string in given font.

    We use our own fucntion to calculate the length because the builtin
    has a bug.
    """
    len = 0
    for c in text:
        len += GLUT.glutBitmapWidth(font, ord(c))
    return len


# font='tr24'
def drawText2D(text, x, y, font="9x15", adjust="left"):
    """Draw the given text at given 2D position in window.

    If adjust == 'center', the text will be horizontally centered on
    the insertion point.
    If adjust == 'right', the text will be right aligned on the point.
    Any other setting will align the text left.
    Default is to center.
    """
    if type(font) == str:
        font = glutFont(font)

    if adjust != "left":
        len1 = myBitmapLength(font, text)

    if adjust == "center":
        x -= len1 / 2
    elif adjust == "right":
        x -= len1

    glRasterPos2f(float(x), float(y))
    drawGlutText(text, font)


def glutFont(font):
    """
    Return GLUT font designation for the named font.

    The recognized font names are:
    fixed: '9x15', '8x13',
    times-roman: 'tr10', 'tr24'
    helvetica:   'hv10', 'hv12',  'hv18'
    If an unrecognized string is  given, the default is 9x15.
    """
    return GLUTFONTS.get(font, GLUTFONTS['9x15'])


def drawGlutText(text, font):
    """Draw a text in given font at the current rasterpoint.

    font should be one  of the legal fonts returned by glutFont().
    If text is not a string, it will be formatted to a string
    before drawing.
    After drawing, the rasterpos will have been updated!
    """
    for character in str(text):
        GLUT.glutBitmapCharacter(font, ord(character))


# 绘制图像函数
def drawFunc():
    global ang_fw, ang_fy, ang_hg

    # 清除屏幕及深度缓存
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    get_data(ser)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1, 0.01, 100)
    glViewport(0, 0, 800, 800)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # if ang_fw < 0 :
    #     ang_fw = 360 + ang_fw
    #
    # if ang_hg < 0:
    #     ang_hg = 360 + ang_hg

    ang_fw = ang_fw - 74
    ang_fy = -ang_fy
    ang_hg = ang_hg + 180

    drawText2D('ang_fw: %.2f' % ang_fw, -1, 0.95)
    drawText2D('ang_fy: %.2f' % ang_fy, -1, 0.90)
    drawText2D('ang_hg: %.2f' % ang_hg, -1, 0.85)

    # 设置绕轴旋转(角度,x,y,z)
    glRotatef(ang_fw, 0, 1, 0)
    glRotatef(ang_fy, 0, 0, 1)
    glRotatef(ang_hg, 1, 0, 0)

    # 绘制实心茶壶
    # glutSolidTeapot(0.5)

    # 绘制线框茶壶
    glutWireTeapot(0.5)

    glutSwapBuffers()
    # 刷新显示图像
    # glFlush()


if __name__ == "__main__":
    '''
    print( parse_data(254, 212) )
    exit()
    '''

    # 使用glut库初始化OpenGL
    glutInit()

    # 显示模式 GLUT_SINGLE无缓冲直接显示|GLUT_RGBA采用RGB(A非alpha)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)

    # 设置窗口位置及大小
    glutInitWindowPosition(0, 0)
    glutInitWindowSize(800, 800)

    # 创建窗口
    glutCreateWindow('Angle sensor')

    # 调用display()函数绘制图像
    glutDisplayFunc(drawFunc)

    # 设置全局的回调函数
    # 当没有窗口事件到达时,GLUT程序功能可以执行后台处理任务或连续动画
    glutIdleFunc(drawFunc)

    # 进入glut主循环
    glutMainLoop()

