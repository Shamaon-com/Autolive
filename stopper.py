import subprocess
import re, sys

def executePorcess(process):
    process = subprocess.Popen(process.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return str(output)

key = sys.argv[1]

at = "atq"
output = executePorcess(at)
if output != 'b\'\'':
    for item in output.split('/n'):
        jobid = re.findall('\d+', item)[0]
        print(jobid)
        at = "at -c {jobid}".format(jobid=jobid)
        output = executePorcess(at)
        keyex = re.findall(r"(?<=--key )([^\s]+)", output)[0].split('\\')[0]
        try:
            if key == keyex:
                sys.exit()
        except Exception as e:
            print(e)
            pass
p1 = "echo autolive --action Delete --key {key}".format(key=key)
execp1 = subprocess.Popen(p1.split(), stdout=subprocess.PIPE)
excep2 = subprocess.Popen("at now + 10 minutes".split(), stdin=execp1.stdout)