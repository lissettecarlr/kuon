try:
    from win32.lib import win32con
    from win32.win32api import GetSystemMetrics
    from win32.win32gui import GetDC
    from win32.win32print import GetDeviceCaps
    win32_flag = True
except:
    win32_flag = False
    screen_scale_rate_ = 1

# 获取显示器物理分辨率
def get_real_resolution():
    hDC = GetDC(0)
    # 横向分辨率
    w = GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h

# 获取系统设置的分辨率
def get_screen_size():
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    return w, h