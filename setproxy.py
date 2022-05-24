#!/usr/bin/env python3

import subprocess
import sys
import argparse
import os


ASSETS = '{}/assets/'.format(os.path.split(os.path.abspath(sys.argv[0]))[0]) # assets directory path 
DATA_DIR = '/data/local/tmp/'


# return : (ret_code, normal, error) or (None, None, None)
def exec_cmd(cmdline, cwd=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    '''
    Wrapped system command line execution method
    '''
    # print(cmdline)
    try:
        subp = subprocess.Popen(cmdline, shell=True, stdout=stdout, stderr=stderr, cwd=cwd)
    except Exception as e:
        return None, None, None
    out, err = subp.communicate()
    normal = None
    error = None
    if out:
        normal = out.decode(errors='ignore')
    if err:
        error = err.decode(errors='ignore')
    return subp.returncode, normal, error


def adb_shell(cmdline):
    '''
    Wrapped adb command line execution method
    '''
    print(cmdline)
    rc, normal, error = exec_cmd('adb shell {}'.format(cmdline))
    if normal is None:
        return ''
    else:
        # print(normal)
        return normal
        # .replace('\r\n', '\n')


def push_file(file_name):
    '''
    upload files to Android "/data/local/tmp/" directory. Give it executable permissions
    '''
    exist = not bool(int(adb_shell("'[ -a {}/{} ];echo -n $?'".format(DATA_DIR, file_name))))
    if not exist:
        print('push ' + file_name)
        exec_cmd('adb push {}/{} {}/{}'.format(ASSETS, file_name, DATA_DIR, file_name))
    else:
        print('Warning: The file is existed in devices!, {} not pushed\n'.format(file_name))

    adb_shell('chmod 755 {}/{}'.format(DATA_DIR, file_name))

def adb_root_shell(cmdline):
    uid = adb_shell('id -u').strip()
    if uid == '0':
        adb_shell(cmdline)
    else:
        uid = adb_shell("\"su -c 'id -u'\"").strip()
        if uid == '0':
            adb_shell("\"su -c '{}'\"".format(cmdline))
        else:
            print('Device is not rooted')
            exit(-1)

def set_proxy(uid, proxy_ip, port=8080):
    '''
    Configuring redsocks proxy
    '''


    push_file('iptables.sh')
    push_file('proxy.sh')
    push_file('redsocks')

    adb_root_shell("{}proxy.sh {} start http {} {} false foo bar".format(DATA_DIR, DATA_DIR, proxy_ip, port))
    adb_root_shell("{}/iptables.sh {} {}".format(DATA_DIR, proxy_ip, uid))


def unset_proxy():
    '''
    release redsocks proxy
    '''
    print('unset proxy')
    push_file('iptables.sh')
    push_file('proxy.sh')
    push_file('redsocks')

    adb_shell('{}proxy.sh {} stop'.format(DATA_DIR, DATA_DIR))
    # 需要执行第两遍
    adb_shell('{}proxy.sh {} stop'.format(DATA_DIR, DATA_DIR))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='set proxy')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--proxy', help='proxy address. ip:port or ip, 8080 is default port')
    group.add_argument('-u', '--unset', action='store_true', help='unset proxy')
    parser.add_argument('target', nargs='?', help="package name or uid")

    args = parser.parse_args()

    if args.unset:
        unset_proxy()
        exit(0)

    if ':' in args.proxy:
        s_proxy = args.proxy.split(':')
        proxy_ip = s_proxy[0]
        proxy_port = s_proxy[1]
    else:
        proxy_ip = args.proxy
        proxy_port = 8080
    
    if args.target is None:
        print('Error: target is None')
        exit(-1)

    target = args.target

    if target.isdigit():
        uid = target
    else:
        uid = adb_shell('pm list package -U {} | grep "package:{} uid:" |cut -d ":" -f 3'.format(target, target))
        if uid is None or uid == '':
            print('Error: not found {}'.format(target))
            exit(-1)
        uid = uid.strip()

    print('set {}:{} proxy to {}:{}'.format(target, uid, proxy_ip, proxy_port))
    set_proxy(uid, proxy_ip, proxy_port)
