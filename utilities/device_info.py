"""Local network identity and device information; no external IP lookup."""
import json
import os
import platform
import subprocess
from datetime import datetime

from utilities.error_messages import error_message
from PySide6.QtNetwork import QNetworkInterface, QAbstractSocket


def network_interfaces():
    result = []
    for interface in QNetworkInterface.allInterfaces():
        flags = interface.flags()
        if not flags & QNetworkInterface.IsUp:
            continue
        ipv4, ipv6 = [], []
        for entry in interface.addressEntries():
            ip = entry.ip()
            if ip.isLoopback():
                continue
            if ip.protocol() == QAbstractSocket.IPv4Protocol:
                ipv4.append(ip.toString())
            elif ip.protocol() == QAbstractSocket.IPv6Protocol:
                ipv6.append(ip.toString())
        if ipv4 or ipv6:
            result.append({'name': interface.humanReadableName(), 'ipv4': ipv4,
                           'ipv6': ipv6, 'mac': interface.hardwareAddress()})
    return result


def local_ipv4_addresses():
    return sorted({ip for interface in network_interfaces() for ip in interface['ipv4']})


def cpu_name():
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
                return winreg.QueryValueEx(key, 'ProcessorNameString')[0].strip()
        except OSError:
            pass
    return platform.processor() or platform.machine()


def gpu_report():
    lines = []
    if os.name == 'nt':
        try:
            result = subprocess.run(
                ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
                 '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
                 'ConvertTo-Json -Compress -InputObject @(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name)'],
                capture_output=True, text=True, encoding='utf-8-sig', errors='replace',
                timeout=15, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
            names = json.loads(result.stdout)
            lines.append('GPU: ' + (', '.join(names) or 'No adapter reported'))
        except (OSError, ValueError, subprocess.SubprocessError):
            lines.append('GPU: OS adapter information unavailable')
    try:
        import torch
        available = torch.cuda.is_available()
        lines.append(f'PyTorch {torch.__version__} — CUDA GPU acceleration: {"available" if available else "unavailable"}')
        if available:
            for i in range(torch.cuda.device_count()):
                lines.append(f'  CUDA {i}: {torch.cuda.get_device_name(i)}')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            lines.append('PyTorch MPS GPU acceleration: available')
        else:
            lines.append('PyTorch will use CPU; no supported GPU acceleration is available.')
    except ImportError:
        lines.append('PyTorch is not installed; GPU acceleration could not be checked.')
    except Exception as error:
        lines.append(f'PyTorch GPU check failed: {error_message(error)}')
    return lines


def device_report():
    lines = [f'Current date: {datetime.now().astimezone().isoformat(timespec="seconds")}',
             f'CPU: {cpu_name()} ({os.cpu_count() or "unknown"} logical processors)']
    lines.extend(gpu_report())
    interfaces = network_interfaces()
    if not interfaces:
        lines.extend(['IPv4: unavailable', 'IPv6: unavailable', 'MAC: unavailable'])
    for interface in interfaces:
        lines.extend([f'Network: {interface["name"]}',
                      '  IPv4: ' + (', '.join(interface['ipv4']) or 'unavailable'),
                      '  IPv6: ' + (', '.join(interface['ipv6']) or 'unavailable'),
                      '  MAC: ' + (interface['mac'] or 'unavailable')])
    numbered = ['']
    number = 0
    for line in lines:
        if line.startswith('  '):
            numbered.append('        ' + line.strip())
        else:
            number += 1
            numbered.append(f'{number}. {line}')
    return '\n'.join(numbered)
