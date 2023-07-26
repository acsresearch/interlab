cd `dirname $0`

TARGET_PATH=../interlab/ui/browser

rm -r ${TARGET_PATH:?}/*
mv build/* ${TARGET_PATH}
git add ${TARGET_PATH}
