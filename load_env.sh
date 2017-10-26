#!/usr/bin/env bash

echo "$(eval "echo \"$(cat script/local.env)\"")" > script/local-compiled.env
tmpfile=$(mktemp /tmp/actual-env.XXXXXX.sh)
echo "#default.env" > $tmpfile
sed -E -n 's/[^#]+/export &/ p' ./script/default.env >> $tmpfile
echo "" >> $tmpfile
echo "#local-compiled.env" >> $tmpfile
sed -E -n 's/[^#]+/export &/ p' ./script/local-compiled.env >> $tmpfile
source $tmpfile
cat  $tmpfile | grep -v PASS
rm -rf  $tmpfile
if [ "$(echo $PATH | sed 's/:/\n/g' | grep /usr/local/bin | wc -l)" == "0" ]; then
    export PATH=$PATH:/usr/local/bin
fi
