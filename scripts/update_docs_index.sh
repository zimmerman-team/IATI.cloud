#!/bin/bash

# Import utility functions
source ./scripts/util.sh

cat README.md ./docs/*.md > ./docs/combined.md
pandoc -s --metadata title="IATI.cloud Documentation" -o ./docs/index.html ./docs/combined.md
rm ./docs/combined.md

# Google tag content to be inserted inside <head>
HEAD_CONTENT='<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CP65J0T1G0"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag("js", new Date());
gtag("config", "G-CP65J0T1G0");
</script>'

# Insert the Google tag content inside the <head> tag of docs/index.html
sed -i '/<head>/r /dev/stdin' ./docs/index.html <<< "$HEAD_CONTENT"

# Replace "<img src="./docs/images/aida-artboard1.png" with "<img src="./images/aida-artboard1.png" in docs/index.html
sed -i 's#<img src="./docs/images/#<img src="./images/#g' ./docs/index.html

print_status "Done updating docs/index.html from README.md and docs/*.md. Make sure to push the updated index to GitHub, to the branch in use under settings/pages."