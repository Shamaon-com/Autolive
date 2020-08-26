

DIR="rtmp://localhost/live/${1}"

OUTPUT=$(ffprobe -v quiet -print_format json -show_format -show_streams "$DIR")

autolive --action Create --key ${1} --data "$OUTPUT" --debug true > /home/ubuntu/${1}.log 