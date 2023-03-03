import wmi

def changeDNS():
    wmiService = wmi.WMI()
    colNicConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)

    # 检测适配器是否可用
    if len(colNicConfigs) < 1:
        print('[!!!]Error: 没有可用的网络适配器')
        exit()

    objNicConfig = colNicConfigs[0]
    arrDNSServers = ['114.114.114.114']
    returnValue = objNicConfig.SetDNSServerSearchOrder(DNSServerSearchOrder=arrDNSServers)

    if returnValue[0] == 0:
        print('[Successfully!!!]')
    else:
        print('[Error,Failled!!!]')

changeDNS()