import subprocess, sys, re

key = sys.argv[0]

at = "atq"
output = executePorcess(at)

for item in output.split('/n'):
    at = "at -c {jobid}".format(jobid=item[2])
    output = executePorcess(at)
    #print(re.findall(r"(?<=--key ).*$", str(output))[0].split('\\')[0])
    if key == re.findall(r"(?<=--key ).*$", output)[0].split('\\')[0]:
        executePorcess("atrm {jobid}".format(jobid=item[2]) )

rtmp = "rtmp://localhost/pool/{key}".format(key=key)
ffprobe = "ffprobe -v quiet -print_format json -show_format -show_streams {rtmp}".format(rtmp=rtmp)
ffporbeOutput = executePorcess(ffprobe)
autolive = "--action Create --key {key} --data {data} --debug true > /home/ubuntu/{key}.log".format(key=key, data=ffporbeOutput)
executePorcess(autolive)

def executePorcess(process):
    process = subprocess.Popen(process.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return str(output)