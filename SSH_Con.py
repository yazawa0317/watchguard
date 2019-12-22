import paramiko
import time
import pprint
import re
import datetime

class wg_mgt():

    def __init__(self,ipaddr,usr,pwd):
 
        self.host = ipaddr
        self.user = usr
        self.passwd = pwd
        self.port = 4118
#        self.logdir = "C:\\FTP\\logs"
#        self.logfile = self.host + "_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_logs.txt"
#        self.logpath = os.path.join(self.logdir,self.logfile)

    def wg_connect(self):
        self.res = ''
        self.con = paramiko.SSHClient()
        self.con.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.con.connect(self.host, self.port, self.user, self.passwd)

        self.session_ = self.con.invoke_shell()
        self.res += self.session_.recv(9999).decode()
        return self.res

    def wg_show(self, cmds):   
        self.res = ''
        for cmd in cmds:
            self.session_.send(cmd+'\n')
            time.sleep(5)
            if (self.session_.recv_ready()):
                self.res += self.session_.recv(9999).decode()                
            else:
                raise Exception
        return self.res

    def wg_configure(self, cmds, policy = False):
        self.res = ''
        result = 'configure commands-----------\n'
        self.session_.send('configure\n')
        time.sleep(3)
        self.res += self.session_.recv(9999).decode()

        if policy is True:        
            self.session_.send('policy\n')
            time.sleep(3)
            self.res += self.session_.recv(9999).decode()

        for cmd in cmds:
            result += 'Execute Command---->' + cmd + '\n'
            self.session_.send(cmd+'\n')
            time.sleep(3)
            if (self.session_.recv_ready()):
                self.res += self.session_.recv(9999).decode()
                          
            else:
                raise Exception

        if policy is True:        
            self.session_.send('apply\n')
            time.sleep(3)
            self.res += self.session_.recv(9999).decode()
            print(self.res)
        for v in range(3):

            self.session_.send('exit\n')           
            self.res += self.session_.recv(9999).decode()

            if 'WG#' in str(self.res[:-1]):
                break 

        return result

    def wg_disconnect(self):
        self.res = ''
        for v in range(3):
            try:
                self.session_.send('exit\n')
                self.res += self.session_.recv(9999).decode()
            except:
                break
            
        self.con.close()

        return self.res

if __name__ == '__main__':

    cur_entrise_with_number = {}
    cur_entrise = []
    cn = wg_mgt('10.1.50.254', 'auto', 'auto1234')
    cn.wg_connect()

    cmds= ['show alias test-alias']
    res = cn.wg_show(cmds).replace(' ', '').split('\n')
    for row in res:
        pat = '.(\d+).*{(.*)}.*$'
        entry = re.match(pat, row)
        if entry is None:
            continue
        cur_entrise_with_number[entry[2]] = entry[1]
        cur_entrise.append(entry[2])

    with open(r'c:\python\myCode\WatchGuard\list') as f:
        new_entrise = []
        tmp_entrise_dict = {}
        for row in f:
            entry = row.split(',')
            new_entrise.append(entry[1].replace(' ','').strip('\n'))
            tmp_entrise_dict[entry[1].strip('\n')] = entry[0].strip('\n')

    #    print(tmp_entrise_dict)
    del_entrise = set(cur_entrise) - set(new_entrise)

    del_cmds = []
    result = 'Delete-Entry---------\n'
    for entry in list(del_entrise):
        result += entry + '\n'
        entry_number = cur_entrise_with_number[entry]
        del_cmds.append("no alias test-alias position {}".format(entry_number))
#    print(del_cmds)

    add_entrise = set(new_entrise) - set(cur_entrise)
    add_cmds = []
    result += 'Add-Entry------------\n'
    for entry in list(add_entrise):
        result += entry + '\n'
        if re.match('\d+\.\d+\.\d+\.\d+', entry):
            add_cmds.append("alias test-alias {} {}".format(tmp_entrise_dict[entry],entry))  
        else:  
            add_cmds.append("alias test-alias {} '{}'".format(tmp_entrise_dict[entry],entry))
#    print(add_cmds)


#    bk_cmds = ['export config to tftp://192.168.113.2/configuration_{}.xml'.format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")),]
#    res = cn.wg_show(bk_cmds)
    chg_cmds = del_cmds + add_cmds
    res = cn.wg_configure(chg_cmds, policy=True)
    print(result + res )

    res = cn.wg_disconnect()


