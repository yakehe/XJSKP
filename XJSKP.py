import Quartz
import os
import pytesseract
import pyautogui
import subprocess
import time
import Quartz.CoreGraphics as CG
import datetime
from PIL import Image
import logging
from email_sender import send_email


# 发送邮件
sender_email = "xxxxx@163.com"
receiver_email = "xxxxx@icloud.com"
smtp_server = "smtp.163.com"
port = 25
password = "xxxxxx"


def send_email_a(content,title):
    subject = title
    body = content
    send_email(sender_email, receiver_email, subject, body, smtp_server, port, password)


# 配置日志记录器
logging.basicConfig(filename='/Users/suimulate/Desktop/game.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def click_at_position(x, y):
    event = CG.CGEventCreateMouseEvent(
        None, 
        CG.kCGEventLeftMouseDown, 
        (x, y), 
        CG.kCGMouseButtonLeft
    )
    CG.CGEventPost(CG.kCGHIDEventTap, event)
    CG.CGEventSetType(event, CG.kCGEventLeftMouseUp)
    CG.CGEventPost(CG.kCGHIDEventTap, event)

# 设置点击坐标
hack_coordinates = [(600, 187), (340, 478)]  # 替换成你想要点击的坐标
start_coordinates = [(330, 800), (1000, 54)]  # 替换成你想要点击的坐标
pause_coordinates = [(100, 90)]  # 替换成你想要点击的坐标
select_coordinates = [(165, 440),(323, 440),(489, 440)]  # 替换成你想要点击的坐标
end_coordinates = [(430, 830),(433,800),(537,179)]  # 替换成你想要点击的坐标
restart_coordinates = [(323, 630),(700,1048),(345,587),(540,154),(347,841)]  # 替换成你想要点击的坐标


cropped_area = (0,27,641,972)
cropped_area_skill1 = (80,495,227,625)
cropped_area_skill2 = (247,495,393,625)
cropped_area_skill3 = (414,495,563,625)
deteact_area = (243,474,407,541)
deteact_area2 = (256,761,393,794)

def capture_window(window_id):
    region = Quartz.CGRectInfinite
    options = Quartz.kCGWindowListOptionIncludingWindow
    image = Quartz.CGWindowListCreateImage(region, options, window_id, Quartz.kCGWindowImageBoundsIgnoreFraming)
    width = Quartz.CGImageGetWidth(image)
    height = Quartz.CGImageGetHeight(image)
    provider = Quartz.CGImageGetDataProvider(image)
    bitmap = Quartz.CGDataProviderCopyData(provider)
    pil_image = Image.frombuffer("RGB", (width, height), bitmap, "raw", "RGBX", 0, 1)
    return pil_image

def get_game_window_id():
    for window_info in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID):
        # print(window_info['kCGWindowOwnerName'])
        if window_info['kCGWindowOwnerName'] == 'XJSKP':
            return window_info['kCGWindowNumber']
    return None

save_path = '/Users/suimulate/Desktop/tmp/capture.png'
save_skill1_path = '/Users/suimulate/Desktop/tmp/skill1.png'
save_skill2_path = '/Users/suimulate/Desktop/tmp/skill2.png'
save_skill3_path = '/Users/suimulate/Desktop/tmp/skill3.png'
save_deteact_path = '/Users/suimulate/Desktop/tmp/game_deteact.png'
save_deteact_path2 = '/Users/suimulate/Desktop/tmp/game_deteact2.png'

safari_window_id = 0
def capture_image(area,path):
    safari_window_id = get_game_window_id()
    if safari_window_id:
        screenshot = capture_window(safari_window_id)
        screenshot = screenshot.convert("RGB")  # 将图像转换为RGB模式

        # 定义裁剪区域 (left, top, right, bottom)
        get_cropped_area = area
        screenshot = screenshot.crop(get_cropped_area)

        screenshot.save(path)
        screenshot.close()
        return 1
    else:
        return 0


