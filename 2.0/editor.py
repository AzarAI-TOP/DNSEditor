# -*- coding : utf-8 -*-
# @author : Azar

import os
import sys
import wmi
import re
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QInputDialog,QListWidget

IP_Pattern = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

def get_dnslist() -> list[str]:
    # 从文件中读取DNS列表
    l = []
    with open('dns_list', 'r')as file:
        for line in file:
            l.append(line[:-1] if line.endswith('\n') else line)
    return l

def isIP(text:str) -> bool:
    # 使用正则表达式检测IP格式
    if re.match(IP_Pattern,text):
        return True
    else:
        return False

class Window(QWidget):
    def __init__(self) -> None:
        super(Window, self).__init__(None)
        uic.loadUi('ui.ui', self)

        # 获取 设置实例 以及初始DNS、当前选定DNS、以及文件中的DNS列表
        self.config = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)[0]
        
        self.pre_dns = self.get_dnsServers()
        # 检测DNSServer的数量
        if len(self.pre_dns) == 1:
            self.pre_dns = (self.pre_dns[0],self.pre_dns[0])
        print('初始DNS列表：',self.pre_dns)
        
        self.cur_dns = list(self.pre_dns)
        self.dns_list = get_dnslist()


        # self.dns_widget = QListWidget()

        # 标签显示电脑配置信息
        self.dns_adapter.setText(self.get_adapterName())
        self.dns_main.setText(self.pre_dns[0])
        self.dns_second.setText(self.pre_dns[1] if len(self.pre_dns)==1 else self.pre_dns[0])

        # 显示DNS列表
        self.dns_widget.addItems(self.dns_list)

        # 绑定按键事件
        self.btn_add.clicked.connect(self.list_add)
        self.btn_del.clicked.connect(self.list_del)
        self.btn_back.clicked.connect(self.back)
        self.btn_main.clicked.connect(self.set_main)
        self.btn_second.clicked.connect(self.set_second)

        # self.dns_widget = QListWidget()

    def set_main(self):
        item = self.dns_widget.selectedItems()[0].text()
        self.cur_dns[0] = item
        self.set_dnsServers(self.cur_dns)
        self.dns_main.setText(item)

    def set_second(self):
        item = self.dns_widget.selectedItems()[0].text()
        self.cur_dns[1] = item
        self.set_dnsServers(self.cur_dns)
        self.dns_second.setText(item)
    
    def list_add(self):
        # 添加IP列表
        ip, flag = QInputDialog.getText(self, '请输入DNS服务器地址', 'IP:')
        if flag and isIP(ip):
            print('检测到合格的IP地址', ip)
            self.dns_list.append(ip)
            self.dns_widget.addItem(ip)

    def list_del(self):
        item = self.dns_widget.selectedItems()[0].text()
        self.dns_list.remove(item)
        self.dns_widget.takeItem(self.dns_widget.currentRow())

    def back(self):
        # 恢复DNS设置初始状态
        self.dns_main.setText(self.pre_dns[0])
        self.dns_second.setText(self.pre_dns[1])
        self.set_dnsServers(self.pre_dns)

        # 恢复DNS列表文件初始状态
        with open('dns_list', 'w') as file1:
            with open('dns_list_base', 'r') as file2:
                file1.write(file2.read())
        self.dns_list = get_dnslist()

        # 更新列表控件
        self.dns_widget.clear()
        self.dns_widget.addItems(self.dns_list)

    def get_adapterName(self) -> str:
        # 获取默认适配器
        return self.config.Description

    def get_dnsServers(self) -> tuple[str]:
        # 获取当前DNS服务器IP地址
        return self.config.DNSServerSearchOrder

    def set_dnsServers(self,dns:list[str]) -> bool:
        print('更改DNS：', dns)
        flag = True
        r = self.config.SetDNSServerSearchOrder(DNSServerSearchOrder=dns)
        if r[0] == 0:
            print('成功设置DNS')
        elif r[0] == 1:
            print('成功设置DNS')
            self.show_rebootBox()
        else:
            print('设置DNS失败')
            flag = False
        return flag

    def show_rebootBox(self):
        # 显示重启对话框
        # QMessageBox.information(self,'设置完成', "DNS设置完成，需重启")
        box = QMessageBox(self)
        box.setWindowTitle('成功')
        box.setText('DNS设置完毕，需要重启电脑，是否立即重启？')
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        reboot = box.button(QMessageBox.StandardButton.Yes)
        reboot.setText('重启')

        later = box.button(QMessageBox.StandardButton.No)
        later.setText('稍后')

        box.exec_()
        if box.clickedButton() == reboot:
            print('重启')
            self.save()
            os.system('shutdown /r')

    def save(self):
        with open('dns_list', 'w') as file:
            file.write('\n'.join(self.dns_list))
        print('文件保存完毕')

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.save()
        print('程序退出，文件已保存')
        app.quit()
        


            

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wmiService = wmi.WMI()

    myWindow = Window()
    myWindow.show()

    app.exec_()