# 执行点击动作
def perform_click_actions():
    window_result = capture_image(cropped_area,save_path)
    
    # 使用 OCR 对截图中的文本进行识别
    ocr_text = pytesseract.image_to_string(save_path, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata')

    # # 根据 OCR 结果执行点击动作
    if"非法" in ocr_text or window_result == 0:
        logging.debug('非法检测或窗口无法找到，正在执行重启')
        send_email_a('窗口检测失败！','窗口检测失败！')
        # raise Exception("窗口检测失败！")  # 抛出异常中断函数执行
        time.sleep(80)

        if window_result != 0 :
            logging.debug('关闭非法弹窗')
            pyautogui.click(restart_coordinates[0])
            time.sleep(5)
        else :
            logging.debug('准备打开游戏')
            time.sleep(5)
        logging.debug('点击游戏图标')
        pyautogui.click(restart_coordinates[1])
        time.sleep(10)

        logging.debug('等待插件弹窗...')
        capture_deteact = 0
        while capture_deteact == 0:
            capture_image(deteact_area,save_deteact_path)
            ocr_text_deteact = pytesseract.image_to_string(save_deteact_path, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata')
            if "拉黑" in ocr_text_deteact :
                logging.debug('插件弹窗已打开')
                capture_deteact = 1
            time.sleep(5)

        logging.debug('点击插件弹窗')
        pyautogui.click(restart_coordinates[2])
        time.sleep(5)

        logging.debug('点击公告关闭窗口')
        pyautogui.click(restart_coordinates[3])
        time.sleep(10)
        logging.debug('点击开始按钮')
        pyautogui.click(restart_coordinates[4])
        time.sleep(8)
        capture_image(deteact_area2,save_deteact_path2)
        restart_ocr_text = pytesseract.image_to_string(save_deteact_path2, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata')
        if "开始游戏" in restart_ocr_text:
            logging.debug('重启成功')
        else:
            logging.debug('重启失败')
    elif "完美通关" in ocr_text or "开始游戏" in ocr_text  or "羌美" in ocr_text:
        print('\n------------开始关卡------------')
        logging.info('\n------------开始关卡------------')
        pyautogui.click(start_coordinates[0])
        time.sleep(1.5)
        pyautogui.click(pause_coordinates[0])
        time.sleep(1.5)
        pyautogui.click(hack_coordinates[0])
        time.sleep(1.5)
        pyautogui.click(hack_coordinates[1])
        time.sleep(1.5)
        pyautogui.click(end_coordinates[1])
    elif "当局" in ocr_text:
        # print(datetime.datetime.now())
        capture_image(cropped_area_skill1,save_skill1_path)
        capture_image(cropped_area_skill2,save_skill2_path)
        capture_image(cropped_area_skill3,save_skill3_path)
        ocr_text_skill = []
        ocr_text_skill.append (pytesseract.image_to_string(save_skill1_path, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata') )
        ocr_text_skill.append (pytesseract.image_to_string(save_skill2_path, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata') )
        ocr_text_skill.append (pytesseract.image_to_string(save_skill3_path, config = '-l chi_sim --psm 6--tessdata-dir /opt/homebrew/Cellar/tesseract/5.3.4_1/share/tessdata') )
        # for skill in ocr_text_skill:
        #     skill = skill.strip()
        #     print(skill)

        maxlevel = 0
        all_skill_power = []
        for index, value in enumerate(ocr_text_skill):
            if "释放高能" in value:
                maxlevel = 10
            elif "折射" in value:
                maxlevel = 9
            elif "学习高能" in value or "学习制导" in value or "学习旋风" in value or "学习装甲" in value:
                maxlevel = 8
            elif "范围" in value:
                maxlevel = 6
            elif "释放2个" in value or "连发" in value or "穿透+" in value or "次数+" in value or "分裂" in value or "并向" in value or "穿透" in value or "次级" in value:
                maxlevel = 11
            elif "子弹弹道数量" in value or "射击连发数" in value :
                maxlevel = 12
            elif "出击次数" in value:
                maxlevel = 5
            elif "车" in value:
                maxlevel = 4
            elif "风" in value:
                maxlevel = 3
            elif "线" in value or "激光" in value:
                maxlevel = 2
            elif "燃油" in value:
                maxlevel = 10
            elif "子弹" in value:
                maxlevel = 1
            elif "额外" in value:
                maxlevel = 0.9
            else :
                maxlevel = 0
            all_skill_power.append([maxlevel,index])

        select_index = max(all_skill_power, key=lambda x: x[0])
        # time.sleep(9999)   
        pyautogui.click(select_coordinates[select_index[1]])
        info_string = str(select_index[0]) + '选择技能:' + str(ocr_text_skill[select_index[1]]).strip().replace('\n', '')
        print(info_string)
        logging.info(info_string)
    elif "今日" in ocr_text:
        pyautogui.click(end_coordinates[0])
        print('------------结束关卡------------')
        send_email_a('关卡结束','关卡结束')
        time.sleep(1)
        logging.info('\n------------结束关卡------------\n\n\n')
    elif "空白" in ocr_text:
        pyautogui.click(end_coordinates[0])
        logging.info('boss')
    elif "升级" in ocr_text or "Lv" in ocr_text:
        pyautogui.click(end_coordinates[0])
        time.sleep(1)
        logging.info('升级')
    elif "最长" in ocr_text or "巡逻" in ocr_text:
        pyautogui.click(end_coordinates[1])
        time.sleep(1)
        pyautogui.click(end_coordinates[1])
        time.sleep(1)
        pyautogui.click(end_coordinates[2])
        logging.info('升级')
    # else:
    #     no_spaces_ocr_text = ocr_text.replace(" ", "")
    #     no_newlines_ocr_text = no_spaces_ocr_text.replace("\n", "")
    #     print(no_newlines_ocr_text)


# 主循环
times = 99999
try:
    pyautogui.click(135,41)

    while (times != 0):
        try:
            perform_click_actions()
        except Exception as e:
            logging.error(f"发生异常：{e}")
            break
        times -= 1
        time.sleep(3)
except KeyboardInterrupt:
    print("Stopped monitoring")
